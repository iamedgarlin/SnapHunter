"""
Build MySQL INSERT statements for route and route_task.

Table creation is managed separately. The exporter only serializes route rows
produced by the route pipeline.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any


# Each nearby task adds three minutes to the route completion estimate.
task_completion_sec = 180


def write_insert_sql(routes: Any, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "-- SnapHunter preset route inserts.",
        "-- Table creation is handled separately.",
        "START TRANSACTION;",
        "",
    ]

    if routes.empty:
        lines.extend(["-- No routes generated.", "COMMIT;", ""])
        output_path.write_text("\n".join(lines), encoding="utf-8")
        return

    for route_index, (_, route) in enumerate(routes.iterrows(), start=1):
        route_var = f"@route_id_{route_index}"
        lines.extend(build_route_insert_sql(route, route_var))
        lines.append("")

    lines.append("COMMIT;")
    lines.append("")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def build_route_insert_sql(route: Any, route_var: str) -> list[str]:
    difficulty_level = mysql_string(route_difficulty_level(route.get("difficulty")))
    distance_m = sql_decimal(route.get("total_distance_m"), 2)
    estimated_time_sec = int(
        math.ceil(
            float(route.get("walking_time_sec", 0))
            + int(route.get("nearby_task_count", 0)) * task_completion_sec
        )
    )
    start_point_wkt = mysql_string(route_start_point_wkt(route.geometry))
    line_wkt = mysql_string(route.geometry.wkt)
    task_rows = route.get("route_task_rows") or []

    lines = [
        "INSERT INTO `route` (",
        "    park_id, difficulty_level, distance_m, estimated_time_sec,",
        "    start_point, st_line, task_cluster_count, original_task_count",
        ") VALUES (",
        f"    {int(route['park_id'])}, {difficulty_level}, {distance_m}, {estimated_time_sec},",
        f"    ST_GeomFromText({start_point_wkt}, 4326),",
        f"    ST_GeomFromText({line_wkt}, 4326),",
        f"    {int(route.get('nearby_task_cluster_count', 0))}, {int(route.get('nearby_task_count', 0))}",
        ");",
        f"SET {route_var} = LAST_INSERT_ID();",
    ]

    if task_rows:
        lines.extend(build_route_task_insert_sql(route_var, task_rows))
    return lines


def build_route_task_insert_sql(route_var: str, task_rows: list[dict[str, Any]]) -> list[str]:
    values = []
    for task in task_rows:
        values.append(
            f"    ({route_var}, {int(task['task_id'])}, {sql_decimal(task['distance_from_route_m'], 2)})"
        )
    return [
        "INSERT INTO `route_task` (route_id, task_id, distance_from_route_m) VALUES",
        ",\n".join(values) + ";",
    ]


def route_difficulty_level(value: Any) -> str:
    difficulty = stringify(value).strip()
    if difficulty not in {"Easy", "Medium", "Adventure"}:
        raise ValueError(f"Unsupported route difficulty: {difficulty}")
    return difficulty


def route_start_point_wkt(geometry: Any) -> str:
    if geometry is None or geometry.is_empty:
        return "POINT EMPTY"
    first_coord = list(geometry.coords)[0]
    return f"POINT ({first_coord[0]} {first_coord[1]})"


def sql_decimal(value: Any, digits: int) -> str:
    return f"{float(value):.{digits}f}"


def mysql_string(value: Any) -> str:
    return "'" + stringify(value).replace("\\", "\\\\").replace("'", "''") + "'"


def stringify(value: Any) -> str:
    if value is None:
        return ""
    try:
        if value != value:
            return ""
    except (TypeError, ValueError):
        pass
    return str(value)
