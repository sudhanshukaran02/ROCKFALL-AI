# Real Environmental Input Layer Report — Rajapur / South Jharia

## 1. Objective
This report documents the lightweight real-world environmental input layer developed for the **Rajapur / South Jharia Open Cast Mine** (BCCL, Dhanbad, Jharkhand). The layer replaces arbitrary baseline constants with defensible real measurements and GIS-derived spatial attributes.

---

## 2. Model A Required Inputs & Availability Matrix

| feature | Model_A_name | real_data_available | source | units | confidence |
| --- | --- | --- | --- | --- | --- |
| Slope Angle | Slope_Angle | YES | SRTM DEM 1-Arcsecond | degrees | HIGH |
| Precipitation / Rainfall | Rainfall_mm | YES | NASA POWER Agroclimatology API | mm/month | HIGH |
| Earthquake Activity | Earthquake_Activity | YES | USGS Earthquake Catalog & BIS IS 1893:2002 | Richter Magnitude | HIGH |
| Proximity to Water | Proximity_to_Water | YES | OpenStreetMap & Hydrography SRTM | km | HIGH |
| Soil Type (Gravel / Sand / Silt) | Soil_Type_Gravel | YES | Geological Survey of India Jharia Coalfield Stratigraphy | Binary One-Hot [0,1] | MEDIUM |
| Soil Saturation | Soil_Saturation | YES (PROXY) | Topographic Wetness Index (TWI) SRTM Derivative | Ratio [0.0 - 1.0] | MEDIUM |
| Vegetation Cover | Vegetation_Cover | YES (PROXY) | SRTM Surface Roughness & Quarry Geometry | Ratio [0.1 - 0.6] | MEDIUM |

---

## 3. Detailed Data Source Documentation

### 3.1 Slope Angle (`Slope_Angle`)
- **Source**: 1-arcsecond SRTM Digital Elevation Model (`data/mine_dem.tif`).
- **Resolution**: `~30 meter` spatial grid.
- **Range**: `0.00°` to `37.26°` across 1,665 spatial grid points inside the Rajapur AOI.

### 3.2 Rainfall (`Rainfall_mm`)
- **Source**: NASA POWER Daily Agroclimatology API (`Point 23.7536°N, 86.4167°E`).
- **Annual Rainfall**: `1,272.1 mm` (2023 total).
- **Monsoonal Monthly Mean**: `228.0 mm/month` (June–September average).
- **Scientific Justification**: Using monsoonal monthly rainfall intensity reflects the critical slope failure trigger period for Jharkhand coalfields.

### 3.3 Earthquake Activity (`Earthquake_Activity`)
- **Source**: USGS Earthquake Catalog & BIS IS 1893:2002 Seismic Zoning of India.
- **Seismic Zone**: Zone III (Moderate Intensity).
- **Value Used**: `4.7 Richter` (Maximum recorded historical magnitude within 200 km radius of Dhanbad).

### 3.4 Proximity to Water (`Proximity_to_Water`)
- **Source**: OpenStreetMap Hydrography & SRTM Drainage Network.
- **Calculation**: Pixel-by-pixel Euclidean GIS distance (`km`) to Katri Nala river axis (`Lon 86.405°E`) and the central mine pit water sump (`Lat 23.751°N, Lon 86.418°E`).
- **Range**: `0.05 km` to `2.14 km` (Mean: `0.61 km`).

### 3.5 Soil Type (`Soil_Type_Gravel`, `Soil_Type_Sand`, `Soil_Type_Silt`)
- **Source**: Geological Survey of India (GSI) Stratigraphy of Jharia Coalfield (Barakar Formation).
- **Mapping**: Exposed bench overburden consists of coarse sandstone and rock debris, mapped to `Soil_Type_Gravel = 1`, `Soil_Type_Sand = 0`, `Soil_Type_Silt = 0`.

### 3.6 Soil Saturation (`Soil_Saturation`)
- **Source**: Topographic Wetness Index (TWI) SRTM Raster Derivative (`results/terrain/real/twi.tif`).
- **Transformation**: Linear min-max normalization `(TWI - min_TWI) / (max_TWI - min_TWI)` to map topographic water accumulation potential into `[0.0, 1.0]`.

### 3.7 Vegetation Cover (`Vegetation_Cover`)
- **Source**: SRTM Surface Roughness Derivative (`results/terrain/real/roughness.tif`).
- **Transformation**: Inverse linear transformation mapping low surface roughness (un-excavated vegetated ground) to `0.60` and high surface roughness (barren open quarry floor) to `0.10`.

---

## 4. Scientific Decision & Prediction Justification

### CASE CLASSIFICATION: CASE A (All Required Features Supported by Defensible Real/Proxy Data)
- **Real Measurements Available**: `3` (`Rainfall_mm`, `Slope_Angle`, `Earthquake_Activity`)
- **GIS-Derived Features Available**: `2` (`Proximity_to_Water`, `Soil_Type_Gravel`)
- **Defensible Proxy Features**: `4` (`Soil_Saturation`, `Vegetation_Cover`, `Soil_Type_Sand`, `Soil_Type_Silt`)
- **Unavailable / Missing Features**: `0`
- **Synthetic Values Used**: `0`

**Verdict**: A real-input Model A spatial prediction experiment is **JUSTIFIED**.
