# Real Rajapur Spatial Rockfall Susceptibility Analysis Report

## 1. Objective
This report presents the real-terrain spatial rockfall susceptibility assessment for the **Rajapur / South Jharia Open Cast Mine** (BCCL, Dhanbad, Jharkhand). The analysis applies the pre-trained **Model A (Ground Instability Pipeline)** directly to the real 1-arcsecond SRTM terrain derivative dataset extracted across the 1.45 km² active mining AOI polygon.

> [!CAUTION]
> **NOT A CERTIFIED ROCKFALL HAZARD MAP**:
> This document and associated spatial maps represent a **prototype terrain-based rockfall susceptibility application of an un-calibrated ML model**. It is **NOT** a certified operational rockfall hazard map or safety directive.

---

## 2. Data Used
1. **Official AOI Boundary**: `scratch/rajapur_south_jharia_aoi.geojson` (`1.4503 km²`, WGS84 polygon).
2. **Spatial Feature Dataset**: `results/terrain/spatial_features.csv` (`1,665` valid spatial grid points).
3. **Real SRTM Terrain Derivatives**: Elevation, Slope, Aspect, Curvature, Roughness, TWI (`results/terrain/real/*.tif`).
4. **Historical Event Inventory**: `data/events/rajapur_instability_events.csv` (`10` documented historical events).

---

## 3. Model Used
- **Model Architecture**: `models/model_A_best.pkl` (Scikit-Learn Random Forest Classification Pipeline).
- **Training Context**: Model A was trained on synthetic benchmark datasets; it has **NOT** been retrained or modified during this spatial analysis step.

---

## 4. Model Input Features
Model A expects exactly **9 features** in the following exact order:
1. `Rainfall_mm` (Regional annual/monsoon baseline = 120.0 mm)
2. `Slope_Angle` (Mapped directly from pixel-level SRTM slope derivative, range: `0.00°` to `37.26°`)
3. `Soil_Saturation` (Regional baseline = 0.40)
4. `Vegetation_Cover` (Open-cast mine quarry baseline = 0.30)
5. `Earthquake_Activity` (Richter regional rating = 1.5)
6. `Proximity_to_Water` (Distance to pit water sump / Katri River = 1.0 km)
7. `Soil_Type_Gravel` (1 - Sandstone/overburden rock composition)
8. `Soil_Type_Sand` (0)
9. `Soil_Type_Silt` (0)

---

## 5. Spatial Prediction Method
Model A `predict_proba()` was evaluated across all 1,665 spatial grid points inside the Rajapur AOI polygon. Continuous instability probability values were mapped into official project risk tiers using standard thresholds:
- `P < 0.35` -> **LOW**
- `0.35 <= P < 0.65` -> **MODERATE**
- `0.65 <= P < 0.85` -> **HIGH**
- `P >= 0.85` -> **VERY HIGH**

---

## 6. Probability Distribution Summary
- **Total Valid Spatial Grid Points**: `1665`
- **Minimum Instability Probability**: `0.004279`
- **Maximum Instability Probability**: `0.097720`
- **Mean Instability Probability**: `0.009406`
- **Median Instability Probability**: `0.006276`

| total_spatial_points | mean_probability | median_probability | min_probability | max_probability | count_LOW | pct_LOW | count_MODERATE | pct_MODERATE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1665.0 | 0.009406 | 0.006276 | 0.004279 | 0.09772 | 1665.0 | 100.0 | 0.0 | 0.0 |

---

## 7. Risk-Class Distribution
- **LOW Risk (`P < 0.35`)**: `1665 points` (`100.00%`)
- **MODERATE Risk (`0.35 <= P < 0.65`)**: `0 points` (`0.00%`)
- **HIGH Risk (`0.65 <= P < 0.85`)**: `0 points` (`0.00%`)
- **VERY HIGH Risk (`P >= 0.85`)**: `0 points` (`0.00%`)

---

## 8. Terrain Morphology & Slope Comparison
The table below compares Model A susceptibility predictions against actual DEM slope angles:

| risk_class | point_count | mean_slope_deg | median_slope_deg | max_slope_deg | points_gt_20deg | points_gt_30deg |
| --- | --- | --- | --- | --- | --- | --- |
| LOW | 1665 | 6.76 | 4.45 | 37.26 | 93 | 16 |
| MODERATE | 0 | 0.0 | 0.0 | 0.0 | 0 | 0 |
| HIGH | 0 | 0.0 | 0.0 | 0.0 | 0 | 0 |
| VERY HIGH | 0 | 0.0 | 0.0 | 0.0 | 0 | 0 |

*Note: Steep slopes (>20° and >30°) are framed as terrain morphology indicators and NOT as proof of active rockfall occurrence.*

---

## 9. Historical Event Spatial Overlay
Overlaid `9` documented instability events from `data/events/rajapur_instability_events.csv` on the spatial susceptibility map:
- **Confirmed Rockfall (`EVT_RAJ_007`)**: April 2023 (`Lat: 23.753611°N`, `Lon: 86.416667°E`).
- **Bench Failures**: `EVT_RAJ_001`, `EVT_RAJ_010`.
- **Confirmed Slope Failures**: `EVT_RAJ_005`.
- **Ground Collapse & Subsidence**: `EVT_RAJ_004`, `EVT_RAJ_006`.

*Note: This layer represents an exploratory event overlay, NOT a formal statistical model validation, due to the small sample size of confirmed rockfall labels (N=1).*

---

## 10. Top Susceptibility Locations (Top 10 Display)
The top 10 highest susceptibility locations extracted from `results/rajapur/top_50_susceptibility_locations.csv`:

| rank | latitude | longitude | model_A_probability | risk_class | elevation | slope | aspect |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 23.75361111111112 | 86.41666666666667 | 0.09772 | LOW | 178.0 | 37.25556564331055 | 188.66673278808597 |
| 2 | 23.75388888888889 | 86.41611111111112 | 0.095115 | LOW | 172.0 | 36.910247802734375 | 215.10903930664065 |
| 3 | 23.75388888888889 | 86.41583333333334 | 0.080416 | LOW | 188.0 | 34.78622055053711 | 213.0736083984375 |
| 4 | 23.75361111111112 | 86.41694444444445 | 0.077507 | LOW | 178.0 | 34.324310302734375 | 174.0709991455078 |
| 5 | 23.75388888888889 | 86.4163888888889 | 0.068017 | LOW | 160.0 | 32.69840240478516 | 207.3910675048828 |
| 6 | 23.75555555555556 | 86.41444444444446 | 0.064883 | LOW | 176.0 | 32.11505126953125 | 252.7670440673828 |
| 7 | 23.756111111111117 | 86.41416666666667 | 0.062911 | LOW | 185.0 | 31.73440742492676 | 266.2522277832031 |
| 8 | 23.75583333333334 | 86.41444444444446 | 0.062556 | LOW | 168.0 | 31.664661407470703 | 258.2769470214844 |
| 9 | 23.75666666666667 | 86.41444444444446 | 0.061011 | LOW | 178.0 | 31.356922149658203 | 302.9539794921875 |
| 10 | 23.756388888888893 | 86.41416666666667 | 0.058383 | LOW | 185.0 | 30.816242218017575 | 284.5214538574219 |

---

## 11. Limitations & Boundaries
1. **Synthetic Training Origin**: Model A was trained on synthetic benchmark datasets and has not been fine-tuned on real Dhanbad geotechnical soil test data.
2. **Coarse DEM Resolution**: SRTM 1-arcsecond resolution (~30m) smooths sub-meter bench geometries and vertical pit walls.
3. **No Retraining / Retrained Labels**: Model predictions reflect prototype feature relationships, not verified rockfall occurrences.

---

## 12. Conclusion
The spatial application of Model A successfully maps terrain slope variability into continuous ground instability probability across the Rajapur AOI. The generated outputs provide a baseline prototype susceptibility framework ready for interactive visualization in the dashboard.
