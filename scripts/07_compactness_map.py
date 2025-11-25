import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
from pathlib import Path

# --- Setup Paths ---
print("--- Starting 07_compactness_map.py (Compactness Distribution Map) ---")
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


# --- 1. Creating Compactness Distribution Map ---

def create_compactness_map(gdf, output_path):
    """Generates a map showing the spatial distribution of the Polsby-Popper Compactness Index."""

    # 1. Plotting
    fig, ax = plt.subplots(1, 1, figsize=(15, 15))

    # Use 'plasma' or 'magma' colormap for sequential data.
    # Higher compactness (close to 1.0, means more regular/circular) should be darker.
    # 'viridis' is a good default sequential colormap.
    gdf.plot(column='compactness_idx', ax=ax, cmap='viridis_r', linewidth=0.5, edgecolor='0.8',
             legend=True, vmin=0, vmax=1.0,
             legend_kwds={'label': "Compactness Index (0.0 to 1.0)", 'orientation': "vertical"})

    ax.set_title("Spatial Distribution of Compactness Index (Farahzad)", fontsize=18)
    ax.set_axis_off()  # Hide axes

    # 2. Save the map
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Compactness Distribution Map saved to: {output_path}")


print("1. Generating Compactness Distribution Map...")
create_compactness_map(gdf, OUTPUT_DIR / '05_compactness_map.png')
print("-" * 60)
print("SUCCESS: Compactness Distribution Map created. Check the 'results' folder!")