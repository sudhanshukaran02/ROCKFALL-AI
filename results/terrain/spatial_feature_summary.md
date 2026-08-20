# Spatial Terrain Feature Dataset Summary

**Dataset Label:** Mine AOI Clipped Dataset (AOI: rajapur_south_jharia_aoi.geojson)  
**Input DEM:** `data/mine_dem.tif`  
**Terrain Layer Directory:** `results/terrain/real`  
**AOI GeoJSON Path:** `scratch/rajapur_south_jharia_aoi.geojson`  
**Extraction Note:** Full extraction of all 1,665 valid pixels.  

---

## 1. Spatial & Dataset Overview

| Parameter | Value |
| :--- | :--- |
| **Dataset Type** | Mine AOI Clipped Dataset (AOI: rajapur_south_jharia_aoi.geojson) |
| **CRS** | `EPSG:4326` |
| **Pixel Resolution** | `0.0002777778° x 0.0002777778°` (approx 28.4m lon x 30.9m lat) |
| **Geographic Bounds (Data)** | Latitude: [23.746389°, 23.765000°], Longitude: [86.412500°, 86.424444°] |
| **Exported Rows (Pixels)** | **1,665** |
| **Total Area Pixels** | 3,220 |
| **Valid Pixels Found** | 1,665 |
| **Excluded / NoData Pixels** | 1,555 |

---

## 2. Feature Statistics

The extracted tabular dataset contains **8 features**: `latitude`, `longitude`, `elevation`, `slope`, `aspect`, `curvature`, `roughness`, `twi`.

| Feature | Min | Max | Mean | Median | Std Dev |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **latitude** | 23.746389 | 23.765 | 23.755229 | 23.755278 | 0.004749 |
| **longitude** | 86.4125 | 86.424444 | 86.417959 | 86.417778 | 0.00303 |
| **elevation** | 134.0 | 236.0 | 204.944144 | 207.0 | 18.603495 |
| **slope** | 0.0 | 37.255566 | 6.75532 | 4.445918 | 6.403425 |
| **aspect** | 0.0 | 358.356293 | 193.666896 | 219.277359 | 112.274837 |
| **curvature** | -0.019351 | 0.030733 | 3.1e-05 | -0.0 | 0.005149 |
| **roughness** | 0.0 | 19.036676 | 3.119005 | 2.060804 | 2.877491 |
| **twi** | 8.641626 | 13.646056 | 10.042373 | 9.962476 | 0.716835 |


---

## 3. Data Integrity & Alignment Verification

- **Spatial Alignment:** Verified 100% spatial transform and cell boundary alignment across all 7 input rasters.
- **Coordinate Integrity:** Derived pixel-center latitude/longitude using exact affine spatial transform matrix.
- **Null & Invalid Values:** **0** null/NaN values, **0** infinite values, and **0** NoData (-9999.0) values present in exported CSV.
- **Domain Constraints:** All slope values within [0°, 90°], aspect within [0°, 360°], elevation within valid physical range.

---

## IMPORTANT SCIENTIFIC NOTE

> [!WARNING]
> **Spatial Intelligence & Morphological Disclaimer**:
> This dataset provides spatial terrain features for geographic intelligence and susceptibility modeling.
> Do NOT interpret steep slope as automatically meaning rockfall.
> Terrain layers must later be combined with geological, environmental, structural, and sensor evidence.
> No machine learning models were trained during this step.
