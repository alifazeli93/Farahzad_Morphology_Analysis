import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import os
import sys
from pathlib import Path

# --- Setup Paths ---
print("--- Starting 04_visualization.py (Mapping & Rose Diagram) ---")
current_script_path = Path(__file__).resolve()
project_root = current_script_path.parent.parent

INPUT_PATH = project_root / 'data' / 'processed' / 'parcels_final_clustered.gpkg'
OUTPUT_DIR = project_root / 'results'
os.makedirs(OUTPUT_DIR, exist_ok=True)  # Ensure results folder exists

# --- Load Data ---
try:
    gdf = gpd.read_file(INPUT_PATH)
    print(f"Clustered data loaded successfully. Parcel count: {len(gdf)}")
    print("-" * 60)
except Exception as e:
    print(f"FATAL ERROR: Could not load clustered data. {e}")
    sys.exit()


# --- 1. Morphological Cluster Map ---

def create_cluster_map(gdf, output_path):
    """Generates a map showing the spatial distribution of the K-Means clusters."""

    # 1. Define colors for the 4 clusters
    cmap = colors.ListedColormap(['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])  # Distinct colors for 4 clusters

    # Ensure the cluster column is numeric for plotting
    gdf['morpho_cluster'] = pd.to_numeric(gdf['morpho_cluster'])

    # 2. Plotting
    fig, ax = plt.subplots(1, 1, figsize=(15, 15))

    # Plotting based on the 'morpho_cluster' column
    gdf.plot(column='morpho_cluster', ax=ax, cmap=cmap, linewidth=0.5, edgecolor='0.8', legend=True,
             categories=gdf['morpho_cluster'].unique().tolist())

    # Customizing the legend title
    legend = ax.get_legend()
    if legend:
        legend.set_title("Morphological Cluster")

    ax.set_title("Spatial Distribution of Morphological Clusters (Farahzad)", fontsize=18)
    ax.set_axis_off()

    # 3. Save the map
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Cluster Map saved to: {output_path}")


print("1. Generating Morphological Cluster Map...")
create_cluster_map(gdf, OUTPUT_DIR / '01_morphological_cluster_map.png')
print("-" * 60)


# --- 2. Rose Diagram (Kolersky Diagram) ---

def create_rose_diagram(gdf, output_path):
    """Generates a Rose Diagram for the Main Axis Orientation (0 to 90 degrees)."""

    # We only care about the orientation angle
    angles = gdf['orientation_angle'].dropna().values

    # Angles are 0 to 90, representing the main axis direction
    # We use 18 bins for a 5-degree interval (90 / 5 = 18)
    bins = np.arange(0, 95, 5)

    # 1. Create the plot
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': 'polar'})

    # 2. Convert angles to radians and plot histogram
    # Since Rose Diagram is 360, we need to map our 0-90 angles to a full circle display
    # to show both N-S and E-W alignment directions.
    # We map 0-90 to 0-180 and repeat the data to make it symmetric.
    angles_radians = np.deg2rad(angles * 2)

    # Plotting the histogram
    N, bins_polar = np.histogram(angles, bins=bins)

    # Correcting the polar axis (0-90 degrees displayed as 0-360)
    ax.set_theta_zero_location("N")  # Set North (0 degrees) at the top
    ax.set_theta_direction(-1)  # Clockwise direction
    ax.bar(np.deg2rad(bins_polar[:-1]), N, width=np.deg2rad(np.diff(bins_polar)), bottom=0.0, color='red', alpha=0.7)

    # Customizing the angle labels (0 to 90 degrees)
    ax.set_xticks(np.deg2rad(np.arange(0, 180, 45)))
    ax.set_xticklabels(['0° (N/S)', '45°', '90° (E/W)', '45°'])

    ax.set_title("Rose Diagram of Parcel Orientation (Farahzad)", va='bottom', fontsize=16)

    # 3. Save the diagram
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Rose Diagram saved to: {output_path}")


print("2. Generating Rose Diagram for Orientation...")
create_rose_diagram(gdf, OUTPUT_DIR / '02_rose_diagram_orientation.png')
print("-" * 60)
print("SUCCESS: All visualizations created. Check the 'results' folder!")