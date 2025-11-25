import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
from pathlib import Path

# --- Setup Paths ---
print("--- Starting 06_area_distribution_map.py (Area Distribution Map) ---")
current_script_path = Path(__file__).resolve()
project_root = current_script_path.parent.parent

# Load the final clustered data
INPUT_PATH = project_root / 'data' / 'processed' / 'parcels_final_clustered.gpkg'
OUTPUT_DIR = project_root / 'results'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Load Data ---
try:
    gdf = gpd.read_file(INPUT_PATH)
    print(f"Data loaded successfully. Parcel count: {len(gdf)}")
    print("-" * 60)
except Exception as e:
    print(f"FATAL ERROR: Could not load data. {e}")
    sys.exit()


# --- 1. Creating Area Distribution Map ---

def create_area_distribution_map(gdf, output_path):
    """Generates a map showing the spatial distribution of parcel areas."""

    # 1. Apply Log transformation to area for better visualization of scale differences
    # Add a small value (+1) to avoid log(0) if any area is exactly zero.
    gdf['log_area_m2'] = np.log10(gdf['area_m2'] + 1)

    # 2. Plotting
    fig, ax = plt.subplots(1, 1, figsize=(15, 15))

    # Use a sequential colormap (e.g., 'viridis', 'plasma', 'magma') for area
    # 'viridis_r' is reversed viridis, so smaller areas are yellow/green and larger are dark blue.
    gdf.plot(column='log_area_m2', ax=ax, cmap='viridis_r', linewidth=0.5, edgecolor='0.8',
             legend=True, legend_kwds={'label': "Log10(Area in m²)", 'orientation': "vertical"})

    ax.set_title("Spatial Distribution of Parcel Area (Farahzad)", fontsize=20)
    ax.set_axis_off()  # Hide axes

    # 3. Save the map
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Area Distribution Map saved to: {output_path}")


print("1. Generating Area Distribution Map...")
create_area_distribution_map(gdf, OUTPUT_DIR / '04_area_distribution_map.png')
print("-" * 60)
print("SUCCESS: Area Distribution Map created. Check the 'results' folder!")