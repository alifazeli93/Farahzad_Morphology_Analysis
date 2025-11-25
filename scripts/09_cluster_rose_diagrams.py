import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
from pathlib import Path

# --- Setup Paths ---
print("--- Starting 09_cluster_rose_diagrams.py (Orientation by Cluster) ---")
current_script_path = Path(__file__).resolve()
project_root = current_script_path.parent.parent

# Load the final clustered data
INPUT_PATH = project_root / 'data' / 'processed' / 'parcels_final_clustered.gpkg'
OUTPUT_DIR = project_root / 'results'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Load Data ---
try:
    gdf = gpd.read_file(INPUT_PATH)
    print(f"Clustered data loaded. Parcel count: {len(gdf)}")

    # Ensure cluster column is numeric
    gdf['morpho_cluster'] = pd.to_numeric(gdf['morpho_cluster'], errors='coerce')
    gdf.dropna(subset=['orientation_angle', 'morpho_cluster'], inplace=True)

    # Identify unique clusters
    unique_clusters = sorted(gdf['morpho_cluster'].unique())
    N_CLUSTERS = len(unique_clusters)
    print(f"Found {N_CLUSTERS} clusters for analysis: {unique_clusters}")
    print("-" * 60)

except Exception as e:
    print(f"FATAL ERROR: Could not load data. {e}")
    sys.exit()


# --- 1. Generating Rose Diagrams for Each Cluster ---

def create_multi_rose_diagram(gdf, clusters, output_path):
    """Generates four Rose Diagrams (one for each cluster) in a single figure."""

    # Setup the figure (2 rows, 2 columns)
    fig, axes = plt.subplots(2, 2, figsize=(16, 16),
                             subplot_kw={'projection': 'polar'})
    axes = axes.flatten()  # Flatten the 2x2 grid into a 1D array for easy iteration

    bins = np.arange(0, 95, 5)  # 5-degree interval bins

    print("Generating Rose Diagrams...")

    # Iterate through each cluster (0, 1, 2, 3)
    for i, cluster_id in enumerate(clusters):
        # Filter data for the current cluster
        cluster_data = gdf[gdf['morpho_cluster'] == cluster_id]
        angles = cluster_data['orientation_angle'].values

        # Calculate histogram (frequency)
        N, bins_polar = np.histogram(angles, bins=bins)

        # Set polar plot settings
        ax = axes[i]
        ax.set_theta_zero_location("N")  # 0 degrees (North) at the top
        ax.set_theta_direction(-1)  # Clockwise direction

        # Plot the bars
        ax.bar(np.deg2rad(bins_polar[:-1]), N,
               width=np.deg2rad(np.diff(bins_polar)), bottom=0.0,
               color='darkred', alpha=0.7, edgecolor='black', linewidth=0.5)

        # Customize the angle labels (0 to 90 degrees)
        ax.set_xticks(np.deg2rad(np.arange(0, 180, 45)))
        ax.set_xticklabels(['0° (N/S)', '45°', '90° (E/W)', '45°'])

        # Set Title
        ax.set_title(f"Cluster {cluster_id} (Count: {len(cluster_data)} - Avg Angle: {np.mean(angles):.1f}°)",
                     va='bottom', fontsize=14)

        # Hide radial labels (the frequency numbers) for a cleaner look
        ax.set_yticks([])

        # Set a Super Title for the entire figure
    fig.suptitle("Comparison of Parcel Orientation by Morphological Cluster (Farahzad)", fontsize=20, y=1.02)

    # Adjust layout to prevent overlapping titles
    plt.tight_layout(rect=[0, 0, 1, 0.98])

    # 2. Save the diagram
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Multi-Rose Diagram saved to: {output_path}")


print("2. Generating Multi-Rose Diagram (4 Plots)...")
create_multi_rose_diagram(gdf, unique_clusters, OUTPUT_DIR / '07_orientation_by_cluster_rose_diagrams.png')
print("-" * 60)
print("SUCCESS: All final visualizations are complete! Check the 'results' folder.")