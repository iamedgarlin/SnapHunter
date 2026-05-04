from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

# Set input and output paths
park_enriched_path = Path("park_enriched_final.csv")
transport_accessibility_path = Path("park_transport_accessibility.csv")
output_path = Path("park_table.csv")

park_id_col = "park_id"
area_ha_col = "ha"
park_suitability_score_col = "park_suitability_score"
transport_score_col = "transport_accessibility_score"

# Load data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load park enrichment and the transport score table."""
    parks = pd.read_csv(park_enriched_path, encoding="utf-8-sig")
    transport = pd.read_csv(transport_accessibility_path, encoding="utf-8-sig")
    return parks, transport

# merge transport score with park data
def merge_transport_score(
    parks: pd.DataFrame,
    transport: pd.DataFrame,
) -> tuple[pd.DataFrame, int]:
    """Join the transport accessibility score with the park"""
    transport_score = transport[[park_id_col, transport_score_col]].copy()
    merged = parks.merge(transport_score, on=park_id_col, how="left")

    missing_transport_score_count = int(merged[transport_score_col].isna().sum())
    merged[transport_score_col] = (
        pd.to_numeric(merged[transport_score_col], errors="coerce")
        .fillna(0)
        .clip(0, 10)
    )

    return merged, missing_transport_score_count

# convert park area into a 0-10 score based on size thresholds
def calculate_area_score(ha: Any) -> int:
    """Convert park area into a 0-10 size score."""
    area = pd.to_numeric(pd.Series([ha]), errors="coerce").iloc[0]
    if pd.isna(area):
        return 0
    if area < 0.5:
        return 2
    if area < 2:
        return 4
    if area < 5:
        return 6
    if area < 10:
        return 8
    return 10

# convert park suitability score into a 0-10 task richness score
def calculate_richness_score(row: pd.Series) -> float:
    """Use park_suitability_score as the task richness score."""
    score = row[park_suitability_score_col] * 10
    return float(pd.Series([score]).clip(0, 10).iloc[0])

# Use the area score, task richness score, and transport score to generate weather resilience score
def calculate_weather_acceptance_score(row: pd.Series) -> float:
    """Combine richness, area, and transport into one weather resilience score."""
    score = (
        0.45 * row["task_richness_score"]
        + 0.30 * row["park_ha_level"]
        + 0.25 * row[transport_score_col]
    )
    return round(float(max(0, min(score, 10))), 2)

# Reverse the park score into the minimum weather score needed
def calculate_min_weather_accept_level(weather_acceptance_score: float) -> float:
    """Reverse the park score into the minimum weather score needed."""
    min_level = 10 - weather_acceptance_score * 0.5
    return round(float(max(5, min(min_level, 10))), 2)

# Generate a short explanation for the final recommendation text based on the weather acceptance score
def generate_weather_related_explanation(weather_acceptance_score: float) -> str:
    """Create a short explanation for the final recommendation text."""
    if weather_acceptance_score >= 7.5:
        return (
            "This park has strong weather tolerance because it combines rich "
            "activities, suitable size, and accessible transport."
        )
    if weather_acceptance_score >= 5:
        return (
            "This park is suitable for good weather conditions and may still "
            "work for short outdoor visits."
        )
    return (
        "This park is best recommended only under ideal weather because its "
        "size, activity richness, or transport access is limited."
    )

# Combine the weather explanation and feature summary into final recommendation description 
def build_recommend_description(df: pd.DataFrame) -> pd.Series:
    """Combine weather explanation and feature summary."""
    weather_text = df["weather_related_explanation"].fillna("")
    feature_text = df.get("feature_summary", pd.Series("", index=df.index)).fillna("")
    return (weather_text + " " + feature_text).str.strip()

# Build the final park table with all calculated fields and selected columns
def build_park_table(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate weather acceptance fields and output final park_table columns."""
    results = df.copy()

    if area_ha_col not in results.columns:
        results[area_ha_col] = pd.NA

    results["park_ha_level"] = results[area_ha_col].apply(calculate_area_score)
    results["task_richness_score"] = results.apply(calculate_richness_score, axis=1)
    results["weather_acceptance_score"] = results.apply(
        calculate_weather_acceptance_score,
        axis=1,
    )
    results["min_weather_accept_level"] = results["weather_acceptance_score"].apply(
        calculate_min_weather_accept_level
    )
    results["weather_related_explanation"] = results["weather_acceptance_score"].apply(
        generate_weather_related_explanation
    )

    park_table = pd.DataFrame(
        {
            "park_id": results["park_id"].astype(int),
            "park_name": results["park_name"].fillna(""),
            "description": results["description"].fillna(""),
            "latitude": pd.to_numeric(results["latitude"], errors="coerce").round(7),
            "longitude": pd.to_numeric(results["longitude"], errors="coerce").round(7),
            "st_point": results["st_point"],
            "min_weather_accept_level": results["min_weather_accept_level"].round(2),
            "transport_accessibility_score": results[transport_score_col].round(2),
            "task_richness_score": results["task_richness_score"].round(2),
            "park_ha_level": results["park_ha_level"].round(4),
            "recommend_description": build_recommend_description(results),
        }
    )

    return park_table


def export_results(park_table: pd.DataFrame) -> None:
    park_table.to_csv(output_path, index=False, encoding="utf-8-sig")


def main() -> None:
    parks, transport = load_data()
    merged, missing_transport_score_count = merge_transport_score(parks, transport)
    park_table = build_park_table(merged)
    export_results(park_table)

    print(f"Output file: {output_path}")
    print(f"Total parks: {len(park_table)}")
    print("min_weather_accept_level distribution:")
    print(park_table["min_weather_accept_level"].value_counts().sort_index().to_string())
    print(f"Missing transport_accessibility_score count: {missing_transport_score_count}")


if __name__ == "__main__":
    main()
