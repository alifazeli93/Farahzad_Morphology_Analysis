import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import box
# Import make_valid for geometry repair
from shapely.validation import make_valid
import os
import sys
from pathlib import Path

# --- Setup Paths ---
print("--- Starting 10_parcel_density_analysis.py (Parcel Density Analysis) ---")
# 1. Define Root Path based on script location
current_script_path = Path(__file__).resolve()
project_root = current_script_path.parent.parent

# 2. Define Input/Output Paths
# Loads the final clustered data
INPUT_PATH = project_root / 'data' / 'processed' / 'parcels_final_clustered.gpkg'
OUTPUT_DIR = project_root / 'results'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Parameters ---
GRID_CELL_SIZE = 50  # 50 meters x 50 meters grid cell size
# Buffer to ensure large parcels and boundaries are fully covered by the grid
BUFFER_DISTANCE = 100

# --- Load Data ---
try:
    gdf = gpd.read_file(INPUT_PATH)
    CRS = gdf.crs
    print(f"Data loaded successfully. CRS: {CRS.name}. Parcel count: {len(gdf)}")
    print("-" * 60)
except Exception as e:
    # Handles "INPUT_PATH is not defined" error if paths setup failed previously
    print(f"FATAL ERROR: Could not load data. Ensure INPUT_PATH is defined correctly. {e}")
    sys.exit()

# --- 1. Geometry Validation and Repair ---
print("Validating and repairing parcel geometries...")
invalid_count = (~gdf.is_valid).sum()
if invalid_count > 0:
    # Use make_valid to repair invalid geometries (crucial for accurate intersection)
    gdf['geometry'] = gdf.geometry.apply(lambda geom: make_valid(geom) if not geom.is_valid else geom)
    print(f"Repaired {invalid_count} invalid geometries.")
else:
    print("All parcel geometries are valid.")
print("-" * 60)


# --- 2. Create Fishnet Grid (The Contextual Framework) ---

def create_fishnet(gdf, cell_size, buffer_distance):
    """Creates a regular grid covering the *buffered* extent."""

    xmin, ymin, xmax, ymax = gdf.total_bounds

    # Apply buffer to ensure full boundary coverage
    xmin_buf = xmin - buffer_distance
    ymin_buf = ymin - buffer_distance
    xmax_buf = xmax + buffer_distance
    ymax_buf = ymax + buffer_distance

    # Calculate grid boundaries
    rows = int(np.ceil((ymax_buf - ymin_buf) / cell_size))
    cols = int(np.ceil((xmax_buf - xmin_buf) / cell_size))

    X = np.linspace(xmin_buf, xmax_buf, cols + 1)
    Y = np.linspace(ymin_buf, ymax_buf, rows + 1)

    polygons = []

    for i in range(cols):
        for j in range(rows):
            polygons.append(box(X[i], Y[j], X[i + 1], Y[j + 1]))

    grid = gpd.GeoDataFrame({'geometry': polygons}, crs=gdf.crs)
    grid['grid_id'] = range(len(grid))

    print(f"Fishnet created: {len(grid)} cells of {cell_size}m x {cell_size}m (Buffered).")
    return grid


grid_gdf = create_fishnet(gdf, GRID_CELL_SIZE, BUFFER_DISTANCE)

# --- 3. Spatial Join and Aggregation (Counting Density - Robust Polygon Intersects) ---

# Use 'inner' join and 'intersects' predicate to count all parcels that touch a grid cell.
# This ensures even large parcels that partially cover multiple cells are counted.
joined = gpd.sjoin(gdf, grid_gdf, how="inner", predicate="intersects")

# Count the number of UNIQUE parcel intersections per grid cell
density_counts = joined.groupby('index_right').size().reset_index(name='parcel_count')

# Rename the column for merging
density_counts.rename(columns={'index_right': 'grid_id'}, inplace=True)

# Merge the counts back into the original grid GeoDataFrame
grid_final = grid_gdf.merge(density_counts, on='grid_id', how='left')
# Fill NaN (cells with no parcels) with 0
grid_final['parcel_count'] = grid_final['parcel_count'].fillna(0)

print(f"Density calculation complete. Max parcels in a cell: {grid_final['parcel_count'].max()}")
print("-" * 60)


# --- 4. Visualization (Density Heatmap) ---

def create_density_map(grid_gdf, gdf_original, output_path):
    """Generates a thematic map of parcel density per grid cell."""

    fig, ax = plt.subplots(1, 1, figsize=(15, 15))

    VMAX_FIXED = 50

    # Plot only cells with parcels (count > 0)
    plot_data = grid_gdf[grid_gdf['parcel_count'] > 0]

    plot_data.plot(
        column='parcel_count',
        ax=ax,
        cmap='Reds',  # Lighter colors for low density, darker red for high density.
        linewidth=0,
        edgecolor='none',
        legend=True,
        vmax=VMAX_FIXED,
        legend_kwds={
            'label': f"Parcel Count (Density per {GRID_CELL_SIZE}m cell)",
            'orientation': "vertical",
            'shrink': 0.7,
            'aspect': 25
        }
    )

    # Plot the original study area boundary for context (using facecolor='none')
    gdf_original.plot(ax=ax, linewidth=0.4, edgecolor='gray', facecolor='none', alpha=0.7)

    ax.set_title(f"Parcel Density (Granularity Texture) Map - Farahzad ({GRID_CELL_SIZE}m Grid)", fontsize=18)
    ax.set_axis_off()

    # Save the map
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Density Map saved to: {output_path}")

print("Generating Parcel Density Map...")
create_density_map(grid_final, gdf, OUTPUT_DIR / '08_parcel_density_map.png')
print("-" * 60)
print("SUCCESS: Contextual Density analysis complete. Check the 'results' folder!")



# --- 4. Saving Final Grid Results ---
print("4. Saving Final Grid Results...")
GRID_OUTPUT_PATH = project_root / 'data' / 'processed' / 'density_grid_final.gpkg'
try:
    # Ensure only essential columns are saved (geometry, grid_id, parcel_count)
    grid_final[['geometry', 'grid_id', 'parcel_count']].to_file(GRID_OUTPUT_PATH, driver="GPKG")
    print(f"SUCCESS: Density Grid data saved to: {GRID_OUTPUT_PATH}")
except Exception as e:
    print(f"ERROR: Could not save the density grid. {e}")
print("-" * 60)
