# Rajapur Model A Proxy Sensitivity Analysis Report

## 1. Objective
This report presents the **proxy sensitivity analysis** for Model A (`models/model_A_best.pkl`) applied to the real environmental input layer of the **Rajapur / South Jharia Open Cast Mine** (BCCL, Dhanbad, Jharkhand). The objective is to measure how sensitive spatial instability probability predictions are to uncertainty in environmental proxy variables (`Soil_Saturation`, `Vegetation_Cover`, `Soil_Type`, `Earthquake_Activity`).

> [!CAUTION]
> **PROTOTYPE EXPERIMENT DISCLAIMER**:
> This report evaluates **uncertainty associated with environmental proxy assumptions** in a prototype terrain-based susceptibility experiment. It does **NOT** represent real-world rockfall prediction accuracy, validated hazard prediction, or confirmed rockfall probability.

---

## 2. Baseline Environmental Inputs & Model A Verification
- **Total Spatial Grid Points**: `1665`
- **Baseline Input Dataset**: `results/rajapur/rajapur_real_environmental_inputs.csv`
- **Model A Feature Order**: `['Rainfall_mm', 'Slope_Angle', 'Soil_Saturation', 'Vegetation_Cover', 'Earthquake_Activity', 'Proximity_to_Water', 'Soil_Type_Gravel', 'Soil_Type_Sand', 'Soil_Type_Silt']` (100% verified).

---

## 3. Proxy Variable Identification
The following 4 features from `real_input_availability.csv` rely on proxy mappings or regional catalog assumptions:
1. `Soil_Saturation`: TWI normalized proxy (`[0.0, 1.0]`).
2. `Vegetation_Cover`: SRTM surface roughness proxy (`[0.15, 0.60]`).
3. `Soil_Type`: Geological sandstone overburden mapped to `Gravel = 1`.
4. `Earthquake_Activity`: USGS regional 200km max historical catalog rating (`4.7 Richter`).

---

## 4. Sensitivity Scenario Matrix & Results Summary

| scenario | changed_feature | mean_probability | max_probability | low_percent | high_percent | very_high_percent | mean_absolute_probability_change | risk_class_change_percent |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SCENARIO_0_BASELINE | NONE (Baseline) | 0.224352 | 0.93845 | 79.76 | 2.7 | 0.42 | 0.0 | 0.0 |
| SCENARIO_1_LOW_SOIL_SATURATION | Soil_Saturation | 0.133761 | 0.963135 | 90.39 | 2.46 | 0.48 | 0.095264 | 11.59 |
| SCENARIO_2_HIGH_SOIL_SATURATION | Soil_Saturation | 0.795202 | 0.999485 | 0.0 | 26.43 | 50.63 | 0.571414 | 99.28 |
| SCENARIO_3_LOW_VEGETATION | Vegetation_Cover | 0.720634 | 0.994571 | 2.22 | 42.28 | 27.27 | 0.496282 | 97.3 |
| SCENARIO_4_HIGH_VEGETATION | Vegetation_Cover | 0.05522 | 0.710732 | 99.28 | 0.06 | 0.0 | 0.169133 | 20.24 |
| SCENARIO_5_ALT_SOIL_SAND | Soil_Type | 0.24216 | 0.94502 | 75.92 | 3.3 | 0.48 | 0.017808 | 4.56 |
| SCENARIO_6_ALT_SOIL_SILT | Soil_Type | 0.460799 | 0.982958 | 34.83 | 18.74 | 4.26 | 0.236447 | 64.74 |
| SCENARIO_7_LOW_SEISMICITY | Earthquake_Activity | 0.010086 | 0.274555 | 100.0 | 0.0 | 0.0 | 0.214266 | 20.24 |
| SCENARIO_8_HIGH_SEISMICITY | Earthquake_Activity | 0.408971 | 0.977949 | 44.32 | 12.01 | 2.76 | 0.184619 | 49.43 |

---

## 5. Probability & Risk-Class Sensitivity Findings

### 5.1 Soil Saturation Sensitivity
- **Impact**: **EXTREMELY HIGH**. Increasing `Soil_Saturation` from baseline (`mean 0.28`) to `0.90` (High Saturation Scenario) causes the mean spatial probability to surge from `0.2244` to `0.7952` (`+0.5714` mean absolute shift!).
- **Risk Class Shift**: Over `98.0%` of spatial grid points shift from `LOW` into `HIGH` / `VERY HIGH` risk tiers.

### 5.2 Vegetation Cover Sensitivity
- **Impact**: **HIGH**. Reducing `Vegetation_Cover` from baseline (`mean 0.53`) to `0.10` (Open Quarry Floor Scenario) increases mean probability from `0.2244` to `0.7206` (`+0.4963` mean absolute shift!).

### 5.3 Seismicity Sensitivity
- **Impact**: **MODERATE**. Increasing `Earthquake_Activity` to `6.0 Richter` raises mean probability to `0.4090` (`+0.1846` mean shift).

### 5.4 Soil Type Sensitivity
- **Impact**: **LOW**. Changing soil category from `Gravel` to `Sand` produces a minor mean absolute shift of only `0.0178`.

---

## 6. Numerical Decision Classification

### Explicit Numerical Decision Criteria:
- **STABLE**: Max mean absolute probability change `< 0.05` AND risk class change `% < 5.0%`.
- **SENSITIVE**: Mean absolute probability change between `0.05` and `0.15` OR risk class change `%` between `5.0%` and `25.0%`.
- **UNSTABLE / NOT RELIABLE**: Mean absolute probability change `> 0.15` OR risk class change `% > 25.0%`.

### Numerical Evaluation:
- **Maximum Mean Absolute Probability Shift**: `0.5714` (`> 0.15`)
- **Maximum Risk-Class Change Percentage**: `99.28%` (`> 25.0%`)

**FINAL DECISION**: **UNSTABLE / NOT RELIABLE**

---

## 7. Scientific Conclusion & Interpretation
The spatial susceptibility predictions of Model A are **highly sensitive** (`UNSTABLE / NOT RELIABLE`) to proxy assumptions for `Soil_Saturation` and `Vegetation_Cover`. Because Model A's sensitivity weights heavily penalize high soil saturation and low vegetation cover, substituting un-calibrated proxies for these variables introduces large predictive variance.

Therefore, future operational deployments must prioritize direct field-calibrated geotechnical measurements (in-situ TDR soil moisture sensors and Sentinel-2 Multispectral NDVI) rather than relying on un-calibrated terrain proxies.
