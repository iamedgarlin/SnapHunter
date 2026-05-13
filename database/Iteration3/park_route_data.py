"""Data loading and task preparation for park route generation."""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any

import geopandas as gpd
import networkx as nx
import pandas as pd


# Prepared OSM exports from park_osm_prepare.py.
prepared_boundaries_file = Path("output/parks_with_boundaries.geojson")
osm_roads_file = Path("output/parks_osm_internal_roads.geojson")
entrances_file = Path("output/parks_osm_gates_entrances.geojson")
task_files = [
    Path("park_feature_join_tree_flower.csv"),
    Path("park_feature_join_artwork_landmark.csv"),
]
task_id_mapping_file = Path("task_202605131503.csv")

wgs84_crs = "EPSG:4326"
projected_crs = "EPSG:7855"
task_cluster_distance_m = 35
task_id_match_max_distance_m = 1.0

warnings.filterwarnings("ignore", category=RuntimeWarning, module="shapely")


def load_inputs() -> tuple[Any, Any, Any, Any]:
    parks = load_route_parks()
    roads = load_existing_road_network()
    entrances = load_entrances()
    tasks = load_task_points()
    print(f"Loaded prepared route parks: {len(parks)}")
    print(f"Loaded road/path features: {len(roads)}")
    print(f"Loaded gates/entrances: {len(entrances)}")
    print(f"Loaded task points for route scoring: {len(tasks)}")
    return parks, roads, entrances, tasks


def load_route_parks() -> Any:
    if not prepared_boundaries_file.exists():
        raise FileNotFoundError(
            f"Prepared park boundary file not found: {prepared_boundaries_file}. "
            "Run park_osm_prepare.py before park_route_generate.py."
        )
    parks = gpd.read_file(prepared_boundaries_file).to_crs(wgs84_crs)
    required = {"park_id", "park_name", "latitude", "longitude", "park_ha_level"}
    missing = required - set(parks.columns)
    if missing:
        raise ValueError(f"{prepared_boundaries_file} is missing required columns: {sorted(missing)}")
    parks["park_id"] = pd.to_numeric(parks["park_id"], errors="coerce").astype(int)
    sort_columns = [column for column in ["park_name", "park_id"] if column in parks.columns]
    return parks.sort_values(sort_columns).reset_index(drop=True)


def load_existing_road_network() -> Any:
    if not osm_roads_file.exists():
        raise FileNotFoundError(f"OSM internal road/path network file not found: {osm_roads_file}")
    roads = gpd.read_file(osm_roads_file).to_crs(wgs84_crs)
    roads = roads[roads.geometry.geom_type.isin(["LineString", "MultiLineString"])].copy()
    roads["network_source"] = "osm_internal_roads"
    return roads


def load_entrances() -> Any:
    if not entrances_file.exists():
        return gpd.GeoDataFrame(geometry=[], crs=wgs84_crs)
    entrances = gpd.read_file(entrances_file).to_crs(wgs84_crs)
    return entrances


def load_task_points() -> Any:
    # Tasks are used for scoring and route_task rows. They are not route waypoints.
    frames = []
    for path in task_files:
        if not path.exists():
            continue
        frame = pd.read_csv(path, encoding="utf-8-sig")
        frame["source_file"] = path.name
        frames.append(frame)
    if not frames:
        return gpd.GeoDataFrame(geometry=[], crs=wgs84_crs)
    tasks = pd.concat(frames, ignore_index=True)
    tasks = tasks.dropna(subset=["latitude", "longitude"]).copy()
    tasks = attach_database_task_ids(tasks)
    unmatched = tasks["task_id"].isna()
    if unmatched.any():
        print(f"  warning: {int(unmatched.sum())} source tasks could not be matched to database task_id")
        print(tasks.loc[unmatched, ["park_name", "feature_name", "latitude", "longitude"]].head(8).to_string(index=False))
        tasks = tasks.loc[~unmatched].copy()
    tasks["task_id"] = pd.to_numeric(tasks["task_id"], errors="coerce").astype(int)
    tasks["task_uid"] = tasks["task_id"]
    return gpd.GeoDataFrame(
        tasks,
        geometry=gpd.points_from_xy(tasks["longitude"], tasks["latitude"]),
        crs=wgs84_crs,
    )


def build_task_clusters_for_park(park: Any, tasks: Any) -> list[dict[str, Any]]:
    """Group nearby tasks once so planner and preview use the same clusters."""
    if tasks.empty or "park_id" not in tasks.columns:
        return []
    park_id = int(park["park_id"])
    park_tasks = tasks[pd.to_numeric(tasks["park_id"], errors="coerce") == park_id].copy()
    if park_tasks.empty:
        return []

    projected = park_tasks.to_crs(projected_crs).copy()
    task_graph = nx.Graph()
    task_indices = list(projected.index)
    task_graph.add_nodes_from(task_indices)

    # Connected components mean one task can only belong to one cluster.
    for left_pos, left_idx in enumerate(task_indices):
        left_point = projected.loc[left_idx].geometry
        for right_idx in task_indices[left_pos + 1:]:
            right_point = projected.loc[right_idx].geometry
            if left_point.distance(right_point) <= task_cluster_distance_m:
                task_graph.add_edge(left_idx, right_idx)

    clusters = []
    for cluster_number, component in enumerate(nx.connected_components(task_graph), start=1):
        indices = sorted(component)
        cluster_tasks = park_tasks.loc[indices].copy()
        centroid_projected = projected.loc[indices].geometry.union_all().centroid
        centroid_wgs84 = gpd.GeoSeries([centroid_projected], crs=projected_crs).to_crs(wgs84_crs).iloc[0]
        task_rows = []
        for task_idx in indices:
            task = park_tasks.loc[task_idx]
            task_rows.append({
                "task_id": int(task["task_id"]),
                "task_uid": int(task["task_uid"]),
                "task_name": stringify(task.get("feature_name")),
                "projected_geometry": projected.loc[task_idx].geometry,
                "geometry": task.geometry,
            })
        clusters.append({
            "cluster_id": f"{park_id}_tc{cluster_number}",
            "park_id": park_id,
            "task_count": len(cluster_tasks),
            "task_uids": cluster_tasks["task_uid"].astype(int).tolist(),
            "task_names": cluster_tasks.get("feature_name", pd.Series(dtype=str)).astype(str).tolist(),
            "tasks": task_rows,
            "projected_geometry": centroid_projected,
            "geometry": centroid_wgs84,
        })
    return clusters


def attach_database_task_ids(tasks: Any) -> Any:
    if not task_id_mapping_file.exists():
        raise FileNotFoundError(
            f"Database task export not found: {task_id_mapping_file}. "
            "Export task_id, task_name, latitude, longitude before generating route_task SQL."
        )

    db_tasks = pd.read_csv(task_id_mapping_file, encoding="utf-8-sig")
    required = {"task_id", "task_name", "latitude", "longitude"}
    missing = required - set(db_tasks.columns)
    if missing:
        raise ValueError(f"{task_id_mapping_file} is missing required columns: {sorted(missing)}")

    source = tasks.copy()
    source["_task_name_key"] = source["feature_name"].map(normalize_task_name)
    db_tasks = db_tasks.dropna(subset=["task_id", "task_name", "latitude", "longitude"]).copy()
    db_tasks["_task_name_key"] = db_tasks["task_name"].map(normalize_task_name)

    source_gdf = gpd.GeoDataFrame(
        source,
        geometry=gpd.points_from_xy(source["longitude"], source["latitude"]),
        crs=wgs84_crs,
    ).to_crs(projected_crs)
    db_gdf = gpd.GeoDataFrame(
        db_tasks,
        geometry=gpd.points_from_xy(db_tasks["longitude"], db_tasks["latitude"]),
        crs=wgs84_crs,
    ).to_crs(projected_crs)

    db_by_name = {name: group.copy() for name, group in db_gdf.groupby("_task_name_key")}
    matched_ids = []
    matched_distances = []

    # Match by normalized name first, then use nearest coordinate within 1m.
    for _, source_row in source_gdf.iterrows():
        candidates = db_by_name.get(source_row["_task_name_key"])
        if candidates is None or candidates.empty:
            matched_ids.append(pd.NA)
            matched_distances.append(pd.NA)
            continue
        distances = candidates.geometry.distance(source_row.geometry)
        best_index = distances.idxmin()
        best_distance = float(distances.loc[best_index])
        if best_distance <= task_id_match_max_distance_m:
            matched_ids.append(int(candidates.loc[best_index, "task_id"]))
            matched_distances.append(round(best_distance, 3))
        else:
            matched_ids.append(pd.NA)
            matched_distances.append(round(best_distance, 3))

    source["task_id"] = matched_ids
    source["task_id_match_distance_m"] = matched_distances
    matched_count = source["task_id"].notna().sum()
    print(
        f"Matched database task_id: {matched_count}/{len(source)} "
        f"(name + nearest point <= {task_id_match_max_distance_m}m)"
    )
    return source.drop(columns=["_task_name_key"])


def stringify(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    return str(value)


def normalize_task_name(value: Any) -> str:
    return " ".join(stringify(value).strip().lower().split())
