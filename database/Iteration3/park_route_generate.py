"""Command-line entry point for the park route pipeline."""

from __future__ import annotations

from pathlib import Path

from park_route_data import load_inputs
from park_route_planner import build_routes_for_parks, print_summary
from park_route_preview import create_preview_map
from park_route_sql_export import write_insert_sql


output_routes = Path("output/park_preset_routes.geojson")
output_html = Path("output/park_preset_routes_preview.html")
output_sql = Path("output/park_preset_routes_insert.sql")


def save_outputs(routes, parks, roads, entrances, tasks) -> None:
    output_routes.parent.mkdir(parents=True, exist_ok=True)

    # route_task_rows is only used by SQL export; keep it out of the GeoJSON.
    sql_routes = routes.copy()
    map_routes = routes.drop(columns=["route_task_rows"], errors="ignore")

    map_routes.to_file(output_routes, driver="GeoJSON")
    create_preview_map(parks, roads, entrances, map_routes, tasks, output_html)
    write_insert_sql(sql_routes, output_sql)

    print(f"Output routes GeoJSON: {output_routes}")
    print(f"Output HTML: {output_html}")
    print(f"Output route insert SQL: {output_sql}")


def main() -> None:
    route_parks, roads, entrances, tasks = load_inputs()
    routes = build_routes_for_parks(route_parks, roads, entrances, tasks)
    save_outputs(routes, route_parks, roads, entrances, tasks)
    print_summary(routes)


if __name__ == "__main__":
    main()
