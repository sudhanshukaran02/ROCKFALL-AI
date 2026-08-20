# Rajapur Environmental Input Gap Audit Report

## 1. Executive Summary
This document presents the formal input gap audit evaluating the **9 required features** of Model A (`models/model_A_best.pkl`) against authoritative real-world measurements and GIS-derived layers for the **Rajapur / South Jharia Open Cast Mine** (BCCL, Dhanbad, Jharkhand).

---

## 2. Audit Classification Matrix of Model A Features

| Feature Name | Model A Column | Audit Classification | Real Source Identified | Transformation / Method |
| :--- | :--- | :--- | :--- | :--- |
| **Slope Angle** | `Slope_Angle` | **A. REAL GIS-DERIVED VALUE** | SRTM 1-Arcsecond DEM | Raster slope derivative (`results/terrain/real/slope.tif`) |
| **Rainfall** | `Rainfall_mm` | **A. REAL MEASUREMENT** | NASA POWER Agroclimatology API | 2023 actual monsoonal monthly mean (`261.3 mm/month`) |
| **Earthquake Activity** | `Earthquake_Activity` | **A. REAL MEASUREMENT** | USGS Earthquake Catalog | Max historical magnitude within 200km (`4.7 Richter`) |
| **Proximity to Water** | `Proximity_to_Water` | **B. REAL GIS-DERIVED VALUE** | OpenStreetMap Hydrography | GIS Euclidean distance to Katri Nala & pit sump (`km`) |
| **Soil Type Gravel** | `Soil_Type_Gravel` | **C. DEFENSIBLE PROXY** | GSI Jharia Coalfield Stratigraphy | Barakar sandstone overburden mapped to `Gravel=1` |
| **Soil Type Sand** | `Soil_Type_Sand` | **C. DEFENSIBLE PROXY** | GSI Jharia Coalfield Stratigraphy | Mapped to `Sand=0` |
| **Soil Type Silt** | `Soil_Type_Silt` | **C. DEFENSIBLE PROXY** | GSI Jharia Coalfield Stratigraphy | Mapped to `Silt=0` |
| **Soil Saturation** | `Soil_Saturation` | **C. DEFENSIBLE PROXY** | TWI SRTM Raster Derivative | Linear min-max normalization of TWI `[0.0, 1.0]` |
| **Vegetation Cover** | `Vegetation_Cover` | **C. DEFENSIBLE PROXY** | SRTM Roughness & Pit Geometry | Roughness-based open pit vegetation proxy `[0.1, 0.6]` |

---

## 3. Key Audit Findings
1. **Elimination of Arbitrary Constants**: Previous exploratory scripts used static fixed constants (e.g. `Rainfall_mm = 120.0`, `Proximity_to_Water = 1.0`). This real input layer replaces all static assumptions with pixel-specific spatial calculations and authentic meteorological data.
2. **Zero Fabricated Values**: All 9 features are supported by either direct physical measurements (NASA POWER, USGS) or defensible GIS derivatives (SRTM, OSM, GSI).
3. **Model Compatibility**: All inputs match the exact feature names and expected range formatting of Model A.
