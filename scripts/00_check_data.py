import geopandas as gpd
import os
import sys

# Define target CRS for Tehran (UTM Zone 39N)
TARGET_CRS = "EPSG:32639"

# --- 1. Define File Paths ---
current_script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_script_dir)
shapefile_path = os.path.join(project_root, 'data', 'raw', 'parcels.shp')
output_path = os.path.join(project_root, 'data', 'processed', 'parcels_utm.gpkg')

print(f"Loading file from: {shapefile_path}")
print("-" * 60)

try:
    # 2. Load the Shapefile
    gdf = gpd.read_file(shapefile_path)

    print("SUCCESS: Shapefile loaded correctly.")
    print(f"Initial CRS: {gdf.crs}")

    # 3. Check and Reproject
    if gdf.crs is None or not gdf.crs.is_projected:
        print("\n--- Reprojection Action ---")

        # We first assign the commonly assumed geographic CRS (WGS 84)
        print("ACTION 1: Assigning WGS 84 (EPSG:4326) as the source CRS.")
        gdf = gdf.set_crs(epsg=4326, allow_override=True)

        # Then, transform the layer to the target Metric CRS (UTM 39N)
        print(f"ACTION 2: Reprojecting to Metric system ({TARGET_CRS}).")
        gdf = gdf.to_crs(TARGET_CRS)

        print(f"SUCCESS: Layer reprojected to {gdf.crs}")

    else:
        print("STATUS: CRS is already Metric. Continuing...")

    # 4. Save the Cleaned Data (for Phase 1)
    # Saving as GeoPackage (.gpkg) is modern and preserves CRS better than SHP
    gdf.to_file(output_path, driver="GPKG")

    print("-" * 60)
    print(f"🎉 Phase 0 COMPLETE! Cleaned data saved to: {output_path}")

    # Pass the reprojected GeoDataFrame for the next phase
    print(f"Ready for Phase 1. Total parcels: {len(gdf)}")

except FileNotFoundError:
    print("ERROR: File not found!")
    sys.exit()
except Exception as e:
    print(f"An unexpected error occurred: {e}")