"""
Folium preview rendering for SnapHunter preset park routes.

Route generation and SQL export are handled by the route pipeline modules.
"""

from __future__ import annotations

import html
from pathlib import Path
from typing import Any

import folium
import geopandas as gpd
import pandas as pd

from park_route_data import build_task_clusters_for_park, stringify


wgs84_crs = "EPSG:4326"
projected_crs = "EPSG:7855"
task_score_max_distance_m = 50

route_colors = {
    "Easy": "#2a9d8f",
    "Medium": "#1f78ff",
    "Adventure": "#e76f51",
}
task_cluster_color = "#f4a261"


def create_preview_map(
    parks: Any,
    roads: Any,
    entrances: Any,
    routes: Any,
    tasks: Any,
    output_html: Path,
) -> None:
    center = parks.to_crs(projected_crs).union_all().centroid
    center_wgs84 = gpd.GeoSeries([center], crs=projected_crs).to_crs(wgs84_crs).iloc[0]
    map_view = folium.Map(location=[center_wgs84.y, center_wgs84.x], zoom_start=13, tiles="OpenStreetMap")

    route_park_ids = set(routes["park_id"].astype(int)) if not routes.empty else set()
    add_park_layer(map_view, parks[parks["park_id"].astype(int).isin(route_park_ids)].copy())
    add_road_layer(map_view, roads, parks, route_park_ids)
    add_gate_layer(map_view, entrances, route_park_ids)
    add_task_cluster_layer(map_view, parks, tasks, routes)
    add_route_layers(map_view, routes)
    add_legend(map_view)

    folium.LayerControl(collapsed=False).add_to(map_view)
    map_view.save(output_html)


def add_park_layer(map_view: Any, parks: Any) -> None:
    if parks.empty:
        return
    fields = [field for field in ["park_id", "park_name", "park_ha_level"] if field in parks.columns]
    folium.GeoJson(
        parks[fields + ["geometry"]],
        name=f"Large park boundaries ({len(parks)})",
        style_function=lambda _: {"color": "#176f3a", "weight": 2, "fillColor": "#69bd73", "fillOpacity": 0.08},
        tooltip=folium.GeoJsonTooltip(fields=["park_name"], aliases=["Park"]),
        popup=folium.GeoJsonPopup(fields=fields, aliases=[pretty(field) for field in fields]),
    ).add_to(map_view)


def add_road_layer(map_view: Any, roads: Any, parks: Any, route_park_ids: set[int]) -> None:
    layer = folium.FeatureGroup(name="Internal road/path network", show=False)
    for _, park in parks[parks["park_id"].astype(int).isin(route_park_ids)].iterrows():
        park_roads = get_internal_roads_for_park(roads, park)
        for _, row in park_roads.iterrows():
            folium.GeoJson(
                row.geometry,
                style_function=lambda _: {"color": "#999999", "weight": 1, "opacity": 0.35},
            ).add_to(layer)
    layer.add_to(map_view)


def get_internal_roads_for_park(roads: Any, park: Any) -> Any:
    park_id = int(park["park_id"])
    return roads[
        pd.to_numeric(roads.get("park_id"), errors="coerce") == park_id
    ].copy()


def add_gate_layer(map_view: Any, entrances: Any, route_park_ids: set[int]) -> None:
    layer = folium.FeatureGroup(name="OSM gates / entrances", show=True)
    if not entrances.empty and "park_id" in entrances.columns:
        show = entrances[entrances["park_id"].astype(int).isin(route_park_ids)].copy()
        for _, row in show.iterrows():
            label = row.get("name") or row.get("entrance") or row.get("barrier") or "gate/entrance"
            folium.CircleMarker(
                location=[row.geometry.y, row.geometry.x],
                radius=4,
                color="#ffffff",
                weight=1,
                fill=True,
                fill_color="#e63946",
                fill_opacity=0.95,
                tooltip=f"{row.get('park_name')}: {label}",
            ).add_to(layer)
    layer.add_to(map_view)


def add_task_cluster_layer(map_view: Any, parks: Any, tasks: Any, routes: Any) -> None:
    if tasks.empty or routes.empty:
        return

    used_cluster_ids = set()
    for value in routes.get("nearby_task_cluster_ids", []):
        used_cluster_ids.update(parse_cluster_ids(value))
    if not used_cluster_ids:
        return

    route_park_ids = set(routes["park_id"].astype(int))
    layer = folium.FeatureGroup(name=f"Task clusters scored within {task_score_max_distance_m}m", show=True)
    for _, park in parks[parks["park_id"].astype(int).isin(route_park_ids)].iterrows():
        for cluster in build_task_clusters_for_park(park, tasks):
            if cluster["cluster_id"] not in used_cluster_ids:
                continue
            names = [name for name in cluster["task_names"] if stringify(name)]
            popup = popup_table([
                ("Park", park.get("park_name")),
                ("Cluster ID", cluster["cluster_id"]),
                ("Task count", cluster["task_count"]),
                ("Task names", ", ".join(names[:8]) + (" ..." if len(names) > 8 else "")),
            ])
            radius = min(12, 5 + cluster["task_count"])
            folium.CircleMarker(
                location=[cluster["geometry"].y, cluster["geometry"].x],
                radius=radius,
                color="#7a4f01",
                weight=1,
                fill=True,
                fill_color=task_cluster_color,
                fill_opacity=0.85,
                tooltip=f"{park.get('park_name')} task cluster: {cluster['task_count']} tasks",
                popup=folium.Popup(popup, max_width=420),
            ).add_to(layer)
    layer.add_to(map_view)


def parse_cluster_ids(value: Any) -> list[str]:
    text = stringify(value)
    if not text:
        return []
    return [item.strip() for item in text.split(",") if item.strip()]


def add_route_layers(map_view: Any, routes: Any) -> None:
    if routes.empty:
        return
    for difficulty, group in routes.groupby("difficulty", sort=False):
        color = route_colors.get(difficulty, "#333333")
        layer = folium.FeatureGroup(name=f"{difficulty} preset routes ({len(group)})", show=True)
        for _, row in group.iterrows():
            folium.GeoJson(
                row.geometry,
                style_function=lambda _, color=color: {"color": color, "weight": 5, "opacity": 0.9},
                tooltip=f"{row['park_name']} {difficulty}: {row['total_distance_m']}m",
                popup=folium.Popup(route_popup(row), max_width=450),
            ).add_to(layer)
        layer.add_to(map_view)


def route_popup(row: Any) -> str:
    return popup_table([
        ("Park", row.get("park_name")),
        ("Difficulty", row.get("difficulty")),
        ("Base difficulty", row.get("base_difficulty")),
        ("Distance m", row.get("total_distance_m")),
        ("Walking time sec", row.get("walking_time_sec")),
        ("Route score", row.get("route_score")),
        ("Distance score", row.get("distance_score")),
        ("Task score", row.get("task_score")),
        ("Nearby task clusters", row.get("nearby_task_cluster_count")),
        ("Nearby tasks", row.get("nearby_task_count")),
        ("Start gate", row.get("start_gate_name")),
    ])


def popup_table(fields: list[tuple[str, Any]]) -> str:
    rows = ["<table>"]
    for label, value in fields:
        rows.append(
            "<tr>"
            f"<th style='text-align:left;padding-right:8px'>{html.escape(str(label))}</th>"
            f"<td>{html.escape(stringify(value) or '-')}</td>"
            "</tr>"
        )
    rows.append("</table>")
    return "".join(rows)


def add_legend(map_view: Any) -> None:
    items = [
        (route_colors["Easy"], "Easy route"),
        (route_colors["Medium"], "Medium route"),
        (route_colors["Adventure"], "Adventure route"),
        ("#999999", "Internal road/path"),
        ("#e63946", "Gate / entrance"),
        (task_cluster_color, "Task cluster scored <=50m"),
    ]
    item_html = "".join(
        "<div style='display:flex;align-items:center;gap:6px;margin:3px 0;'>"
        f"<span style='width:12px;height:12px;border-radius:50%;background:{color};"
        "display:inline-block;border:1px solid #fff;box-shadow:0 0 0 1px #999;'></span>"
        f"<span>{html.escape(label)}</span>"
        "</div>"
        for color, label in items
    )
    legend = f"""
    <div style="
        position: fixed;
        bottom: 24px;
        left: 24px;
        z-index: 9999;
        background: white;
        padding: 10px 12px;
        border: 1px solid #aaa;
        border-radius: 6px;
        box-shadow: 0 1px 6px rgba(0,0,0,0.2);
        font-size: 13px;
    ">
        <strong>Preset Park Routes</strong>
        {item_html}
    </div>
    """
    map_view.get_root().html.add_child(folium.Element(legend))


def pretty(value: str) -> str:
    return value.replace("_", " ").title()
