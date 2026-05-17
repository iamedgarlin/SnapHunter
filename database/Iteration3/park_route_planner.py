"""
Route planning logic for SnapHunter preset park routes.

Routes are generated from the internal OSM walking graph. Task clusters are
attached after route generation for scoring.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Any

import geopandas as gpd
import networkx as nx
import pandas as pd
from shapely.geometry import LineString, Point

from park_route_data import (
    build_task_clusters_for_park,
    stringify,
)


wgs84_crs = "EPSG:4326"
projected_crs = "EPSG:7855"
walking_speed_m_per_sec = 54 / 60
node_rounding_m = 1.0

# Candidate generation limits.
boundary_gate_max_distance_m = 35
virtual_boundary_node_max_distance_m = 30
max_start_nodes = 10
max_simple_paths_per_pair = 30
max_loop_paths_per_gate = 80

# Shape and overlap filters.
min_route_distance_m = 250
min_loop_distance_m = 300
max_overlap_ratio = 0.25
max_overlap_m = 180
max_backtrack_ratio = 0.2
max_selected_edge_jaccard = 0.72

# Nearby task clusters affect score and final difficulty.
dead_end_task_context_distance_m = 500
task_score_full_distance_m = 30
task_score_max_distance_m = 50
task_score_points_per_cluster = 6
max_task_score = 30
task_difficulty_promote_score = 24
task_difficulty_demote_score = 6

min_distance_fit_for_selection = 1.00


@dataclass(frozen=True)
class DifficultySpec:
    name: str
    distance_min: float
    distance_max: float


difficulty_specs = [
    DifficultySpec("Easy", 250, 600),
    DifficultySpec("Medium", 600, 850),
    DifficultySpec("Adventure", 850, 1200),
]


class CRSHelper:
    def __init__(self) -> None:
        from pyproj import Transformer

        self.to_wgs84 = Transformer.from_crs(projected_crs, wgs84_crs, always_xy=True)
        self.to_projected = Transformer.from_crs(wgs84_crs, projected_crs, always_xy=True)

    def project_point(self, point: Point) -> Point:
        x, y = self.to_projected.transform(point.x, point.y)
        return Point(x, y)

    def unproject_line(self, line: LineString) -> LineString:
        return LineString([self.to_wgs84.transform(x, y) for x, y in line.coords])

# Main functions for building routes for parks, including graph construction, candidate generation, and scoring.
def build_routes_for_parks(
    parks: Any,
    roads: Any,
    entrances: Any,
    tasks: Any,
) -> Any:
    rows = []
    for index, park in parks.iterrows():
        park_id = int(park["park_id"])
        park_name = str(park["park_name"])
        print(f"[{index + 1}/{len(parks)}] Generating preset routes: {park_name}")

        park_roads = get_internal_roads_for_park(roads, park)
        print(f"  internal roads: {len(park_roads)}")
        if park_roads.empty:
            print("  warning: skipped, no internal roads")
            continue

        # Convert the park's internal OSM paths into a walkable graph.
        graph_data = build_park_graph(park_roads)
        if graph_data is None:
            print("  warning: skipped, could not build graph")
            continue
        graph, node_points, transformer = graph_data

        # Task clusters are attached after route generation for scoring/output.
        task_clusters = build_task_clusters_for_park(park, tasks)
        print(f"  task clusters for scoring: {len(task_clusters)}")
        # Prefer real OSM entrances; fall back to road nodes near the boundary.
        starts = build_start_candidates(park, entrances, graph, node_points, transformer)
        if not starts:
            print("  warning: skipped, no gate or virtual boundary node")
            continue
        print(f"  start/end candidates: {len(starts)} ({candidate_source_summary(starts)})")

        candidates = generate_route_candidates(graph, node_points, transformer, task_clusters, starts)
        print(f"  route candidates after filters: {len(candidates)}")
        if not candidates:
            print("  warning: no usable road-network route candidates")
            continue

        selected = select_best_routes(candidates)
        if not selected:
            print("  warning: no difficulty route selected")
            continue

        for route in selected:
            rows.append(build_route_row(park, route))
            print(
                f"  {route['difficulty']} (base={route['base_difficulty']}): {route['distance_m']:.0f}m, "
                f"{route['walking_time_sec']}sec, "
                f"backtrack={route['backtrack_ratio']:.3f}, "
                f"nearby_task_clusters={route['nearby_task_cluster_count']}, "
                f"score={route['route_score']:.1f}"
            )

    return gpd.GeoDataFrame(rows, geometry="geometry", crs=wgs84_crs)

# Load internal OSM roads for a park, which are used for route generation.
def get_internal_roads_for_park(roads: Any, park: Any) -> Any:
    park_id = int(park["park_id"])
    return roads[
        pd.to_numeric(roads.get("park_id"), errors="coerce") == park_id
    ].copy()


def build_park_graph(park_roads: Any) -> tuple[Any, dict[Any, Point], CRSHelper] | None:
    projected = park_roads.to_crs(projected_crs)
    graph = nx.Graph()
    node_points: dict[Any, Point] = {}

    # Each path segment becomes an edge. Rounding avoids near-duplicate nodes.
    for _, row in projected.iterrows():
        for line in iter_lines(row.geometry):
            coords = list(line.coords)
            for coord_a, coord_b in zip(coords, coords[1:]):
                node_a = node_key(coord_a)
                node_b = node_key(coord_b)
                if node_a == node_b:
                    continue
                point_a = Point(node_a)
                point_b = Point(node_b)
                length = point_a.distance(point_b)
                if length <= 0:
                    continue
                node_points[node_a] = point_a
                node_points[node_b] = point_b
                if graph.has_edge(node_a, node_b):
                    graph[node_a][node_b]["weight"] = min(graph[node_a][node_b]["weight"], length)
                else:
                    graph.add_edge(node_a, node_b, weight=length)

    if graph.number_of_nodes() == 0:
        return None

    # Keep one connected walking network so shortest paths are actually valid.
    largest = max(nx.connected_components(graph), key=len)
    graph = graph.subgraph(largest).copy()
    node_points = {node: node_points[node] for node in graph.nodes}
    return graph, node_points, CRSHelper()


def iter_lines(geometry: Any) -> list[Any]:
    if geometry is None or geometry.is_empty:
        return []
    if geometry.geom_type == "LineString":
        return [geometry]
    if geometry.geom_type == "MultiLineString":
        return list(geometry.geoms)
    return []


def node_key(coord: tuple[float, float]) -> tuple[float, float]:
    return (
        round(float(coord[0]) / node_rounding_m) * node_rounding_m,
        round(float(coord[1]) / node_rounding_m) * node_rounding_m,
    )

# Load gate/entrance points for candidate route start locations.
def build_start_candidates(
    park: Any,
    entrances: Any,
    graph: Any,
    node_points: dict[Any, Point],
    transformer: CRSHelper,
) -> list[dict[str, Any]]:
    park_id = int(park["park_id"])
    nodes = list(graph.nodes)
    points = [node_points[node] for node in nodes]
    candidates = []

    if not entrances.empty and "park_id" in entrances.columns:
        park_entrances = entrances[pd.to_numeric(entrances["park_id"], errors="coerce") == park_id].copy()
        if not park_entrances.empty and "distance_to_boundary_m" in park_entrances.columns:
            park_entrances = park_entrances[
                pd.to_numeric(park_entrances["distance_to_boundary_m"], errors="coerce") <= boundary_gate_max_distance_m
            ].copy()
        for _, entrance in park_entrances.iterrows():
            candidates.append(nearest_gate_candidate(entrance, nodes, points, transformer))

    candidates = dedupe_candidates(candidates)
    if candidates:
        return candidates[:max_start_nodes]

    return build_virtual_boundary_candidates(park, graph, node_points)[:max_start_nodes]

# Find the nearest graph node to the entrance point for candidate generation. 
def nearest_gate_candidate(
    entrance: Any,
    nodes: list[Any],
    node_points: list[Point],
    transformer: CRSHelper,
) -> dict[str, Any]:
    projected = transformer.project_point(entrance.geometry)
    best_idx, best_point = min(enumerate(node_points), key=lambda item: projected.distance(item[1]))
    gate_name = entrance.get("name") or entrance.get("entrance") or entrance.get("barrier") or entrance.get("osm_id")
    return {
        "source": "gate",
        "source_id": entrance.get("osm_id"),
        "name": stringify(gate_name) or "OSM gate/entrance",
        "node": nodes[best_idx],
        "distance_to_node_m": round(projected.distance(best_point), 1),
    }

# If not enough real gates/entrances, add virtual candidates along the park boundary 
# which are close to boundary and well connected in the path graph. 
def build_virtual_boundary_candidates(park: Any, graph: Any, node_points: dict[Any, Point]) -> list[dict[str, Any]]:
    boundary = gpd.GeoSeries([park.geometry], crs=wgs84_crs).to_crs(projected_crs).iloc[0].boundary
    rows = []
    for node, point in node_points.items():
        distance = point.distance(boundary)
        if distance <= virtual_boundary_node_max_distance_m:
            rows.append({
                "source": "virtual_boundary_node",
                "source_id": f"virtual_{int(park['park_id'])}_{len(rows) + 1}",
                "name": "Virtual boundary node",
                "node": node,
                "distance_to_node_m": 0.0,
                "distance_to_boundary_m": round(distance, 1),
            })
    rows = sorted(rows, key=lambda item: (item["distance_to_boundary_m"], -graph.degree[item["node"]]))
    return spread_out_candidates(rows, node_points, max_start_nodes)


def spread_out_candidates(candidates: list[dict[str, Any]], node_points: dict[Any, Point], limit: int) -> list[dict[str, Any]]:
    selected = []
    for candidate in candidates:
        point = node_points[candidate["node"]]
        if all(point.distance(node_points[other["node"]]) >= 80 for other in selected):
            selected.append(candidate)
        if len(selected) >= limit:
            break
    if selected:
        return selected
    return candidates[:limit]


def dedupe_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    unique = {}
    for candidate in candidates:
        existing = unique.get(candidate["node"])
        if existing is None or candidate["distance_to_node_m"] < existing["distance_to_node_m"]:
            unique[candidate["node"]] = candidate
    return sorted(unique.values(), key=lambda item: item["distance_to_node_m"])


def candidate_source_summary(candidates: list[dict[str, Any]]) -> str:
    counts = pd.Series([candidate["source"] for candidate in candidates]).value_counts()
    return ", ".join(f"{source}={count}" for source, count in counts.items())

# Generate candidate routes from the graph, then attach nearby task clusters for scoring.
def generate_route_candidates(
    graph: Any,
    node_points: dict[Any, Point],
    transformer: CRSHelper,
    task_clusters: list[dict[str, Any]],
    starts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    candidates = []
    # Candidate routes come only from graph paths, don't directly connect tasks.
    if len(starts) >= 2:
        for start, end in itertools.combinations(starts, 2):
            candidates.extend(generate_entrance_to_entrance_candidates(
                graph, node_points, transformer, task_clusters, start, end
            ))
    for start in starts:
        candidates.extend(generate_loop_candidates(graph, node_points, transformer, task_clusters, start))
    return candidates

# Choose two gates/entrances as start/end candidates, prepare for entrance and leave from different gates
def generate_entrance_to_entrance_candidates(
    graph: Any,
    node_points: dict[Any, Point],
    transformer: CRSHelper,
    task_clusters: list[dict[str, Any]],
    start: dict[str, Any],
    end: dict[str, Any],
) -> list[dict[str, Any]]:
    if start["node"] == end["node"]:
        return []
    try:
        simple_paths = nx.shortest_simple_paths(graph, start["node"], end["node"], weight="weight")
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return []

    rows = []
    for path_nodes in iter_shortest_simple_paths(simple_paths, max_simple_paths_per_pair):
        route = build_candidate_from_path(
            graph, node_points, transformer, task_clusters, path_nodes, start, end, "entrance_to_entrance"
        )
        if route is not None:
            rows.append(route)
    return rows

# If not enough gates allow for one gate loops.
def generate_loop_candidates(
    graph: Any,
    node_points: dict[Any, Point],
    transformer: CRSHelper,
    task_clusters: list[dict[str, Any]],
    start: dict[str, Any],
) -> list[dict[str, Any]]:
    start_node = start["node"]
    neighbors = list(graph.neighbors(start_node))
    if len(neighbors) < 2:
        return []

    rows = []
    graph_without_start = graph.copy()
    graph_without_start.remove_node(start_node)
    for first, second in itertools.combinations(neighbors, 2):
        try:
            paths = nx.shortest_simple_paths(graph_without_start, first, second, weight="weight")
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            continue
        for middle in iter_shortest_simple_paths(paths, max_loop_paths_per_gate):
            path_nodes = [start_node] + middle + [start_node]
            if path_weight_allowing_cycle(graph, path_nodes) < min_loop_distance_m:
                continue
            route = build_candidate_from_path(
                graph, node_points, transformer, task_clusters, path_nodes, start, start, "loop"
            )
            if route is not None:
                rows.append(route)
    return rows


def iter_shortest_simple_paths(paths: Any, limit: int) -> list[list[Any]]:
    rows = []
    while len(rows) < limit:
        try:
            rows.append(next(paths))
        except StopIteration:
            break
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            break
    return rows


def build_candidate_from_path(
    graph: Any,
    node_points: dict[Any, Point],
    transformer: CRSHelper,
    task_clusters: list[dict[str, Any]],
    path_nodes: list[Any],
    start: dict[str, Any],
    end: dict[str, Any],
    candidate_type: str,
) -> dict[str, Any] | None:
    distance_m = path_weight_allowing_cycle(graph, path_nodes)
    if distance_m < min_route_distance_m:
        return None

    # Reject routes that reuse too much geometry or walk back over the same edge.
    overlap = route_overlap_metrics(graph, path_nodes)
    if overlap["overlap_ratio"] > max_overlap_ratio or overlap["overlap_m"] > max_overlap_m:
        return None
    backtrack = route_backtrack_metrics(graph, path_nodes)
    if backtrack["has_bad_immediate_reverse"] or backtrack["backtrack_ratio"] > max_backtrack_ratio:
        return None

    projected_line = LineString([node_points[node].coords[0] for node in path_nodes])
    if projected_line.is_empty or projected_line.length <= 0:
        return None
    if not projected_line.is_simple and overlap["overlap_ratio"] > 0:
        return None

    # Dead-end branches are only kept when they have nearby task context.
    context_task_clusters = clusters_near_route(
        projected_line,
        task_clusters,
        dead_end_task_context_distance_m,
    )
    if route_uses_dead_end_branch(graph, path_nodes) and not context_task_clusters:
        return None
    # Nearby task clusters add score and SQL route_task rows, not waypoints.
    scored_task_clusters = score_task_clusters_near_route(projected_line, task_clusters)
    task_score_units = sum(cluster["route_score_weight"] for cluster in scored_task_clusters)
    route_task_rows = build_route_task_rows_from_clusters(projected_line, scored_task_clusters)

    return {
        "candidate_type": candidate_type,
        "start": start,
        "end": end,
        "geometry": transformer.unproject_line(projected_line),
        "projected_geometry": projected_line,
        "path_nodes": path_nodes,
        "edge_set": route_edge_set(path_nodes),
        "distance_m": round(distance_m, 1),
        "walking_time_sec": int(round(distance_m / walking_speed_m_per_sec)),
        "nearby_task_cluster_count": len(scored_task_clusters),
        "nearby_task_count": sum(cluster["task_count"] for cluster in scored_task_clusters),
        "nearby_task_cluster_ids": [cluster["cluster_id"] for cluster in scored_task_clusters],
        "nearby_task_cluster_details": task_cluster_details(scored_task_clusters),
        "route_task_rows": route_task_rows,
        "task_cluster_score_units": round(task_score_units, 3),
        "path_node_count": len(path_nodes),
        "has_repeated_nodes": len(path_nodes) != len(set(path_nodes)),
        "overlap_m": overlap["overlap_m"],
        "overlap_ratio": overlap["overlap_ratio"],
        "backtrack_m": backtrack["backtrack_m"],
        "backtrack_ratio": backtrack["backtrack_ratio"],
    }


def path_weight_allowing_cycle(graph: Any, path_nodes: list[Any]) -> float:
    return sum(graph[a][b]["weight"] for a, b in zip(path_nodes, path_nodes[1:]))

# Prevent those edge candidates which are too similar.
def route_overlap_metrics(graph: Any, path_nodes: list[Any]) -> dict[str, float]:
    seen = set()
    overlap_m = 0.0
    total_m = 0.0
    for node_a, node_b in zip(path_nodes, path_nodes[1:]):
        edge = tuple(sorted((node_a, node_b)))
        length = graph[node_a][node_b]["weight"]
        total_m += length
        if edge in seen:
            overlap_m += length
        else:
            seen.add(edge)
    return {
        "overlap_m": round(overlap_m, 1),
        "overlap_ratio": round(overlap_m / total_m, 4) if total_m else 0.0,
    }

# Prevent routes that go back and forth over the same edge.
def route_backtrack_metrics(graph: Any, path_nodes: list[Any]) -> dict[str, Any]:
    directed_counts = {}
    edge_lengths = {}
    has_bad_immediate_reverse = False
    total_m = 0.0

    for node_a, node_b in zip(path_nodes, path_nodes[1:]):
        directed_counts[(node_a, node_b)] = directed_counts.get((node_a, node_b), 0) + 1
        edge_key = tuple(sorted((node_a, node_b)))
        edge_lengths[edge_key] = graph[node_a][node_b]["weight"]
        total_m += graph[node_a][node_b]["weight"]

    for node_a, node_b, node_c in zip(path_nodes, path_nodes[1:], path_nodes[2:]):
        if node_a == node_c and graph.degree[node_b] > 1:
            has_bad_immediate_reverse = True
            break

    backtrack_m = 0.0
    seen_edges = set()
    for node_a, node_b in directed_counts:
        edge_key = tuple(sorted((node_a, node_b)))
        if edge_key in seen_edges:
            continue
        seen_edges.add(edge_key)
        forward = directed_counts.get((node_a, node_b), 0)
        reverse = directed_counts.get((node_b, node_a), 0)
        backtrack_m += min(forward, reverse) * edge_lengths[edge_key]

    return {
        "backtrack_m": round(backtrack_m, 1),
        "backtrack_ratio": round(backtrack_m / total_m, 4) if total_m else 0.0,
        "has_bad_immediate_reverse": has_bad_immediate_reverse,
    }


def route_edge_set(path_nodes: list[Any]) -> set[Any]:
    return {tuple(sorted((a, b))) for a, b in zip(path_nodes, path_nodes[1:])}


def route_uses_dead_end_branch(graph: Any, path_nodes: list[Any]) -> bool:
    return any(graph.degree[node] == 1 for node in path_nodes[1:-1])

# Find task clusters that are near the route for scoring.
def clusters_near_route(
    projected_line: LineString,
    task_clusters: list[dict[str, Any]],
    max_distance_m: float,
) -> list[dict[str, Any]]:
    nearby = []
    for cluster in task_clusters:
        if cluster["projected_geometry"].distance(projected_line) <= max_distance_m:
            nearby.append(cluster)
    return nearby


def score_task_clusters_near_route(
    projected_line: LineString,
    task_clusters: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    nearby = []
    for cluster in task_clusters:
        distance_m = cluster["projected_geometry"].distance(projected_line)
        if distance_m > task_score_max_distance_m:
            continue
        weight = task_cluster_distance_weight(distance_m)
        if weight <= 0:
            continue
        nearby.append({
            **cluster,
            "distance_to_route_m": round(distance_m, 1),
            "route_score_weight": round(weight, 3),
        })
    return sorted(nearby, key=lambda item: (item["distance_to_route_m"], item["cluster_id"]))


def task_cluster_distance_weight(distance_m: float) -> float:
    if distance_m <= task_score_full_distance_m:
        return 1.0
    if distance_m >= task_score_max_distance_m:
        return 0.0
    span = task_score_max_distance_m - task_score_full_distance_m
    return (task_score_max_distance_m - distance_m) / span


def task_cluster_details(clusters: list[dict[str, Any]]) -> str:
    return ";".join(
        f"{cluster['cluster_id']}@{cluster['distance_to_route_m']}m*w{cluster['route_score_weight']}"
        for cluster in clusters
    )


def build_route_task_rows_from_clusters(
    projected_line: LineString,
    clusters: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    seen_task_ids = set()
    for cluster in clusters:
        for stop_order, task in enumerate(cluster.get("tasks", []), start=1):
            task_id = int(task["task_id"])
            if task_id in seen_task_ids:
                continue
            seen_task_ids.add(task_id)
            rows.append({
                "task_id": task_id,
                "cluster_id": cluster["cluster_id"],
                "task_name": task["task_name"],
                "task_sequence_within_cluster": stop_order,
                "distance_from_route_m": round(task["projected_geometry"].distance(projected_line), 1),
            })
    return sorted(rows, key=lambda item: (item["distance_from_route_m"], item["task_id"]))


def select_best_routes(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected = []
    for difficulty in difficulty_specs:
        scored = []
        for candidate in candidates:
            score = score_route(candidate, difficulty)
            if score is None:
                continue
            scored.append({**candidate, **score, "difficulty": difficulty.name})
        scored = sorted(scored, key=lambda item: item["route_score"], reverse=True)

        # Pick the strongest route for each difficulty while avoiding duplicates.
        best = None
        for candidate in scored:
            if is_too_similar_to_selected(candidate, selected):
                continue
            best = candidate
            break
        if best is None:
            print(f"  warning: {difficulty.name} route cannot be generated naturally")
            continue
        selected.append(best)
    return adjust_selected_route_difficulties(selected)

# After selecting the best route for each difficulty, adjust displayed difficulty based on task score to prevent just base on distance.
def adjust_selected_route_difficulties(selected: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not selected:
        return selected

    ranks = {difficulty.name: index for index, difficulty in enumerate(difficulty_specs)}
    names = [difficulty.name for difficulty in difficulty_specs]
    adjusted = []
    used_final_difficulties = set()

    # After route selection, task score can promote/demote the displayed level.
    for route in sorted(selected, key=lambda item: ranks[item["difficulty"]], reverse=True):
        base_difficulty = route["difficulty"]
        proposed_difficulty, reason = proposed_task_adjusted_difficulty(route, ranks, names)
        final_difficulty = proposed_difficulty
        adjustment_applied = proposed_difficulty != base_difficulty

        if final_difficulty in used_final_difficulties:
            final_difficulty = base_difficulty
            adjustment_applied = False
            reason = "kept base difficulty because adjusted level was already selected"

        route = {
            **route,
            "base_difficulty": base_difficulty,
            "difficulty": final_difficulty,
            "task_difficulty_adjustment": reason,
            "difficulty_adjusted_by_task_score": adjustment_applied,
        }
        used_final_difficulties.add(final_difficulty)
        adjusted.append(route)

    return sorted(adjusted, key=lambda item: ranks[item["difficulty"]])


def proposed_task_adjusted_difficulty(
    route: dict[str, Any],
    ranks: dict[str, int],
    names: list[str],
) -> tuple[str, str]:
    base_difficulty = route["difficulty"]
    rank = ranks[base_difficulty]
    task_score = route["task_score"]

    if task_score >= task_difficulty_promote_score and rank < len(names) - 1:
        return names[rank + 1], f"promoted by task_score >= {task_difficulty_promote_score}"
    if task_score <= task_difficulty_demote_score and rank > 0:
        return names[rank - 1], f"demoted by task_score <= {task_difficulty_demote_score}"
    return base_difficulty, "kept base difficulty"


def score_route(candidate: dict[str, Any], difficulty: DifficultySpec) -> dict[str, float] | None:
    distance_fit = range_fit_score(candidate["distance_m"], difficulty.distance_min, difficulty.distance_max)
    if distance_fit < min_distance_fit_for_selection:
        return None
    distance_score = distance_fit * 100
    coverage_score = 0.0
    task_score = min(max_task_score, candidate["task_cluster_score_units"] * task_score_points_per_cluster)
    backtrack_penalty = candidate["backtrack_ratio"] * 100
    route_score = distance_score + coverage_score + task_score - backtrack_penalty
    return {
        "distance_fit_score": round(distance_fit, 3),
        "distance_score": round(distance_score, 1),
        "coverage_score": round(coverage_score, 1),
        "task_score": round(task_score, 1),
        "task_cluster_score_units": round(candidate["task_cluster_score_units"], 3),
        "backtrack_penalty": round(backtrack_penalty, 1),
        "route_score": round(route_score, 1),
    }


def range_fit_score(value: float, minimum: float, maximum: float) -> float:
    if minimum <= value <= maximum:
        return 1.0
    if value < minimum:
        return max(0.0, value / minimum)
    tolerance = max(maximum - minimum, minimum)
    return max(0.0, 1.0 - (value - maximum) / tolerance)


def is_too_similar_to_selected(candidate: dict[str, Any], selected: list[dict[str, Any]]) -> bool:
    for existing in selected:
        union = candidate["edge_set"] | existing["edge_set"]
        if not union:
            continue
        jaccard = len(candidate["edge_set"] & existing["edge_set"]) / len(union)
        if jaccard > max_selected_edge_jaccard:
            return True
    return False


def build_route_row(park: Any, route: dict[str, Any]) -> dict[str, Any]:
    route_id = f"{int(park['park_id'])}_{route['difficulty'].lower()}_preset"
    route_name = f"{park['park_name']} {route['difficulty']} preset route"
    return {
        "route_id": route_id,
        "route_name": route_name,
        "park_id": int(park["park_id"]),
        "park_name": park["park_name"],
        "base_difficulty": route["base_difficulty"],
        "difficulty": route["difficulty"],
        "walking_time_sec": route["walking_time_sec"],
        "route_score": route["route_score"],
        "distance_score": route["distance_score"],
        "total_distance_m": route["distance_m"],
        "task_score": route["task_score"],
        "nearby_task_cluster_count": route["nearby_task_cluster_count"],
        "nearby_task_count": route["nearby_task_count"],
        "route_task_rows": route["route_task_rows"],
        "start_gate_name": route["start"]["name"],
        "start_gate_source": route["start"]["source"],
        "geometry": route["geometry"],
    }


def print_summary(routes: Any) -> None:
    print("")
    print("Preset route summary:")
    if routes.empty:
        print("No routes generated")
        return
    print(routes.groupby("difficulty").size().to_string())
    print("")
    print(routes[[
        "park_name",
        "difficulty",
        "base_difficulty",
        "total_distance_m",
        "walking_time_sec",
        "nearby_task_cluster_count",
        "task_score",
        "route_score",
    ]].sort_values(["park_name", "difficulty"]).to_string(index=False))
