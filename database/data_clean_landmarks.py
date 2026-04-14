import pandas as pd
import geopandas as gpd
from pathlib import Path

# mapping sub-theme 
series_id_map = {
    "Nature": 1,
    "Urban": 2,
    "Art": 3,
}

# mapping sub-theme to theme for landmarks dataset
subtheme_mapping = {
    # Nature
    "Informal Outdoor Facility (Park/Garden/Reserve)": "Nature",
    "Outdoor Recreation Facility (Zoo, Golf Course)": "Nature",
    "Marina": "Nature",
    "Aquarium": "Nature",
    # Urban
    "Railway Station": "Urban",
    "Transport Terminal": "Urban",
    "Bridge": "Urban",
    "Observation Tower/Wheel": "Urban",
    "Public Buildings": "Urban",
    "Library": "Urban",
    "Major Sports & Recreation Facility": "Urban",
    "Function/Conference/Exhibition Centre": "Urban",
    # Art
    "Art Gallery/Museum": "Art",
    "Theatre Live": "Art",
    "Visitor Centre": "Art",
    "Sculpture": "Art",
    "Fountain": "Art",
    "Monument": "Art",
    "Mural": "Art",
    "Artwork": "Art",
    "Memorial": "Art",
    "Installation": "Art",
}

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
    print(f"[Landmarks suburb match] matched {joined['location_label'].notna().sum()}/{len(joined)} rows")

    return pd.DataFrame(joined.drop(columns=["geometry", "index_right", "LOCALITY"]))

# Build task description and evaluation criteria based on theme and sub-theme
def build_landmark_task(row: pd.Series) -> pd.Series:
    task_name = str(row["task_name"]).strip()
    theme = str(row["theme"]).strip() if pd.notna(row["theme"]) else ""
    sub_theme = str(row["sub_theme"]).strip() if pd.notna(row["sub_theme"]) else "place"

    if theme == "Nature":
        task_description = f"Take a picture of plant in {task_name}."
        evaluation_criteria = (
            "The photo should show at least one plant (for example trees, flowers, grass, or shrubs). "
            "Use this as a soft check, the image can still pass if the framing is casual."
        )
    elif theme == "Urban":
        task_description = f"Take a picture of building which represents {task_name}."
        evaluation_criteria = (
            f"The photo should include a built structure that matches {sub_theme}. "
            "Use this as a soft check, the image can still pass if the framing is casual."
        )
    else:
        task_description = f"Take a picture of {task_name} related to {sub_theme}."
        evaluation_criteria = (
            f"The photo should show an art or cultural place that fits {sub_theme}. "
            "Use this as a soft check, the image can still pass if the framing is casual."
        )

    return pd.Series(
        {
            "task_description": task_description,
            "evaluation_criteria": evaluation_criteria,
        }
    )

# clean landmarks tasks from raw CSV
def clean_landmarks_tasks(
    landmarks_path: str | Path,
    locality_shp_path: str | Path,
    output_path: str | Path = "tasks_ready_landmarks.csv",
) -> pd.DataFrame:
    landmarks_df = pd.read_csv(landmarks_path)
    print(f"[Load landmarks] rows={len(landmarks_df)}")

    landmarks_df = landmarks_df.drop_duplicates(subset=["Feature Name"]).copy()
    landmarks_df["series_id"] = landmarks_df["Sub Theme"].map(subtheme_mapping)
    landmarks_df = landmarks_df.dropna(subset=["series_id"])
    landmarks_df["series_id"] = landmarks_df["series_id"].map(series_id_map)

    landmarks_df = split_coordinates(landmarks_df)

    task_df = pd.DataFrame(
        {
            "series_id": landmarks_df["series_id"],
            "task_name": landmarks_df["Feature Name"],
            "task_description": pd.NA,
            "evaluation_criteria": pd.NA,
            "environment_type": "outdoor",
            "task_type": "photo",
            "location_label": pd.NA,
            "latitude": pd.to_numeric(landmarks_df["latitude"], errors="coerce"),
            "longitude": pd.to_numeric(landmarks_df["longitude"], errors="coerce"),
            "st_point": pd.NA,
            "geofence_radius_meter": 50,
            "base_difficulty": 1,
            "reward_point": 10,
            "is_active": 1,
            "theme": landmarks_df["series_id"].map({1: "Nature", 2: "Urban", 3: "Art"}),
            "sub_theme": landmarks_df["Sub Theme"],
        }
    )

    task_df = task_df.dropna(subset=["series_id", "task_name", "latitude", "longitude"])

    task_df = add_suburb_location_label(task_df, locality_shp_path)

    task_text = task_df.apply(build_landmark_task, axis=1)
    task_df["task_description"] = task_text["task_description"]
    task_df["evaluation_criteria"] = task_text["evaluation_criteria"]
    task_df["st_point"] = task_df.apply(lambda r: f"POINT({r['longitude']} {r['latitude']})", axis=1)

    task_df["series_id"] = task_df["series_id"].astype(int)
    task_df = task_df[final_columns]

    task_df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"[Done landmarks] rows={len(task_df)} output={output_path}")
    return task_df


if __name__ == "__main__":
    clean_landmarks_tasks(
        landmarks_path="landmarks-and-places-of-interest-including-schools-theatres-health-services-spor.csv",
        locality_shp_path="victoria/VMADMIN/LOCALITY_POLYGON.shp",
        output_path="tasks_ready_landmarks.csv",
    )
