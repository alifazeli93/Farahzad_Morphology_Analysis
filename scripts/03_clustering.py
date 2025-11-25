import geopandas as gpd
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import os
import sys
from pathlib import Path

# --- Setup Paths ---
print("--- Starting 03_clustering.py (K-Means Analysis) ---")
current_script_path = Path(__file__).resolve()
project_root = current_script_path.parent.parent

INPUT_PATH = project_root / 'data' / 'processed' / 'parcels_metrics_final.gpkg'
OUTPUT_PATH = project_root / 'data' / 'processed' / 'parcels_final_clustered.gpkg'

# --- Load Data ---
try:
    gdf = gpd.read_file(INPUT_PATH)
    print(f"Data loaded successfully. Parcel count: {len(gdf)}")
    print("-" * 60)
except Exception as e:
    print(f"FATAL ERROR: Could not load final data. {e}")
    sys.exit()

# --- 2. Data Preparation and Normalization ---

# Select features for clustering
features = [
    'area_m2',
    'compactness_idx',
    'rectangularity_idx',
    'orientation_angle'
]

X = gdf[features].copy()

# Critical step: Normalization (Standard Scaling)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
print("Data successfully normalized (StandardScaler applied).")
print("-" * 60)

# --- 3. Determining Optimal Clusters ---
N_CLUSTERS = 4
print(f"Attempting K-Means clustering with N_CLUSTERS = {N_CLUSTERS}...")


# --- 4. K-Means Clustering ---
kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=42, n_init=10)
gdf['morpho_cluster'] = kmeans.fit_predict(X_scaled)

print(f"SUCCESS: Clustering completed. Identified {N_CLUSTERS} distinct morphological patterns.")
print("-" * 60)


# --- 5. Analysis and Summarization ---
print("Cluster Summary (Mean Metrics for each Cluster):")

# **FIXED CODE:** Exclude geometry and non-numeric columns explicitly
numeric_cols = features + ['compactness_idx', 'rectangularity_idx', 'orientation_angle', 'area_m2', 'perimeter_m']
numeric_cols = list(set(numeric_cols)) # Remove duplicates

# Group by the cluster ID and calculate the mean for all numeric columns
cluster_summary = gdf[numeric_cols + ['morpho_cluster']].groupby('morpho_cluster').mean()
print(cluster_summary)

# --- 6. Saving Final Results ---
# Convert the cluster column to string for GeoPackage compatibility
gdf['morpho_cluster'] = gdf['morpho_cluster'].astype(str)
gdf.to_file(OUTPUT_PATH, driver="GPKG")
print("-" * 60)
print(f"FINAL RESULT: Clustered data saved to: {OUTPUT_PATH}")
print("Ready for final visualization (Mapping and Rose Diagram).")