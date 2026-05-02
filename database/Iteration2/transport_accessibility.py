from __future__ import annotations

from pathlib import Path
import geopandas as gpd
import pandas as pd

# Set input and output paths
parks_path = Path("melbourne_city_parks_final.csv")
stops_path = Path("public_transport_stops.geojson")
output_path = Path("park_transport_accessibility.csv")

# Set CRS for coordinate systems, using a metre-based CRS for distance calculations.
source_crs = "EPSG:4326"
distance_crs = "EPSG:7855"  # GDA2020 / MGA zone 55, metre-based for Melbourne.

park_id_col = "park_id"
park_name_col = "park_name"
park_lat_col = "latitude"
park_lon_col = "longitude"

stop_mode_col = "MODE"

# Distance bands used by the transport score.
stop_search_buffer_m = 2_000.0
near_radius_m = 300.0
walk_radius_m = 500.0

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
    parks_df = pd.read_csv(parks_path, encoding="utf-8-sig")
    parks = gpd.GeoDataFrame(
        parks_df,
        geometry=gpd.points_from_xy(parks_df[park_lon_col], parks_df[park_lat_col]),
        crs=source_crs,
    )

    if parks.crs is None:
        parks = parks.set_crs(source_crs)
    else:
        parks = parks.to_crs(source_crs)

    stops = gpd.read_file(stops_path)

    if stops.crs is None:
        stops = stops.set_crs(source_crs)
    else:
        stops = stops.to_crs(source_crs)

    stops = stops[~stops.geometry.is_empty & stops.geometry.notna()].copy()
    stops["transport_mode"] = stops[stop_mode_col].apply(clean_transport_mode)

    # Project to metres before measuring distance.
    parks_projected = parks.to_crs(distance_crs)
    stops_projected = stops.to_crs(distance_crs)

    # The stop file covers a larger area than the parks. A loose bounding box keeps the calculation quick while still leaving room for nearest stops.
    minx, miny, maxx, maxy = parks_projected.total_bounds
    relevant_stops = stops_projected.cx[
        minx - stop_search_buffer_m : maxx + stop_search_buffer_m,
        miny - stop_search_buffer_m : maxy + stop_search_buffer_m,
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
        stops_300 = stops.loc[distances <= near_radius_m]
        stops_500 = stops.loc[distances <= walk_radius_m]
        modes_500 = set(stops_500["transport_mode"].dropna())

        tram_count = int((stops_500["transport_mode"] == "tram").sum())
        bus_count = int((stops_500["transport_mode"] == "bus").sum())
        train_count = int((stops_500["transport_mode"] == "train").sum())

        metric_rows.append(
            {
                park_id_col: park[park_id_col],
                park_name_col: park[park_name_col],
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
        park_id_col,
        park_name_col,
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
    results.to_csv(output_path, index=False, encoding="utf-8-sig")
    return results


def main() -> None:
    parks, stops = load_data()
    metrics = calculate_accessibility_metrics(parks, stops)
    results = export_results(metrics)
    print(f"Exported {len(results)} park accessibility rows to {output_path}")


if __name__ == "__main__":
    main()
