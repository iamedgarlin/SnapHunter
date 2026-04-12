import pandas as pd
import geopandas as gpd
from pathlib import Path

# Target columns for task dataframe
final_columns = [
    "series_id",
    "task_name",
    "task_description",
    "evaluation_criteria",
    "environment_type",
    "task_type",
    "location_label",
    "latitude",
    "longitude",
    "st_point",
    "geofence_radius_meter",
    "base_difficulty",
    "reward_point",
    "is_active",
]

# Split "Co-ordinates" column into "latitude" and "longitude"
def split_coordinates(df: pd.DataFrame, coord_col: str = "Co-ordinates") -> pd.DataFrame:
    out = df.copy()
    parts = out[coord_col].astype(str).str.split(",", n=1, expand=True)
    out["latitude"] = pd.to_numeric(parts[0].str.strip(), errors="coerce")
    out["longitude"] = pd.to_numeric(parts[1].str.strip(), errors="coerce")
    return out

# Add suburb location label by spatial join with locality shapefile
def add_suburb_location_label(task_df: pd.DataFrame, locality_shp_path: str | Path) -> pd.DataFrame:
    if task_df.empty:
        out = task_df.copy()
        out["location_label"] = pd.NA
        return out

    suburbs = gpd.read_file(locality_shp_path)[["LOCALITY", "geometry"]]
    points = gpd.GeoDataFrame(
        task_df.copy(),
        geometry=gpd.points_from_xy(task_df["longitude"], task_df["latitude"]),
        crs="EPSG:4326",
    ).to_crs(suburbs.crs)

    joined = gpd.sjoin(points, suburbs, how="left", predicate="within")
    joined["location_label"] = joined["LOCALITY"]
    print(f"[Artworks suburb match] matched {joined['location_label'].notna().sum()}/{len(joined)} rows")

    return pd.DataFrame(joined.drop(columns=["geometry", "index_right", "LOCALITY"]))


def build_artwork_task(row: pd.Series) -> pd.Series:
    task_name = str(row["task_name"]).strip()
    structure = str(row["structure"]).strip() if pd.notna(row["structure"]) else ""
    asset_type = str(row["asset_type"]).strip() if pd.notna(row["asset_type"]) else "artwork"
    artist = str(row["artist"]).strip() if pd.notna(row["artist"]) else ""

    structure_or_type = structure if structure else asset_type
    artist_hint = f" Artist hint: {artist}." if artist else ""

    task_description = (
        f"Take a picture of {task_name}. Try to capture its {structure_or_type.lower()} characteristics."
    )
    evaluation_criteria = (
        f"The photo should be of the artwork '{task_name}', and it should look like a {structure_or_type}. "
        f"Use this as a soft check, not an overly strict one.{artist_hint}"
    )

    return pd.Series(
        {
            "task_description": task_description,
            "evaluation_criteria": evaluation_criteria,
        }
    )

# Clean artworks tasks from raw CSV
def clean_artworks_tasks(
    artworks_path: str | Path,
    locality_shp_path: str | Path,
    output_path: str | Path = "tasks_ready_artworks.csv",
) -> pd.DataFrame:
    artworks_df = pd.read_csv(artworks_path)
    print(f"[Load artworks] rows={len(artworks_df)}")

    artworks_df = artworks_df.drop_duplicates(subset=["Name", "Mel way Ref"]).copy()
    artworks_df["series_id"] = 3
    artworks_df = split_coordinates(artworks_df)

    task_df = pd.DataFrame(
        {
            "series_id": artworks_df["series_id"],
            "task_name": artworks_df["Name"],
            "task_description": pd.NA,
            "evaluation_criteria": pd.NA,
            "environment_type": "outdoor",
            "task_type": "photo",
            "location_label": pd.NA,
            "latitude": pd.to_numeric(artworks_df["latitude"], errors="coerce"),
            "longitude": pd.to_numeric(artworks_df["longitude"], errors="coerce"),
            "st_point": pd.NA,
            "geofence_radius_meter": 50,
            "base_difficulty": 1,
            "reward_point": 10,
            "is_active": 1,
            "asset_type": artworks_df["Asset Type"],
            "structure": artworks_df["Structure"],
            "artist": artworks_df["Artist"],
        }
    )

    task_df = task_df.dropna(subset=["series_id", "task_name", "latitude", "longitude"])

    task_df = add_suburb_location_label(task_df, locality_shp_path)

    task_text = task_df.apply(build_artwork_task, axis=1)
    task_df["task_description"] = task_text["task_description"]
    task_df["evaluation_criteria"] = task_text["evaluation_criteria"]
    task_df["st_point"] = task_df.apply(lambda r: f"POINT({r['longitude']} {r['latitude']})", axis=1)

    task_df["series_id"] = task_df["series_id"].astype(int)
    task_df = task_df[final_columns]

    task_df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"[Done artworks] rows={len(task_df)} output={output_path}")
    return task_df


if __name__ == "__main__":
    clean_artworks_tasks(
        artworks_path="public-artworks-fountains-and-monuments.csv",
        locality_shp_path="victoria/VMADMIN/LOCALITY_POLYGON.shp",
        output_path="tasks_ready_artworks.csv",
    )
