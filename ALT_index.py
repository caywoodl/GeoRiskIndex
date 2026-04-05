import rasterio
import numpy as np
import os
import warnings

# ---------------------------------------
# USER INPUTS
# ---------------------------------------

# Root project directory
project_folder = r"C:\Project\Permafrost_Analysis"

# Input and output folders
input_folder = os.path.join(project_folder, "input_rasters")
output_folder = os.path.join(project_folder, "normalized_rasters")

# Input raster name
input_name = "ALT_mean_2001_2015.tif"

# Output raster name
output_name = "ALT_mean_2001_2015_norm.tif"

# ---------------------------------------
# PATHS
# ---------------------------------------

input_tif = os.path.join(input_folder, input_name)
output_tif = os.path.join(output_folder, output_name)

# Create output directory if needed
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Check that input raster exists
if not os.path.exists(input_tif):
    raise RuntimeError(f"Input raster not found: {input_tif}")

# ---------------------------------------
# READ RASTER
# ---------------------------------------

with rasterio.open(input_tif) as src:

    profile = src.profile.copy()

    # Update metadata for output raster
    profile.update(
        dtype=rasterio.float32,
        count=1,
        nodata=np.nan,
        compress="lzw"
    )

    # Read raster band as float
    data = src.read(1).astype("float32")

    # ---------------------------------------
    # NORMALIZATION (MIN-MAX SCALING)
    # ---------------------------------------

    # Suppress warnings caused by NaN-only areas
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)

        min_val = np.nanmin(data)
        max_val = np.nanmax(data)

        # Min–max normalization to range 0–1
        data_norm = (data - min_val) / (max_val - min_val)

# ---------------------------------------
# WRITE NORMALIZED RASTER
# ---------------------------------------

with rasterio.open(output_tif, "w", **profile) as dst:
    dst.write(data_norm.astype(rasterio.float32), 1)

print("Normalization complete.")
print(f"Output raster saved to: {output_tif}")
print(f"Normalized range: min={np.nanmin(data_norm)}, max={np.nanmax(data_norm)}")