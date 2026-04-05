import arcpy
from arcpy.sa import *

# Enable Spatial Analyst
arcpy.CheckOutExtension("Spatial")

# -----------------------------
# ENVIRONMENT (portable)
# -----------------------------
arcpy.env.workspace = arcpy.env.workspace or "."
arcpy.env.overwriteOutput = True

# -----------------------------
# INPUTS (user-defined or in workspace)
# -----------------------------
input_layer = "Circum_Arctic_GI_NSB"
combo_field = "COMBO"

# Output raster
output_raster = "CAGI_risk_normalized_dynamic.tif"

# -----------------------------
# STEP 1 — GET UNIQUE COMBO VALUES
# -----------------------------
combo_values = [row[0] for row in arcpy.da.SearchCursor(input_layer, [combo_field])]
unique_combos = set(combo_values)

# -----------------------------
# STEP 2 — DEFINE WEIGHTS
# -----------------------------
extent_weights = {'c': 1.0, 'd': 0.75, 's': 0.5, 'i': 0.25}
ice_weights = {'h': 1.0, 'm': 0.66, 'l': 0.33}
terrain_weights = {'f': 1.0, 'r': 0.5}
non_permafrost = {'g','l','o','r','ld'}

# -----------------------------
# STEP 3 — BUILD RECLASS TABLE
# -----------------------------
reclass_list = []

for combo in unique_combos:
    combo_lower = str(combo).lower()
    if combo_lower in non_permafrost:
        risk = 0
    else:
        try:
            extent = combo_lower[0]
            ice = combo_lower[1]
            terrain = combo_lower[2]
            risk = (
                extent_weights.get(extent, 0) *
                ice_weights.get(ice, 0) *
                terrain_weights.get(terrain, 0)
            )
        except IndexError:
            risk = 0
    reclass_list.append((combo, risk))

remap = RemapValue(reclass_list)

# -----------------------------
# STEP 4 — POLYGON → RASTER (IF NEEDED)
# -----------------------------
desc = arcpy.Describe(input_layer)

if desc.dataType.lower() in ["featureclass", "shapefile"]:
    temp_raster = "temp_CAGI_dynamic.tif"
    arcpy.conversion.PolygonToRaster(
        in_features=input_layer,
        value_field=combo_field,
        out_rasterdataset=temp_raster,
        cell_assignment="MAXIMUM_COMBINED_AREA",
        priority_field=combo_field,
        cellsize=1000  # adjust as needed
    )
else:
    temp_raster = input_layer

# -----------------------------
# STEP 5 — RECLASSIFY + NORMALIZE
# -----------------------------
risk_raster = Reclassify(temp_raster, "Value", remap, "NODATA")

max_val = float(arcpy.GetRasterProperties_management(risk_raster, "MAXIMUM").getOutput(0))
normalized_raster = risk_raster / max_val

# Save output
normalized_raster.save(output_raster)

print(f"Normalized risk raster saved: {output_raster}")