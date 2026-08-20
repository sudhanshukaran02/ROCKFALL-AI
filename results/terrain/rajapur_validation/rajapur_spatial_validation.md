# Real Spatial Validation Report — Rajapur / South Jharia Coal Mine

## 1. Objective
This report presents the real spatial validation of the Rajapur/South Jharia coal mine study area. The objective is to verify spatial alignment, examine morphological slope indicators, validate feature extraction integrity, cross-check tabular datasets against raster sources, and produce publication-ready spatial visualizations.

---

## 2. Input Datasets
| Input Dataset | File Path | Format / CRS | Verified Status |
| :--- | :--- | :--- | :--- |
| **Real SRTM DEM** | `data/mine_dem.tif` | GeoTIFF / EPSG:4326 | OK |
| **Official Mine AOI** | `scratch/rajapur_south_jharia_aoi.geojson` | GeoJSON / WGS84 EPSG:4326 | OK (18 Vertices) |
| **Elevation Derivative** | `results/terrain/real/elevation.tif` | GeoTIFF / EPSG:4326 | OK |
| **Slope Derivative** | `results/terrain/real/slope.tif` | GeoTIFF / EPSG:4326 | OK |
| **Aspect Derivative** | `results/terrain/real/aspect.tif` | GeoTIFF / EPSG:4326 | OK |
| **Curvature Derivative** | `results/terrain/real/curvature.tif` | GeoTIFF / EPSG:4326 | OK |
| **Roughness Derivative** | `results/terrain/real/roughness.tif` | GeoTIFF / EPSG:4326 | OK |
| **TWI Derivative** | `results/terrain/real/twi.tif` | GeoTIFF / EPSG:4326 | OK |
| **Spatial Feature Dataset** | `results/terrain/spatial_features.csv` | Tabular CSV (1,665 rows) | OK |

---

## 3. AOI Polygon Information
- **AOI Name**: Rajapur/South Jharia OC Proposed Project Area
- **Bounding Box**:
  - West (Min Lon): `86.412223°E`
  - East (Max Lon): `86.424667°E`
  - South (Min Lat): `23.746118°N`
  - North (Max Lat): `23.765276°N`
- **Surface Area**: `1.4503 km²` (`1,450,347.60 m²`)

---

## 4. CRS and Spatial Alignment Checks
- **Reference CRS**: `EPSG:4326` (Geographic Coordinate System, WGS 84)
- **Raster Dimensions**: `3601 x 3601` pixels (Full SRTM tile)
- **Pixel Resolution**: `0.0002777778° x 0.0002777778°` (~28.4 m lon x 30.9 m lat)
- **Alignment Result**: **PASSED** — All 6 derivative rasters strictly match DEM dimensions, CRS, affine transform, and bounds. No reprojection was performed on source rasters.

---

## 5. AOI Pixel Statistics
- **Bounding Box Raster Dimensions**: `46 x 70` pixels
- **Total Pixels in Bounding Box**: `3,220`
- **Valid Pixels Inside Polygon**: `1,665` (`51.71%`)
- **NoData / Outside Polygon Pixels**: `1,555` (`48.29%`)

---

## 6. Elevation Statistics (Inside AOI)
- **Minimum Elevation**: `134.00 m`
- **Maximum Elevation**: `236.00 m`
- **Mean Elevation**: `204.94 m`
- **Median Elevation**: `207.00 m`
- **Standard Deviation**: `18.60 m`
- **Percentiles**:
  - P5: `160.00 m`
  - P25: `200.00 m`
  - P50 (Median): `207.00 m`
  - P75: `217.00 m`
  - P95: `228.00 m`

---

## 7. Slope Statistics (Inside AOI)
- **Minimum Slope**: `0.00°`
- **Maximum Slope**: `37.26°`
- **Mean Slope**: `6.76°`
- **Median Slope**: `4.45°`
- **Standard Deviation**: `6.40°`

---

## 8. Slope Class Distribution
| Slope Range (Degrees) | Terrain Description | Pixel Count | Percentage of AOI |
| :--- | :--- | :---: | :---: |
| **0° – 10°** | Flat to Gentle Slope | 1,322 | 79.40% |
| **10° – 20°** | Moderate Slope | 250 | 15.02% |
| **20° – 30°** | Steep Terrain | 77 | 4.62% |
| **30° – 40°** | Very Steep Terrain | 16 | 0.96% |
| **> 40°** | Extreme Slope | 0 | 0.00% |

---

## 9. Steep-Slope Threshold Percentages
- **Percentage with Slope > 20°** (Steep terrain / morphological indicator): `5.59%` (`93` pixels)
- **Percentage with Slope > 30°** (High slope indicator): `0.96%` (`16` pixels)
- **Percentage with Slope > 40°** (Extreme slope indicator): `0.00%` (`0` pixels)

---

## 10. Top 20 Steepest Locations inside AOI
The table below lists the 20 highest-slope pixel centers extracted from the clipped terrain rasters:

| rank | latitude | longitude | elevation | slope | aspect | curvature | roughness | twi |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1.0 | 23.75361111 | 86.41666667 | 178.0 | 37.2556 | 188.6667 | 0.009106 | 19.0367 | 8.6416 |
| 2.0 | 23.75388889 | 86.41611111 | 172.0 | 36.9102 | 215.109 | 0.019351 | 18.3168 | 8.6586 |
| 3.0 | 23.75388889 | 86.41583333 | 188.0 | 34.7862 | 213.0736 | -0.005691 | 16.8706 | 8.7129 |
| 4.0 | 23.75361111 | 86.41694444 | 178.0 | 34.3243 | 174.071 | 0.005691 | 17.2698 | 8.7391 |
| 5.0 | 23.75388889 | 86.41638889 | 160.0 | 32.6984 | 207.3911 | 0.025042 | 16.3284 | 8.8143 |
| 6.0 | 23.75555556 | 86.41444444 | 176.0 | 32.1151 | 252.767 | -0.009106 | 14.3329 | 8.8455 |
| 7.0 | 23.75611111 | 86.41416667 | 185.0 | 31.7344 | 266.2522 | -0.002277 | 14.3845 | 8.82 |
| 8.0 | 23.75583333 | 86.41444444 | 168.0 | 31.6647 | 258.2769 | 0.012521 | 14.3914 | 8.8604 |
| 9.0 | 23.75666667 | 86.41444444 | 178.0 | 31.3569 | 302.954 | -0.0 | 14.2292 | 8.7909 |
| 10.0 | 23.75638889 | 86.41416667 | 185.0 | 30.8162 | 284.5215 | 0.007968 | 13.8653 | 8.8233 |
| 11.0 | 23.75472222 | 86.415 | 175.0 | 30.8057 | 224.6132 | -0.002277 | 14.5483 | 8.8894 |
| 12.0 | 23.75444444 | 86.41527778 | 178.0 | 30.7678 | 214.7574 | 0.001138 | 14.3303 | 8.8817 |
| 13.0 | 23.75583333 | 86.41416667 | 188.0 | 30.6579 | 258.9919 | -0.004553 | 13.6463 | 8.8688 |
| 14.0 | 23.75361111 | 86.41722222 | 182.0 | 30.531 | 155.7278 | 0.005691 | 15.1421 | 8.8605 |
| 15.0 | 23.75638889 | 86.41444444 | 166.0 | 30.3579 | 288.5105 | 0.020489 | 13.9532 | 8.8739 |
| 16.0 | 23.75388889 | 86.41722222 | 165.0 | 30.0853 | 141.3976 | 0.017074 | 14.0669 | 8.8824 |
| 17.0 | 23.75444444 | 86.415 | 189.0 | 29.8145 | 219.1068 | -0.001138 | 14.1404 | 8.8837 |
| 18.0 | 23.75388889 | 86.4175 | 182.0 | 29.8083 | 134.3107 | -0.018212 | 13.7984 | 8.877 |
| 19.0 | 23.75416667 | 86.41555556 | 182.0 | 29.8005 | 219.7041 | 0.003415 | 13.8198 | 8.9108 |
| 20.0 | 23.75611111 | 86.41444444 | 165.0 | 29.6544 | 267.1512 | 0.013659 | 13.35 | 8.927 |

---

## 11. CSV Data Integrity & Point-in-Polygon Check
- **CSV Source**: `results/terrain/spatial_features.csv`
- **Total CSV Records**: `1,665`
- **Null / NaN Count**: `0` / `0`
- **Inf Count**: `0`
- **Physical Boundary Checks**:
  - Latitude: `23.746389°N` to `23.765000°N` (Valid)
  - Longitude: `86.412500°E` to `86.424444°E` (Valid)
  - Slope Range: `0.00°` to `37.26°` (Valid, within 0–90°)
  - Aspect Range: `0.00°` to `358.36°` (Valid, within 0–360°)
- **Spatial Point-in-Polygon Result**:
  - Points Inside Polygon: `1,665` (`100.00%`)
  - Points Outside Polygon: `0` (`0.00%`)
  - Verification: **100% of CSV records fall strictly within the Rajapur / South Jharia AOI boundary.**

---

## 12. CSV vs Raster Feature Cross-Check
The table below compares feature statistics between the extracted CSV dataset and the AOI-masked rasters:

| Feature | CSV_Mean | Raster_Mean | Diff_Mean | CSV_Min | Raster_Min | CSV_Max | Raster_Max | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| elevation | 204.9441 | 204.9441 | 0.0 | 134.0 | 134.0 | 236.0 | 236.0 | MATCH |
| slope | 6.7553 | 6.7553 | 0.0 | 0.0 | 0.0 | 37.2556 | 37.2556 | MATCH |
| aspect | 193.6669 | 193.6669 | 0.0 | 0.0 | 0.0 | 358.3563 | 358.3563 | MATCH |
| curvature | 0.0 | 0.0 | 0.0 | -0.0194 | -0.0194 | 0.0307 | 0.0307 | MATCH |
| roughness | 3.119 | 3.119 | 0.0 | 0.0 | 0.0 | 19.0367 | 19.0367 | MATCH |
| twi | 10.0424 | 10.0424 | 0.0 | 8.6416 | 8.6416 | 13.6461 | 13.6461 | MATCH |

**Conclusion**: Tabular features in `spatial_features.csv` match the underlying AOI-clipped terrain rasters with zero numerical error.

---

## 13. Generated Maps & Spatial Visualizations
All generated maps have been saved to `results/terrain/rajapur_validation/`:
1. `rajapur_aoi_validation.png` — Context DEM showing official AOI polygon boundary & CSV feature point locations.
2. `rajapur_elevation.png` — High-resolution elevation map clipped to AOI polygon (134 m to 236 m).
3. `rajapur_slope.png` — Morphological slope map clipped to AOI with top 20 steepest locations highlighted.
4. `rajapur_steep_slope.png` — Binary threshold map separating gentle/moderate terrain (<=20°) from steep terrain (>20°).

---

## 14. Quality Control Conclusions
- All 9 required input files exist, are readable, and are spatially synchronized.
- Raster transformation, cell alignment, resolution, CRS, and bounds are 100% verified.
- Spatial feature dataset `spatial_features.csv` contains zero NaNs, zero Infs, zero missing values, and 100% of points fall inside the AOI.
- Cross-check between tabular dataset and raster layers passed with 100% consistency.

---

## 15. Scientific Limitations & Disclaimers

> [!WARNING]
> **MORPHOLOGICAL SUSCEPTIBILITY DISCLAIMER**:
> The analysis describes terrain morphology and steepness within the Rajapur/South Jharia AOI. Steep slope is a morphological susceptibility indicator and does not by itself establish rockfall occurrence, probability, or operational hazard.

> [!IMPORTANT]
> **MODEL VALIDATION DISCLAIMER**:
> The underlying ML models in this project were trained/evaluated on synthetic benchmark datasets and are not validated here against observed Rajapur/South Jharia rockfall events.
