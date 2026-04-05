import arcpy
import os
from arcpy.sa import *

# ----------------------------------------------------
# ENVIRONMENT SETUP
# ----------------------------------------------------
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

# User settings
workspace = os.getcwd()                 # portable workspace
gdb_name = "Permafrost.gdb"
cell_size = 1000
input_layer = "NCSCDv2_Clip"            # feature class or layer name

arcpy.env.workspace = workspace
arcpy.env.cellSize = cell_size

# Paths
gdb_path = os.path.join(workspace, gdb_name)

# ----------------------------------------------------
# CREATE FILE GEODATABASE IF NEEDED
# ----------------------------------------------------
if not os.path.exists(workspace):
    os.makedirs(workspace)

if not arcpy.Exists(gdb_path):
    arcpy.management.CreateFileGDB(workspace, gdb_name)
    print(f"Created geodatabase: {gdb_path}")
else:
    print(f"Geodatabase already exists: {gdb_path}")

# Set workspace to geodatabase for outputs
arcpy.env.workspace = gdb_path

# ----------------------------------------------------
# CREATE FEATURE LAYER AND SET EXTENT
# ----------------------------------------------------
feature_layer = "nsb_layer"
arcpy.management.MakeFeatureLayer(input_layer, feature_layer)
desc = arcpy.Describe(feature_layer)
arcpy.env.extent = desc.extent

print(f"Feature layer created: {feature_layer}")

# ----------------------------------------------------
# FIELDS TO PROCESS
# ----------------------------------------------------
carbon_fields = [
    "SOCM_30CM",
    "SOCM_100CM",
    "SOCM_300",
    "GETSOCM200"
]

percent_fields = [
    "GELISOL_PC",
    "TURBEL_PCT",
    "HISTEL_PCT"
]

# ----------------------------------------------------
# FUNCTIONS
# ----------------------------------------------------
def polygon_to_raster(field_name, out_name=None):
    """Convert a polygon field to raster."""
    if out_name is None:
        out_name = field_name

    arcpy.conversion.PolygonToRaster(
        in_features=feature_layer,
        value_field=field_name,
        out_rasterdataset=out_name,
        cell_assignment="CELL_CENTER",
        cellsize=cell_size
    )
    return out_name


def copy_to_float(in_raster, out_name=None):
    """Copy raster to 32-bit float."""
    if out_name is None:
        out_name = f"{in_raster}_float"

    arcpy.management.CopyRaster(
        in_raster,
        out_name,
        pixel_type="32_BIT_FLOAT"
    )
    return out_name


def normalize_minmax(in_raster, out_name=None):
    """Normalize raster to 0–1 using min-max scaling."""
    if out_name is None:
        out_name = f"{in_raster}_Norm"

    arcpy.management.CalculateStatistics(in_raster)
    r = Raster(in_raster)

    min_val = float(arcpy.management.GetRasterProperties(in_raster, "MINIMUM").getOutput(0))
    max_val = float(arcpy.management.GetRasterProperties(in_raster, "MAXIMUM").getOutput(0))

    print(f"Normalizing {in_raster} | Min={min_val}, Max={max_val}")

    if max_val == min_val:
        norm = CreateConstantRaster(0, "FLOAT", r.meanCellWidth, r.extent)
    else:
        norm = Float((r - min_val) / (max_val - min_val))

    norm = SetNull(IsNull(r), norm)
    norm.save(out_name)

    print(f"Saved normalized raster: {out_name}")
    return out_name


def normalize_percent_raster(in_raster, out_name=None):
    """Normalize percent raster by dividing by 100."""
    if out_name is None:
        out_name = f"{in_raster}_NORM"

    norm = Raster(in_raster) / 100.0
    norm.save(out_name)

    print(f"Saved percent-normalized raster: {out_name}")
    return out_name


# ----------------------------------------------------
# PROCESS CARBON FIELDS
# ----------------------------------------------------
print("\nProcessing carbon fields...")

carbon_output_map = {
    "SOCM_30CM": "SOCM_30_Den",
    "SOCM_100CM": "SOCM_100_Den",
    "SOCM_300": "SOCM_300_Den",
    "GETSOCM200": "GETSOCM200_Den"
}

first_raster = None
for field in carbon_fields:
    out_raster = carbon_output_map[field]
    raster = polygon_to_raster(field, out_raster)
    raster_float = copy_to_float(raster, out_name=out_raster)

    if first_raster is None:
        first_raster = raster_float
        arcpy.env.snapRaster = first_raster

    normalize_minmax(raster_float, out_name=f"{out_raster}_Norm")

# ----------------------------------------------------
# PROCESS PERCENT FIELDS
# ----------------------------------------------------
print("\nProcessing percent fields...")

percent_output_map = {
    "GELISOL_PC": "GELISOL_PCT",
    "TURBEL_PCT": "TURBEL_PCT",
    "HISTEL_PCT": "HISTEL_PCT"
}

for field in percent_fields:
    out_raster = percent_output_map[field]
    raster = polygon_to_raster(field, out_raster)
    normalize_percent_raster(raster, out_name=f"{out_raster}_NORM")

print("\nAll layers normalized successfully.")

# ----------------------------------------------------
# BUILD CARBON STORAGE INDEX
# ----------------------------------------------------
print("\nBuilding Carbon Storage Index...")

carbon_index = (
    Raster("SOCM_30_Den_Norm") * 0.2 +
    Raster("SOCM_100_Den_Norm") * 0.2 +
    Raster("SOCM_300_Den_Norm") * 0.25 +
    Raster("GETSOCM200_Den_Norm") * 0.35
)

carbon_index.save("Carbon_Storage_Index")
print("Carbon_Storage_Index created.")

# ----------------------------------------------------
# OPTIONAL: ADD OUTPUTS TO CURRENT ARC GIS PRO MAP
# ----------------------------------------------------
try:
    aprx = arcpy.mp.ArcGISProject("CURRENT")
    m = aprx.activeMap

    rasters_to_add = [
        "SOCM_30_Den_Norm",
        "SOCM_100_Den_Norm",
        "SOCM_300_Den_Norm",
        "GETSOCM200_Den_Norm",
        "GELISOL_PCT_NORM",
        "TURBEL_PCT_NORM",
        "HISTEL_PCT_NORM",
        "Carbon_Storage_Index"
    ]

    print("\nAdding rasters to map...")
    for raster_name in rasters_to_add:
        raster_path = os.path.join(gdb_path, raster_name)
        if arcpy.Exists(raster_path):
            m.addDataFromPath(raster_path)
            print(f"Added: {raster_name}")
        else:
            print(f"Not found: {raster_name}")

except Exception as e:
    print(f"Map add skipped: {e}")

print("\nDone.")