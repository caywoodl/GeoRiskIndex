import arcpy
from arcpy.sa import *

# ----------------------------------------------------
# ENVIRONMENT SETUP
# ----------------------------------------------------
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

# Use current workspace if already set in ArcGIS Pro;
# otherwise default to the current folder
arcpy.env.workspace = arcpy.env.workspace or "."

# ----------------------------------------------------
# INPUT RASTERS
# These should already exist in the workspace or geodatabase
# and should be normalized to a comparable 0–1 scale.
# ----------------------------------------------------
rasters = {
    "carbon_index": "Carbon_Storage_Index",
    "ground_vulnerability_index": "ground_vulnerability_index",
    "soil_index": "Soil_Vulnerability_Index",
    "ALT_index": "ALT_index",
    "soil_moisture_index": "Soil_Moisture_Risk_Index_0_1"
}

# ----------------------------------------------------
# STEP 1 — RASTER COMPATIBILITY CHECK
# ----------------------------------------------------
print("=== Raster Compatibility Check ===\n")

existing_rasters = {}
reference_raster = None

for label, raster_name in rasters.items():
    if not arcpy.Exists(raster_name):
        print(f"❌ {label}: {raster_name} does not exist\n")
        continue

    desc = arcpy.Describe(raster_name)
    existing_rasters[label] = raster_name

    print(f"Raster label: {label}")
    print(f"Raster name: {raster_name}")
    print(f"  Data type: {desc.dataType}")

    sr = desc.spatialReference
    print(f"  Projection: {sr.name if sr else 'None'}")

    print(f"  Cell size (X, Y): {desc.meanCellWidth}, {desc.meanCellHeight}")

    ext = desc.extent
    print(f"  Extent: XMin={ext.XMin}, XMax={ext.XMax}, YMin={ext.YMin}, YMax={ext.YMax}")

    print(f"  Pixel type: {desc.pixelType}")

    try:
        nodata = arcpy.GetRasterProperties_management(raster_name, "ANYNODATA").getOutput(0)
        print(f"  Any NoData present: {nodata}")
    except Exception:
        print("  Any NoData present: Could not retrieve")

    print("-" * 50)

    if reference_raster is None:
        reference_raster = raster_name

print("\n=== Check complete ===\n")

# ----------------------------------------------------
# STEP 2 — CONFIRM ALL REQUIRED INPUTS EXIST
# ----------------------------------------------------
required_labels = list(rasters.keys())
missing = [label for label in required_labels if label not in existing_rasters]

if missing:
    raise RuntimeError(
        "The following required rasters are missing: " + ", ".join(missing)
    )

# ----------------------------------------------------
# STEP 3 — ALIGNMENT ENVIRONMENT
# Uses the first raster as the reference raster so all
# overlay output is spatially consistent.
# ----------------------------------------------------
arcpy.env.snapRaster = reference_raster
arcpy.env.cellSize = reference_raster
arcpy.env.extent = reference_raster
arcpy.env.outputCoordinateSystem = arcpy.Describe(reference_raster).spatialReference

# ----------------------------------------------------
# STEP 4 — WEIGHTED OVERLAY
# Composite geologic/permafrost risk raster
# ----------------------------------------------------
permafrost_carbon_risk = (
    0.30 * Raster(rasters["carbon_index"]) +
    0.25 * Raster(rasters["ground_vulnerability_index"]) +
    0.20 * Raster(rasters["soil_index"]) +
    0.15 * Raster(rasters["ALT_index"]) +
    0.10 * Raster(rasters["soil_moisture_index"])
)

# ----------------------------------------------------
# STEP 5 — SAVE OUTPUT
# ----------------------------------------------------
output_raster = "permafrost_carbon_risk_base"
permafrost_carbon_risk.save(output_raster)

print(f"Composite risk raster created successfully: {output_raster}")