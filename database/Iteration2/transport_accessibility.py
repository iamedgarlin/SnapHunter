from __future__ import annotations

from pathlib import Path
import sys
import geopandas as gpd
import pandas as pd

# Set input and output paths
PARKS_PATH = Path("melbourne_city_parks_final.csv")
STOPS_PATH = Path("public_transport_stops.geojson")
OUTPUT_PATH = Path("park_transport_accessibility.csv")

# Set CRS for coordinate systems, using a metre-based CRS for distance calculations.
SOURCE_CRS = "EPSG:4326"
DISTANCE_CRS = "EPSG:7855"  # GDA2020 / MGA zone 55, metre-based for Melbourne.

PARK_ID_COL = "park_id"
PARK_NAME_COL = "park_name"
PARK_LAT_COL = "latitude"
PARK_LON_COL = "longitude"

STOP_ID_COL = "STOP_ID"
STOP_NAME_COL = "STOP_NAME"
STOP_MODE_COL = "MODE"

# Distance bands used by the transport score.
STOP_SEARCH_BUFFER_M = 2_000.0
NEAR_RADIUS_M = 300.0
WALK_RADIUS_M = 500.0

# Clean the transport mode values to a consistent set of categories
def clean_transport_mode(mode: object) -> str:
    """Normalize raw stop mode values to tram, train, bus, or other."""
    if pd.isna(mode):
        return "other"

    value = str(mode).strip().lower()

    if "tram" in value:
        return "tram"
    if "train" in value:
        return "train"
    if "bus" in value or "coach" in value:
        return "bus"
    return "other"


# Load the park and stop data
def load_data() -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """Load park points and public transport stops."""
    parks_df = pd.read_csv(PARKS_PATH, encoding="utf-8-sig")
    parks = gpd.GeoDataFrame(
        parks_df,
        geometry=gpd.points_from_xy(parks_df[PARK_LON_COL], parks_df[PARK_LAT_COL]),
        crs=SOURCE_CRS,
    )

    if parks.crs is None:
        parks = parks.set_crs(SOURCE_CRS)
    else:
        parks = parks.to_crs(SOURCE_CRS)

    stops = gpd.read_file(STOPS_PATH)

    if stops.crs is None:
        stops = stops.set_crs(SOURCE_CRS)
    else:
        stops = stops.to_crs(SOURCE_CRS)

    stops = stops[~stops.geometry.is_empty & stops.geometry.notna()].copy()
    stops["transport_mode"] = stops[STOP_MODE_COL].apply(clean_transport_mode)

    # Project to metres before measuring distance.
    parks_projected = parks.to_crs(DISTANCE_CRS)
    stops_projected = stops.to_crs(DISTANCE_CRS)

    # The stop file covers a larger area than the parks. A loose bounding box keeps the calculation quick while still leaving room for nearest stops.
    minx, miny, maxx, maxy = parks_projected.total_bounds
    relevant_stops = stops_projected.cx[
        minx - STOP_SEARCH_BUFFER_M : maxx + STOP_SEARCH_BUFFER_M,
        miny - STOP_SEARCH_BUFFER_M : maxy + STOP_SEARCH_BUFFER_M,
    ].copy()

    if relevant_stops.empty:
        relevant_stops = stops_projected.copy()

    return parks_projected, relevant_stops

# Calculate transport accessibility metrics for each park
def calculate_accessibility_metrics(
    parks: gpd.GeoDataFrame,
    stops: gpd.GeoDataFrame,
) -> pd.DataFrame:
    """Calculate transport metrics for each park."""
    metric_rows: list[dict[str, object]] = []

    if stops.empty:
        raise ValueError("No public transport stops available after filtering.")

    stop_geometries = stops.geometry

    for _, park in parks.iterrows():
        distances = stop_geometries.distance(park.geometry)
        nearest_idx = distances.idxmin()
        nearest_stop = stops.loc[nearest_idx]
        nearest_distance = float(distances.loc[nearest_idx])

        # 300m is treated as very close; 500m is a typical walking catchment.
        stops_300 = stops.loc[distances <= NEAR_RADIUS_M]
        stops_500 = stops.loc[distances <= WALK_RADIUS_M]
        modes_500 = set(stops_500["transport_mode"].dropna())

        tram_count = int((stops_500["transport_mode"] == "tram").sum())
        bus_count = int((stops_500["transport_mode"] == "bus").sum())
        train_count = int((stops_500["transport_mode"] == "train").sum())

        metric_rows.append(
            {
                PARK_ID_COL: park[PARK_ID_COL],
                PARK_NAME_COL: park[PARK_NAME_COL],
                "nearest_stop_distance_m": round(nearest_distance, 1),
                "nearest_stop_mode": nearest_stop["transport_mode"],
                "stops_within_300m": int(len(stops_300)),
                "stops_within_500m": int(len(stops_500)),
                "tram_stops_within_500m": tram_count,
                "bus_stops_within_500m": bus_count,
                "train_stops_within_500m": train_count,
                "transport_modes_count": int(len(modes_500)),
                "has_tram": tram_count > 0,
                "has_bus": bus_count > 0,
                "has_train": train_count > 0,
            }
        )

    return pd.DataFrame(metric_rows)

# Score the accessibility based on the calculated metrics
def calculate_accessibility_score(row: pd.Series) -> int:
    """Score public transport access from 0 to 10."""
    raw_score = 0
    distance = row["nearest_stop_distance_m"]

    # Closer nearest stop means less walking before the trip starts
    if distance <= 200:
        raw_score += 3
    elif distance <= 400:
        raw_score += 2
    elif distance <= 600:
        raw_score += 1
    elif distance > 800:
        raw_score -= 2

    # More nearby stops usually means better frequency and more route choices
    if row["stops_within_300m"] >= 3:
        raw_score += 2
    if row["stops_within_500m"] >= 5:
        raw_score += 2

    # Mode diversity matters: a park served by tram + bus is more flexible than a park served by only one mode.
    if row["transport_modes_count"] >= 2:
        raw_score += 2
    elif row["transport_modes_count"] == 1:
        raw_score += 1

    return int(min(max(raw_score, 0), 10))

# Convert the score to a clear label for easier interpretation 
def assign_accessibility_level(score: float) -> str:
    """Turn the numeric score into a readable label."""
    if score >= 8:
        return "High accessibility"
    if score >= 5:
        return "Medium accessibility"
    return "Low accessibility"

# Export the transport accessibility results
def export_results(metrics: pd.DataFrame) -> pd.DataFrame:
    """Export transport-related fields only."""
    metrics = metrics.copy()
    metrics["transport_accessibility_score"] = metrics.apply(
        calculate_accessibility_score,
        axis=1,
    )
    metrics["accessibility_level"] = metrics["transport_accessibility_score"].apply(
        assign_accessibility_level
    )
    metrics["low_accessibility_warning"] = metrics["transport_accessibility_score"] < 3

    output_cols = [
        PARK_ID_COL,
        PARK_NAME_COL,
        "nearest_stop_distance_m",
        "nearest_stop_mode",
        "stops_within_300m",
        "stops_within_500m",
        "tram_stops_within_500m",
        "bus_stops_within_500m",
        "train_stops_within_500m",
        "transport_modes_count",
        "has_tram",
        "has_bus",
        "has_train",
        "transport_accessibility_score",
        "accessibility_level",
        "low_accessibility_warning",
    ]

    results = metrics[output_cols].copy()
    results.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    return results


def main() -> None:
    parks, stops = load_data()
    metrics = calculate_accessibility_metrics(parks, stops)
    results = export_results(metrics)
    print(f"Exported {len(results)} park accessibility rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
