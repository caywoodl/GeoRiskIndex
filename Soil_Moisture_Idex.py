import arcpy, os
from arcpy.sa import *

arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")

# --- INPUT RASTERS (assumes they are in current workspace or provided path) ---
wv10 = Raster("wv10_CompBand")
wv33 = Raster("wv33_CompBand")

# --- OUTPUT FOLDER (relative or user-defined path) ---
out_folder = os.path.join(os.getcwd(), "SoilMoisture_Depth")

# Create folder if it doesn't exist
if not os.path.exists(out_folder):
    os.makedirs(out_folder)

# ----------------------------------------------------
# STEP 1 — DEPTH-SPECIFIC MOISTURE (BAND AVERAGING)
# ----------------------------------------------------
moist_5_15 = (Raster(wv10, 1) + Raster(wv33, 1)) / 2
moist_5_15.save(os.path.join(out_folder, "Moisture_5_15cm.tif"))

moist_15_30 = (Raster(wv10, 2) + Raster(wv33, 2)) / 2
moist_15_30.save(os.path.join(out_folder, "Moisture_15_30cm.tif"))

moist_30_60 = (Raster(wv10, 3) + Raster(wv33, 3)) / 2
moist_30_60.save(os.path.join(out_folder, "Moisture_30_60cm.tif"))

print("Done ✔ Depth moisture rasters created.")

import arcpy
from arcpy.sa import *
import os

arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")

# --- FOLDER (same output directory) ---
folder = os.path.join(os.getcwd(), "SoilMoisture_Depth")

# --- INPUT RASTERS ---
m_5_15 = Raster(os.path.join(folder, "Moisture_5_15cm.tif"))
m_15_30 = Raster(os.path.join(folder, "Moisture_15_30cm.tif"))
m_30_60 = Raster(os.path.join(folder, "Moisture_30_60cm.tif"))

# ----------------------------------------------------
# ALIGNMENT (CRITICAL FOR RASTER CONSISTENCY)
# ----------------------------------------------------
arcpy.env.snapRaster = m_5_15
arcpy.env.cellSize = m_5_15
arcpy.env.extent = m_5_15

# ----------------------------------------------------
# STEP 2 — DEPTH WEIGHTING
# ----------------------------------------------------
soil_moisture_risk = (m_5_15 * 0.4) + (m_15_30 * 0.35) + (m_30_60 * 0.25)

risk_path = os.path.join(folder, "Soil_Moisture_Risk_Index.tif")
soil_moisture_risk.save(risk_path)

print("Depth-weighted moisture index created.")

# ----------------------------------------------------
# STEP 3 — NORMALIZE 0–1
# ----------------------------------------------------
min_val = float(arcpy.GetRasterProperties_management(risk_path, "MINIMUM").getOutput(0))
max_val = float(arcpy.GetRasterProperties_management(risk_path, "MAXIMUM").getOutput(0))

normalized = (Raster(risk_path) - min_val) / (max_val - min_val)

norm_path = os.path.join(folder, "Soil_Moisture_Risk_Index_0_1.tif")
normalized.save(norm_path)

print("Normalized 0–1 soil moisture risk raster created.")

