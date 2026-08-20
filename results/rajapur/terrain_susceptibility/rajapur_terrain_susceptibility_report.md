# Real-Terrain Susceptibility Analysis Report — Rajapur / South Jharia

## 1. Objective
This report documents the transparent **Rajapur Real-Terrain Instability Susceptibility Index** developed for the **Rajapur / South Jharia Open Cast Coal Mine** (BCCL, Dhanbad, Jharkhand). The analysis is derived exclusively from 1-arcsecond SRTM DEM terrain derivatives over the official 1.45 km² mining AOI polygon.

> [!CAUTION]
> **PROTOTYPE SUSCEPTIBILITY INDEX DISCLAIMER**:
> The index is a transparent prototype morphological susceptibility indicator derived from terrain variables. It is **NOT** a probability, **NOT** a calibrated rockfall prediction model, and **NOT** a certified geotechnical hazard assessment.

---

## 2. Study Area
- **Location**: Rajapur / South Jharia Open Cast Mine, Dhanbad, Jharkhand, India.
- **Official AOI Area**: `1.4503 km²` (`scratch/rajapur_south_jharia_aoi.geojson`).
- **Spatial Grid Points**: `1665 valid pixels` (`30m x 30m` resolution).

---

## 3. Data Sources
- **Digital Elevation Model**: 1-arcsecond SRTM DEM (`data/mine_dem.tif`).
- **Terrain Derivatives**: Elevation, Slope, Aspect, Curvature, Roughness, TWI (`results/terrain/real/*.tif`).
- **Spatial Dataset**: `results/terrain/spatial_features.csv`.
- **Historical Event Inventory**: `data/events/rajapur_instability_events.csv` (Used for spatial context only).

---

## 4. SRTM Terrain Variables & Normalization
Each terrain variable is normalized to a `0.0 - 1.0` susceptibility component using robust **P5-P95 percentile clipping**:

Normalized Value = clip((Value - P5) / (P95 - P5), 0.0, 1.0)

- **Slope (`Slope_Angle`)**: P5 = 1.01°, P95 = 20.79°. Greater slope represents greater morphological steepness.
- **Curvature Magnitude (`Curvature_Abs`)**: P5 = 0.0000, P95 = 0.0114. Absolute curvature |Curvature| represents morphological slope breaks.
- **Roughness (`Roughness`)**: P5 = 0.67, P95 = 9.10. Greater roughness represents complex surface macro-texture.
- **Topographic Wetness Index (`TWI`)**: P5 = 9.07, P95 = 11.35. Greater TWI represents potential surface drainage accumulation.

---

## 5. Primary Susceptibility Index Formula & Weight Selection

Terrain Susceptibility Index = 0.25 * slope_norm + 0.25 * curvature_abs_norm + 0.25 * roughness_norm + 0.25 * twi_norm

> [!NOTE]
> The equal weights (`0.25 / 0.25 / 0.25 / 0.25`) were specified for transparency and were **NOT** learned from observed rockfall events.

---

## 6. Susceptibility Class Distribution
- **VERY LOW (`0.00 - 0.20`)**: `227 pixels` (`13.63%`)
- **LOW (`0.20 - 0.40`)**: `1097 pixels` (`65.89%`)
- **MODERATE (`0.40 - 0.60`)**: `241 pixels` (`14.47%`)
- **HIGH (`0.60 - 0.80`)**: `100 pixels` (`6.01%`)
- **VERY HIGH (`0.80 - 1.00`)**: `0 pixels` (`0.00%`)

---

## 7. Slope Threshold Analysis
- **Slope > 20° (Steep Terrain)**: `93 pixels` (`5.59%` of AOI, Mean Index: `0.6433`)
- **Slope > 30° (Very Steep Terrain)**: `16 pixels` (`0.96%` of AOI, Mean Index: `0.6516`)
- **Slope > 40° (Extreme Precipitous Slopes)**: `0 pixels` (`0.00%` of AOI)

---

## 8. Historical Event Spatial Overlay Context
Overlaid 10 historical events from `data/events/rajapur_instability_events.csv`:
- **Confirmed April 2023 Rockfall (`EVT_RAJ_007`)**: Index = `0.7000` (Class: `HIGH`, Slope: `37.3°`).
- **Event Class Breakdown**: `{'VERY LOW': 1, 'LOW': 3, 'MODERATE': 0, 'HIGH': 5, 'VERY HIGH': 0}`

> [!IMPORTANT]
> The historical event inventory is used for **spatial context only and NOT for statistical model validation** (such as ROC-AUC or Precision/Recall) because only 1 confirmed rockfall event exists.

---

## 9. Comprehensive Terrain Statistics

| feature | min | P5 | median | mean | P95 | max | std |
| --- | --- | --- | --- | --- | --- | --- | --- |
| elevation | 134.0 | 160.0 | 207.0 | 204.944144 | 228.0 | 236.0 | 18.603495 |
| slope | 0.0 | 1.013694 | 4.445918 | 6.75532 | 20.789266 | 37.255566 | 6.403425 |
| curvature | -0.019351 | -0.00683 | -0.0 | 3.1e-05 | 0.007968 | 0.030733 | 0.005149 |
| roughness | 0.0 | 0.666667 | 2.060804 | 3.119005 | 9.102977 | 19.036676 | 2.877491 |
| twi | 8.641626 | 9.067319 | 9.962476 | 10.042373 | 11.354038 | 13.646056 | 0.716835 |
| curvature_magnitude | 0.0 | 0.0 | 0.002277 | 0.00357 | 0.011383 | 0.030733 | 0.003709 |
| terrain_susceptibility_index | 0.144925 | 0.177431 | 0.273822 | 0.316133 | 0.609379 | 0.76323 | 0.136258 |

---

## 10. Weight Sensitivity Analysis

| scenario | weights | mean_index | median_index | max_index | high_susceptibility_pct |
| --- | --- | --- | --- | --- | --- |
| Scenario A (Slope-Heavy) | Slope=0.40, Curv=0.20, Rough=0.20, TWI=0.20 | 0.3085 | 0.2467 | 0.8098 | 9.25 |
| Scenario B (Equal-Weight) | Slope=0.25, Curv=0.25, Rough=0.25, TWI=0.25 | 0.3161 | 0.2738 | 0.7632 | 6.01 |
| Scenario C (Moisture-Heavy) | Slope=0.20, Curv=0.20, Rough=0.20, TWI=0.40 | 0.3362 | 0.318 | 0.6274 | 1.86 |

- **Spatial Stability Classification**: **SENSITIVE**

---

## 11. Top 10 High-Susceptibility Locations

| rank | latitude | longitude | terrain_susceptibility_index | susceptibility_class | elevation | slope | aspect |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 23.75416666666667 | 86.41722222222224 | 0.76323 | HIGH | 154.0 | 20.175296783447266 | 124.13047790527344 |
| 2 | 23.75416666666667 | 86.41611111111112 | 0.762217 | HIGH | 159.0 | 23.230772018432617 | 232.2550506591797 |
| 3 | 23.75583333333334 | 86.41388888888889 | 0.761544 | HIGH | 203.0 | 20.91580581665039 | 262.7079467773437 |
| 4 | 23.755000000000003 | 86.41527777777779 | 0.760587 | HIGH | 150.0 | 23.183801651000977 | 231.4663848876953 |
| 5 | 23.757222222222225 | 86.415 | 0.750489 | HIGH | 186.0 | 22.695905685424805 | 339.6464233398437 |
| 6 | 23.75666666666667 | 86.41472222222224 | 0.75 | HIGH | 163.0 | 26.89157485961914 | 314.54266357421875 |
| 7 | 23.75388888888889 | 86.4163888888889 | 0.75 | HIGH | 160.0 | 32.69840240478516 | 207.3910675048828 |
| 8 | 23.756388888888893 | 86.41444444444446 | 0.75 | HIGH | 166.0 | 30.357908248901367 | 288.5105285644531 |
| 9 | 23.754722222222227 | 86.41527777777779 | 0.75 | HIGH | 160.0 | 28.542200088500977 | 218.0192108154297 |
| 10 | 23.754722222222227 | 86.41805555555557 | 0.75 | HIGH | 175.0 | 24.685998916625977 | 134.00833129882812 |

---

## 12. Quality Control & Scientific Interpretation
- **QC Status**: **PASSED** (0 NaNs, 0 Infs, 100% points inside AOI).
- **ML Retraining**: `NO`.
- **InSAR Data**: `NOT USED`.
- **Conclusion**: The Rajapur Real-Terrain Susceptibility Index provides a transparent, repeatable morphological baseline that highlights steep quarry highwalls and structural slope breaks across the mine area.
