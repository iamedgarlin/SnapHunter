"""
Prepare OSM paths, entrances, and park boundaries for route generation.

The export keeps parks with park_ha_level >= 8 and at least three non-landmark
tasks. Route generation then uses these prepared files directly.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import geopandas as gpd
import pandas as pd
import requests
from shapely.geometry import GeometryCollection, LineString, MultiLineString, Point


park_table_file = Path("park_table.csv")
boundary_file = Path("park_polygon_clean.geojson")
task_files = [
    Path("park_feature_join_tree_flower.csv"),
    Path("park_feature_join_artwork_landmark.csv"),
]
output_dir = Path("output")
park_boundaries_output = output_dir / "parks_with_boundaries.geojson"
osm_roads_output = output_dir / "parks_osm_internal_roads.geojson"
osm_entrances_output = output_dir / "parks_osm_gates_entrances.geojson"

overpass_url = "https://overpass-api.de/api/interpreter"
overpass_timeout = 180
projected_crs = "EPSG:7855"
wgs84_crs = "EPSG:4326"
entrance_buffer_m = 35
large_park_min_level = 8
min_task_count = 3

walkable_highways = [
    "footway",
    "path",
    "pedestrian",
    "track",
    "steps",
]

# Some parks tag internal shared paths or access roads with road-like highway classes.
additional_highways = [
    "cycleway",
    "service",
    "living_street",
    "unclassified",
    "residential",
]

walkable_routes = [
    "foot",
    "hiking",
    "walking",
]


def select_parks_for_osm_export() -> gpd.GeoDataFrame:
    parks = pd.read_csv(park_table_file, encoding="utf-8-sig")
    tasks = load_task_source_files()

    if "feature_source" in tasks.columns:
        tasks = tasks[tasks["feature_source"].astype(str).str.lower() != "landmark"].copy()

    counts = tasks.groupby("park_id").size().reset_index(name="task_count")
    parks["park_id"] = pd.to_numeric(parks["park_id"], errors="coerce")
    counts["park_id"] = pd.to_numeric(counts["park_id"], errors="coerce")
    merged = parks.merge(counts, on="park_id", how="left")
    merged["task_count"] = merged["task_count"].fillna(0).astype(int)
    merged["park_ha_level"] = pd.to_numeric(merged["park_ha_level"], errors="coerce")

    selected = merged[
        (merged["park_ha_level"] >= large_park_min_level)
        & (merged["task_count"] >= min_task_count)
    ].copy()
    selected = selected[["park_id", "park_name", "latitude", "longitude", "park_ha_level", "task_count"]]

    boundaries = gpd.read_file(boundary_file).to_crs(wgs84_crs)
    park_boundaries = boundaries.merge(
        selected,
        on=["park_id", "park_name"],
        how="inner",
    )
    park_boundaries = park_boundaries.sort_values(["park_name"]).reset_index(drop=True)
    if park_boundaries.empty:
        raise ValueError("No selected parks matched park_polygon_clean.geojson.")
    return park_boundaries


def load_task_source_files() -> pd.DataFrame:
    frames = []
    for path in task_files:
        frame = pd.read_csv(path, encoding="utf-8-sig")
        frame["source_file"] = path.name
        frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def overpass_query(query: str) -> dict[str, Any]:
    response = requests.post(
        overpass_url,
        data={"data": query},
        timeout=overpass_timeout,
        headers={"User-Agent": "SnapHunter park OSM prepare"},
    )
    response.raise_for_status()
    return response.json()


def fetch_walkable_paths_for_boundary(park_row: pd.Series) -> gpd.GeoDataFrame:
    boundary = park_row.geometry
    minx, miny, maxx, maxy = boundary.bounds
    highway_pattern = "|".join(walkable_highways + additional_highways)
    route_pattern = "|".join(walkable_routes)
    query = f"""
    [out:json][timeout:{overpass_timeout}];
    (
      way["highway"~"^({highway_pattern})$"]({miny},{minx},{maxy},{maxx});
      way["route"~"^({route_pattern})$"]({miny},{minx},{maxy},{maxx});
    );
    out tags geom;
    """

    data = overpass_query(query)
    rows = []
    for element in data.get("elements", []):
        if element.get("type") != "way":
            continue
        geometry = line_geometry_from_overpass_element(element)
        if geometry is None:
            continue

        clipped = lineal_geometry_or_none(geometry.intersection(boundary))
        if clipped is None or clipped.is_empty:
            continue

        rows.append(
            {
                "element_type": "way",
                "osmid": element.get("id"),
                "tags": element.get("tags", {}),
                "geometry": clipped,
            }
        )

    if not rows:
        return gpd.GeoDataFrame(geometry=[], crs=wgs84_crs)

    roads = gpd.GeoDataFrame(rows, geometry="geometry", crs=wgs84_crs)
    blocked_mask = roads.apply(
        lambda row: access_is_blocked(tag_value(row, "access")),
        axis=1,
    )
    roads = roads[~blocked_mask].copy()
    if roads.empty:
        return gpd.GeoDataFrame(geometry=[], crs=wgs84_crs)

    roads["length_m"] = roads.to_crs(projected_crs).geometry.length.round(1)
    roads["osm_display_id"] = roads.apply(osm_id_from_row, axis=1)
    return roads


def fetch_entrances_for_boundary(park_row: pd.Series) -> gpd.GeoDataFrame:
    boundary = park_row.geometry
    minx, miny, maxx, maxy = boundary.bounds
    margin = 0.0006
    query = f"""
    [out:json][timeout:{overpass_timeout}];
    (
      node["entrance"]({miny - margin},{minx - margin},{maxy + margin},{maxx + margin});
      node["barrier"~"^(gate|entrance|stile)$"]({miny - margin},{minx - margin},{maxy + margin},{maxx + margin});
    );
    out body;
    """
    data = overpass_query(query)
    rows = []
    for element in data.get("elements", []):
        if element.get("type") != "node":
            continue
        tags = element.get("tags", {})
        rows.append(
            {
                "park_id": int(park_row["park_id"]),
                "park_name": str(park_row["park_name"]),
                "osm_type": element.get("type"),
                "osm_id": element.get("id"),
                "entrance": tags.get("entrance"),
                "barrier": tags.get("barrier"),
                "access": tags.get("access"),
                "name": tags.get("name"),
                "geometry": Point(float(element["lon"]), float(element["lat"])),
            }
        )

    if not rows:
        return gpd.GeoDataFrame(geometry=[], crs=wgs84_crs)

    entrances = gpd.GeoDataFrame(rows, geometry="geometry", crs=wgs84_crs)
    projected_boundary = gpd.GeoSeries([boundary], crs=wgs84_crs).to_crs(projected_crs).iloc[0]
    projected = entrances.to_crs(projected_crs)
    entrances["distance_to_boundary_m"] = projected.geometry.distance(projected_boundary.boundary).round(1)
    entrances["inside_boundary"] = entrances.geometry.within(boundary) | entrances.geometry.touches(boundary)
    entrances = entrances[
        entrances["inside_boundary"] | (entrances["distance_to_boundary_m"] <= entrance_buffer_m)
    ].copy()
    entrances["park_point_lon"] = float(park_row["longitude"])
    entrances["park_point_lat"] = float(park_row["latitude"])
    return entrances.drop_duplicates(subset=["osm_type", "osm_id"]).copy()


def prepare_osm_internal_paths_and_entrances() -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, gpd.GeoDataFrame, pd.DataFrame, list[tuple[str, str]]]:
    park_boundaries = select_parks_for_osm_export()
    park_boundary_frames = []
    route_frames = []
    entrance_frames = []
    failed_parks = []

    for index, park_row in park_boundaries.iterrows():
        print(f"[{index + 1}/{len(park_boundaries)}] Processing {park_row['park_name']}")
        try:
            boundary_gdf = gpd.GeoDataFrame([park_row], geometry="geometry", crs=wgs84_crs)
            park_boundary_frames.append(boundary_gdf)

            routes = fetch_walkable_paths_for_boundary(park_row)
            if not routes.empty:
                routes = format_road_rows(routes, park_row)
                route_frames.append(routes)

            entrances = fetch_entrances_for_boundary(park_row)
            if not entrances.empty:
                entrance_frames.append(entrances)

        except Exception as exc:
            failed_parks.append((str(park_row["park_name"]), str(exc)))
            print(f"  Warning: {exc}")

    park_boundaries_export = gpd.GeoDataFrame(
        pd.concat(park_boundary_frames, ignore_index=True),
        geometry="geometry",
        crs=wgs84_crs,
    )
    park_routes_export = (
        gpd.GeoDataFrame(pd.concat(route_frames, ignore_index=True), geometry="geometry", crs=wgs84_crs)
        if route_frames
        else gpd.GeoDataFrame(geometry=[], crs=wgs84_crs)
    )
    park_entrances_export = (
        gpd.GeoDataFrame(pd.concat(entrance_frames, ignore_index=True), geometry="geometry", crs=wgs84_crs)
        if entrance_frames
        else gpd.GeoDataFrame(geometry=[], crs=wgs84_crs)
    )

    write_outputs(park_boundaries_export, park_routes_export, park_entrances_export)
    summary = build_summary(park_boundaries_export, park_routes_export, park_entrances_export)
    print("Export completed.")
    print(summary.to_string(index=False))
    if failed_parks:
        print("Failed parks:")
        for park_name, error in failed_parks:
            print(f"  - {park_name}: {error}")
    return park_boundaries_export, park_routes_export, park_entrances_export, summary, failed_parks


def format_road_rows(routes: gpd.GeoDataFrame, park_row: pd.Series) -> gpd.GeoDataFrame:
    routes = routes.copy()
    routes["_geom_wkb"] = routes.geometry.apply(lambda geometry: geometry.wkb_hex)
    if "osm_display_id" not in routes.columns:
        routes["osm_display_id"] = routes.apply(osm_id_from_row, axis=1)
    routes = routes.drop_duplicates(subset=["osm_display_id", "_geom_wkb"]).drop(columns=["_geom_wkb"])

    routes["park_id"] = int(park_row["park_id"])
    routes["park_name"] = str(park_row["park_name"])
    routes["road_type"] = routes.apply(
        lambda row: stringify_tag(tag_value(row, "highway"))
        or stringify_tag(tag_value(row, "route"))
        or "unknown",
        axis=1,
    )
    routes["road_surface"] = routes.apply(
        lambda row: stringify_tag(tag_value(row, "surface")),
        axis=1,
    )
    routes["road_access"] = routes.apply(
        lambda row: stringify_tag(tag_value(row, "access")),
        axis=1,
    )
    routes["road_name"] = routes.apply(
        lambda row: stringify_tag(tag_value(row, "name")),
        axis=1,
    )
    return routes


def write_outputs(boundaries: gpd.GeoDataFrame, roads: gpd.GeoDataFrame, entrances: gpd.GeoDataFrame) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    boundaries.to_file(park_boundaries_output, driver="GeoJSON")
    if not roads.empty:
        roads.to_file(osm_roads_output, driver="GeoJSON")
    if not entrances.empty:
        entrances.to_file(osm_entrances_output, driver="GeoJSON")


def build_summary(boundaries: gpd.GeoDataFrame, roads: gpd.GeoDataFrame, entrances: gpd.GeoDataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"layer": "boundaries", "count": len(boundaries), "path": str(park_boundaries_output)},
            {"layer": "internal_roads", "count": len(roads), "path": str(osm_roads_output)},
            {"layer": "gates_entrances", "count": len(entrances), "path": str(osm_entrances_output)},
        ]
    )


def line_geometry_from_overpass_element(element: dict[str, Any]) -> LineString | None:
    coords = [
        (float(point["lon"]), float(point["lat"]))
        for point in element.get("geometry", [])
        if "lon" in point and "lat" in point
    ]
    if len(coords) < 2:
        return None
    return LineString(coords)


def lineal_geometry_or_none(geometry: Any) -> LineString | MultiLineString | None:
    if geometry is None or geometry.is_empty:
        return None
    if isinstance(geometry, (LineString, MultiLineString)):
        return geometry
    if isinstance(geometry, GeometryCollection):
        lines = []
        for part in geometry.geoms:
            if isinstance(part, LineString):
                lines.append(part)
            elif isinstance(part, MultiLineString):
                lines.extend(part.geoms)
        if not lines:
            return None
        return MultiLineString(lines) if len(lines) > 1 else lines[0]
    return None


def access_is_blocked(value: Any) -> bool:
    return stringify_tag(value).lower() in {"private", "no"}


def tag_value(row: Any, key: str) -> Any:
    tags = row.get("tags") if hasattr(row, "get") else None
    if isinstance(tags, dict) and key in tags:
        return tags.get(key)
    return row.get(key) if hasattr(row, "get") else None


def osm_id_from_row(row: Any) -> str:
    element_type = row.get("element_type") or row.get("osm_type") or "way"
    osmid = row.get("osmid") if row.get("osmid") is not None else row.get("osm_id")
    return f"{element_type}/{osmid}"


def stringify_tag(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return ",".join(str(item) for item in value if item is not None)
    return str(value)


if __name__ == "__main__":
    prepare_osm_internal_paths_and_entrances()
