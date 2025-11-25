import geopandas as gpd
import pandas as pd
import os
import sys
from pathlib import Path

# --- Setup Paths ---
print("--- Starting 08_cluster_descriptive_table.py (Final Summary Table) ---")
current_script_path = Path(__file__).resolve()
project_root = current_script_path.parent.parent

# Load the final clustered data
INPUT_PATH = project_root / 'data' / 'processed' / 'parcels_final_clustered.gpkg'
OUTPUT_DIR = project_root / 'results'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Load Data ---
try:
    # We explicitly read the 'morpho_cluster' column as numeric again for grouping accuracy
    gdf = gpd.read_file(INPUT_PATH)
    gdf['morpho_cluster'] = pd.to_numeric(gdf['morpho_cluster'])
    print(f"Clustered data loaded. Parcel count: {len(gdf)}")
    print("-" * 60)
except Exception as e:
    print(f"FATAL ERROR: Could not load data. {e}")
    sys.exit()


# --- 1. Define Features for Summary ---

# All key metrics calculated throughout the project
summary_features = [
    'area_m2',
    'perimeter_m',
    'compactness_idx',
    'rectangularity_idx',
    'orientation_angle'
]

# --- 2. Calculate Descriptive Statistics (Mean) ---

# Select features and group by cluster, calculating the mean
cluster_summary = gdf[summary_features + ['morpho_cluster']].groupby('morpho_cluster').mean()

# Add the number of parcels in each cluster (Cluster Size)
cluster_size = gdf.groupby('morpho_cluster').size().rename('parcel_count')
cluster_summary = pd.concat([cluster_size, cluster_summary], axis=1)

# Format the results for better readability in the report
pd.options.display.float_format = '{:,.2f}'.format
print("1. Final Descriptive Cluster Table (Mean Metrics):")
print(cluster_summary)
print("-" * 60)


# --- 3. Save the Table ---
OUTPUT_FILE = OUTPUT_DIR / '06_descriptive_cluster_table.csv'
cluster_summary.to_csv(OUTPUT_FILE, index=True)

print(f"SUCCESS: Descriptive table saved to: {OUTPUT_FILE}")

