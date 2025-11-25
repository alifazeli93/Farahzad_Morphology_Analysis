import geopandas as gpd
import numpy as np
from shapely.geometry import Polygon
import os
import sys
from pathlib import Path

# --- Setup and Data Loading ---
print("--- Starting 02_shape_orientation.py ---")
current_script_path = Path(__file__).resolve()
project_root = current_script_path.parent.parent

INPUT_PATH = project_root / 'data' / 'processed' / 'parcels_metrics_midterm.gpkg'
OUTPUT_PATH = project_root / 'data' / 'processed' / 'parcels_metrics_final.gpkg'

# --- CRITICAL PATH CHECK ---
if not INPUT_PATH.exists():
    print(f"ERROR: Input file not found at {INPUT_PATH}")
    print("Please run 01_geometry_metrics.py first.")
    sys.exit()

try:
    # Load the mid-term data which includes area and perimeter
    gdf = gpd.read_file(INPUT_PATH)
    initial_count = len(gdf)
    print(f"Data loaded successfully. Parcel count: {initial_count}")
    print("-" * 60)

except Exception as e:
    print(f"ERROR reading GeoPackage file: {e}")
    sys.exit()


# --- 1. Calculating Rectangularity and Orientation ---

def calculate_shape_metrics(geometry):
    """
    Calculates Rectangularity Index and Main Axis Orientation for a single polygon.
    The method uses the Minimum Rotated Bounding Box (MRBB).
    """
    if geometry is None or not geometry.is_valid or geometry.is_empty:
        return 0, np.nan

    # 1. Get Minimum Rotated Bounding Box (MRBB)
    # The MRBB is the smallest rectangle that can enclose the geometry,
    # rotated at any angle.
    try:
        # For MultiPolygons, use the convex hull to calculate the bounding box.
        if geometry.geom_type == 'MultiPolygon':
            min_rect = geometry.convex_hull.minimum_rotated_rectangle
        else:
            min_rect = geometry.minimum_rotated_rectangle
    except:
        return 0, np.nan

    if not min_rect or not isinstance(min_rect, Polygon):
        return 0, np.nan

    # 2. Rectangularity Index (Area Ratio)
    # Rectangularity = (Area of Parcel) / (Area of MRBB)
    # This metric ranges from 0 (very irregular) to 1 (perfect rectangle/square).
    rect_area = min_rect.area
    if rect_area > 0:
        rectangularity_idx = geometry.area / rect_area
    else:
        rectangularity_idx = 0

    # 3. Main Axis Orientation
    # Extract coordinates of the MRBB to find the longer edge
    coords = list(min_rect.exterior.coords)
    # The first 4 points define the rectangle
    p1, p2, p3, p4 = np.array(coords[:4])

    # Calculate the squared length of two adjacent sides
    len_sq_ab = np.sum((p2 - p1) ** 2)
    len_sq_bc = np.sum((p3 - p2) ** 2)

    # Identify the longer side (main axis)
    if len_sq_ab >= len_sq_bc:
        main_axis_vector = p2 - p1
    else:
        main_axis_vector = p3 - p2

    # Calculate the angle of the main axis relative to the X-axis (East direction)
    angle_rad = np.arctan2(main_axis_vector[1], main_axis_vector[0])
    angle_deg = np.degrees(angle_rad)

    # Convert angle to 0-180 degrees relative to North (Y-axis)
    # 90 degrees is East, 0 is North. We want 0-180, where 0 is North and 90 is East/West alignment.
    orientation_angle = (90 - angle_deg) % 180
    # Ensure the angle is 0 to 180 degrees
    if orientation_angle > 90:
        orientation_angle = 180 - orientation_angle

    return rectangularity_idx, orientation_angle


print("2. Calculating Rectangularity Index and Orientation Angle...")
# Apply the function to all geometries
results = gdf.geometry.apply(calculate_shape_metrics)

# Extract results into new columns
# .tolist() converts the Series of tuples into a list of tuples
# and zip(*) unpacks it into two separate lists for the columns
if not results.empty:
    rectangularity_list, orientation_list = zip(*results.tolist())
    gdf['rectangularity_idx'] = rectangularity_list
    gdf['orientation_angle'] = orientation_list
    print("SUCCESS: Shape and Orientation metrics calculated.")
else:
    print("WARNING: No valid geometries found for shape analysis.")

print("-" * 60)

# --- 2.5. Final Cleaning of NaN results (Robustness) ---
# Filter out any parcels that failed the shape analysis (MRBB failed)
initial_count_2 = len(gdf)
gdf.dropna(subset=['rectangularity_idx', 'orientation_angle'], inplace=True)
final_count_2 = len(gdf)
print(f"Dropped {initial_count_2 - final_count_2} parcels due to geometry failure in shape analysis.")
print(f"Final valid parcel count after shape analysis: {final_count_2}")
print("-" * 60)

# --- Check Results ---
print("\n[Metric Check (Head)]")
print(gdf[['area_m2', 'perimeter_m', 'compactness_idx', 'rectangularity_idx', 'orientation_angle']].head())
print("-" * 60)

# --- 3. Saving Final Results ---
gdf.to_file(OUTPUT_PATH, driver="GPKG")
print(f"Final results saved to: {OUTPUT_PATH}")
print("Process finished successfully.")