import geopandas as gpd
import numpy as np
import os
import sys
from pathlib import Path

# --- 1. Setup and Data Loading ---
current_script_path = Path(__file__).resolve()
project_root = current_script_path.parent.parent

INPUT_PATH = project_root / 'data' / 'processed' / 'parcels_utm.gpkg'
OUTPUT_PATH = project_root / 'data' / 'processed' / 'parcels_metrics_midterm.gpkg'

# --- CRITICAL PATH CHECK ---
# ... (Path check code remains the same) ...

try:
    gdf = gpd.read_file(INPUT_PATH)
    print("SUCCESS: UTM data loaded for Phase 1.")
    initial_count = len(gdf)
    print(f"Initial parcel count: {initial_count}")
    print("-" * 60)

except Exception as e:
    print(f"ERROR reading GeoPackage file: {e}")
    sys.exit()


# --- 1.5. Final Geometry Cleanup (Minimal Filter) ---
print("1.5. Final Geometry Cleaning (Minimal Filter)...")

# Remove non-polygon types and null geometries
gdf.dropna(subset=['geometry'], inplace=True)
valid_types = ['Polygon', 'MultiPolygon']
gdf = gdf[gdf.geometry.geom_type.isin(valid_types)]
gdf = gdf[~gdf.is_empty]
print(f"Remaining parcels after initial filter: {len(gdf)}")
print("-" * 60)


# --- 2. Calculate Basic Metrics: Area and Perimeter (Grain Size) ---
print("2. Calculating Area and Perimeter...")

# ACTION: USE AREA CALCULATED IN ARCMAP TO BYPASS GEOS ERROR
# CHANGE 'AREA_TEST' to whatever your field name is in ArcMap
try:
    gdf['area_m2'] = gdf['AREA_TEST']
    print("SUCCESS: Area data loaded from GIS attribute table.")
except KeyError:
    print("ERROR: 'AREA_TEST' field not found. Calculating Area with Python (may result in NaNs).")
    gdf['area_m2'] = gdf.geometry.area

# Calculate Perimeter (Still uses Shapely/GEOS, expecting some NaNs)
gdf['perimeter_m'] = gdf.geometry.length


# --- 3. Calculate Compactness (Polsby-Popper Index) ---
print("3. Calculating Compactness (Polsby-Popper)...")

# Handle division by zero:
gdf['compactness_idx'] = np.where(
    gdf['perimeter_m'] > 0,
    (4 * np.pi * gdf['area_m2']) / (gdf['perimeter_m'] ** 2),
    0
)

# --- 3.5. Final Cleaning of NaN results (CRITICAL STEP) ---
print("3.5. Filtering out NaN geometries...")

# Drop rows where perimeter is NaN (these are the structurally broken ones)
initial_count_after_filter = len(gdf)
gdf.dropna(subset=['perimeter_m'], inplace=True)

# Drop rows where area is near zero (slivers/broken geometry)
gdf = gdf[gdf['area_m2'] > 0.01]

final_count_after_filter = len(gdf)
print(f"Dropped {initial_count_after_filter - final_count_after_filter} structurally invalid parcels.")
print(f"Final valid parcel count: {final_count_after_filter}")
print("-" * 60)


# --- Check Results ---
print("\n[Metric Check (Head)]")
print(gdf[['area_m2', 'perimeter_m', 'compactness_idx']].head())
print("-" * 60)

# --- 4. Saving Mid-term Results ---
gdf.to_file(OUTPUT_PATH, driver="GPKG")
print(f"Mid-term results saved to: {OUTPUT_PATH}")
print("Ready for next steps: Rectangularity and Orientation.")