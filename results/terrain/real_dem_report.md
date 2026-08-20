# Dhanbad SRTM 1 Arc-Second DEM Analysis Report

**Study Area:** Dhanbad & Surrounding Region, Jharkhand, India  
**Raster Dataset:** `data/mine_dem.tif` (SRTM 1 Arc-Second Global DEM)  
**Label:** Dhanbad SRTM Terrain Analysis — Prototype  

---

## 1. DEM Metadata & Raster Characteristics

| Parameter | Value |
| :--- | :--- |
| **File Dimensions** | 3601 x 3601 pixels |
| **Number of Bands** | 1 |
| **CRS** | `EPSG:4326` |
| **Coordinate System** | Geographic Coordinate System (GCS_WGS_1984, Latitude/Longitude) |
| **Pixel Resolution** | 0.0002777778° x 0.0002777778° (approx 28.4m lon x 30.9m lat at ~23.5°N) |
| **Geographic Bounds** | West: 85.999861°, South: 22.999861°, East: 87.000139°, North: 24.000139° |
| **Minimum Elevation** | 65.0 m |
| **Maximum Elevation** | 1374.0 m |
| **Mean Elevation** | 208.61 m |
| **Median Elevation** | 196.0 m |
| **Standard Deviation** | 79.59 m |
| **NoData Value** | `-32767.0` |
| **NoData Pixel Percentage** | 0.0% |
| **Valid Pixel Count** | 12,967,201 / 12,967,201 |

---

## 2. Derived Terrain Derivatives

The following 6 terrain layers were calculated from the real SRTM DEM using `TerrainFeatureExtractor` (`src/terrain_features.py`):

1. **Elevation (`elevation.tif`)**: Topographic height above mean sea level in meters.
2. **Slope in Degrees (`slope.tif`)**: Morphological inclination angle calculated using Sobel gradient operators with latitude-adjusted cell distances in meters (~28.4m x 30.9m).
3. **Aspect in Degrees (`aspect.tif`)**: Down-slope direction of maximum rate of change in elevation (0° = North, 90° = East, 180° = South, 270° = West).
4. **Curvature (`curvature.tif`)**: Second spatial derivative (Laplacian) representing surface convexity/concavity.
5. **Terrain Roughness Index / TRI (`roughness.tif`)**: Local surface variability measured as 3x3 window standard deviation of elevation in meters.
6. **Topographic Wetness Index / TWI (`twi.tif`)**: Morphometric measure of soil moisture accumulation capacity defined as ln(a / tan(beta)).

---

## 3. Quality Control (QC) Audit

All derived layers saved under `results/terrain/real/` were audited against spatial and numerical integrity standards:

- **Dimension Consistency**: Verified 3601 x 3601 pixels across all 6 rasters.
- **CRS & Spatial Transform**: Verified identical `EPSG:4326` CRS and spatial affine transform.
- **Bounds Alignment**: Verified identical bounding box coordinates (86.0°E to 87.0°E, 23.0°N to 24.0°N).
- **NoData Value Handling**: Standardized to `-9999.0` for all derived float rasters.
- **Data Integrity Audit**:
  - **NaN Values**: 0 NaN values detected in valid domain across all rasters.
  - **Infinite Values**: 0 Inf / -Inf values detected in valid domain.
  - **Physical Range Validation**:
    - Elevation: [65.0m, 1374.0m] (Valid range for Chota Nagpur plateau / Parasnath range)
    - Slope: [0.0°, 61.82°] (Valid physical slope angles)
    - Aspect: [0.0°, 360.0°] (Valid directional angles)

---

## 4. Derived Terrain Summary Statistics

| Layer | Min | Max | Mean | Median | Std Dev | Valid Pixels |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **elevation** | 65.0 | 1374.0 | 208.6138 | 196.0 | 79.5917 | 12,967,201 |
| **slope** | 0.0 | 61.8174 | 3.1885 | 2.524 | 3.3641 | 12,967,201 |
| **aspect** | 0.0 | 359.7039 | 177.131 | 180.0 | 104.3275 | 12,967,201 |
| **curvature** | -0.1366 | 0.1514 | -0.0 | 0.0 | 0.0033 | 12,967,201 |
| **roughness** | 0.0 | 43.511 | 1.5195 | 1.1967 | 1.5083 | 12,967,201 |
| **twi** | 8.3572 | 14.6137 | 10.4098 | 10.2814 | 0.7337 | 12,967,201 |


---

## 5. Slope Category Distribution

Terrain pixels were classified into 6 standardized slope categories:

| Category | Angle Range | Pixel Count | Percentage |
| :--- | :---: | :---: | :---: |
| **Very Low** | 0–10° | 12,556,194 | 96.8304% |
| **Low** | 10–20° | 274,757 | 2.1189% |
| **Moderate** | 20–30° | 110,124 | 0.8493% |
| **High** | 30–40° | 24,264 | 0.1871% |
| **Very High** | 40–50° | 1,717 | 0.0132% |
| **Extreme** | >50° | 145 | 0.0011% |


---

## IMPORTANT SCIENTIFIC NOTE

> [!WARNING]
> **Geotechnical & Morphological Disclaimer**:
> Do not interpret steep slope as automatically meaning rockfall.
> The terrain layers derived herein are morphological susceptibility indicators and must later be combined with geological, environmental, structural, and sensor evidence (e.g. lithology, jointing, rainfall, blasting vibration, InSAR deformation).
> Do not claim that the SRTM DEM alone predicts rockfall.
