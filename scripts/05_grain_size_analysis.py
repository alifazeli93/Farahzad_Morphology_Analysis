import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
from pathlib import Path

# --- Setup Paths ---
print("--- Starting 05_grain_size_analysis.py (Grain Size Analysis) ---")
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

# --- 1. Statistical Summary (Quantitative Grain Size) ---

area_data = gdf['area_m2'].dropna()

print("1. Statistical Summary of Parcel Area (Grain Size):")
print(f"Total Parcels Analyzed: {len(area_data)}")
print(f"Mean Area (m²): {area_data.mean():.2f}")
print(f"Median Area (m²): {area_data.median():.2f}")
print(f"Standard Deviation: {area_data.std():.2f}")
print("-" * 60)


# --- 2. Visualization (Log-transformed Histogram) ---

def create_area_histogram(area_data, output_path):
    """Generates a log-transformed histogram to visualize area distribution."""

    # Apply Log transformation to handle the skewed data distribution
    # We use a slight offset (+1) to handle potential zero or near-zero values if they existed.
    log_area = np.log10(area_data + 1)

    # 1. Create the plot
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plotting the histogram with density=True for normalized counts
    ax.hist(log_area, bins=30, edgecolor='black', color='#1f77b4', density=True)

    # 2. Customizing the Axis Labels (Showing actual area values)

    # Log area ticks (e.g., 2, 3, 4, 5)
    log_ticks = np.arange(np.floor(log_area.min()), np.ceil(log_area.max()) + 1)

    # Convert log area back to actual area labels (10^2, 10^3, 10^4)
    area_labels = [f'$10^{{{int(t)}}}$' for t in log_ticks]

    ax.set_xticks(log_ticks)
    ax.set_xticklabels(area_labels)

    ax.set_title("Distribution of Parcel Area (Log-transformed) - Farahzad", fontsize=16)
    ax.set_xlabel("Parcel Area (m²)", fontsize=12)
    ax.set_ylabel("Frequency / Density", fontsize=12)
    ax.grid(axis='y', alpha=0.5)

    # 3. Save the visualization
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Area Histogram saved to: {output_path}")


print("2. Generating Log-transformed Area Histogram...")
create_area_histogram(area_data, OUTPUT_DIR / '03_grain_size_histogram.png')
print("-" * 60)
print("SUCCESS: Grain Size analysis complete. Check the 'results' folder!")