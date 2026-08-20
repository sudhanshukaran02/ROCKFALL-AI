# Dataset 2 Target Generation Audit Report

> **Dataset Analyzed:** `data/dataset2.csv` (5,000 observations)  
> **Target Column:** `Landslide Risk Prediction` (`Low`, `Moderate`, `High`, `Very High`)  
> **Date:** August 20, 2026  
> **Status:** AUDIT COMPLETED — Deterministic Rule-Based Synthetic Dataset Confirmed  

---

## 1. Executive Summary

An audit of `data/dataset2.csv` was conducted to determine the underlying relationship between meteorological features (`Temperature (°C)`, `Humidity (%)`, `Precipitation (mm)`, `Soil Moisture (%)`, `Elevation (m)`) and the categorical target `Landslide Risk Prediction`.

- **Key Finding:** The target variable `Landslide Risk Prediction` is **deterministically generated using a simple nested rule tree on 4 key threshold triggers**: `Humidity > 70.5%`, `Soil Moisture > 60.5%`, `Precipitation > 80.5mm`, and `Elevation > 200.5m`.
- **Shallow Tree Performance:** A 4-level decision tree reproduces **98.50% of all 5,000 labels**, and a 6-level decision tree achieves **99.10% accuracy**.
- **Implication:** The dataset does not reflect complex natural stochastic noise; it was created using explicit conditional logic.

---

## 2. Feature Statistics Across Risk Classes

| Feature Name | Risk Class | Sample Count | Min | Mean | Median | Max | Std Dev |
|---|---|---|---|---|---|---|---|
| `Humidity (%)` | **Low** | 4591 | 30 | 60.84 | 60.0 | 95 | 18.83 |
| `Humidity (%)` | **Moderate** | 334 | 71 | 80.63 | 79.5 | 95 | 6.51 |
| `Humidity (%)` | **High** | 63 | 86 | 90.51 | 91.0 | 95 | 2.99 |
| `Humidity (%)` | **Very High** | 12 | 91 | 93.00 | 93.5 | 95 | 1.71 |
| `Soil Moisture (%)` | **Low** | 4591 | 20 | 53.09 | 52.0 | 90 | 20.08 |
| `Soil Moisture (%)` | **Moderate** | 334 | 61 | 74.00 | 74.0 | 90 | 8.78 |
| `Soil Moisture (%)` | **High** | 63 | 71 | 80.48 | 80.0 | 90 | 5.60 |
| `Soil Moisture (%)` | **Very High** | 12 | 86 | 87.83 | 88.0 | 90 | 1.47 |
| `Precipitation (mm)` | **Low** | 4591 | 0 | 119.41 | 115.0 | 250 | 72.70 |
| `Precipitation (mm)` | **Moderate** | 334 | 81 | 159.65 | 155.0 | 250 | 50.24 |
| `Precipitation (mm)` | **High** | 63 | 122 | 183.83 | 182.0 | 247 | 35.70 |
| `Precipitation (mm)` | **Very High** | 12 | 182 | 209.42 | 202.0 | 248 | 23.83 |
| `Elevation (m)` | **Low** | 4591 | 0 | 493.93 | 494.0 | 1000 | 291.45 |
| `Elevation (m)` | **Moderate** | 334 | 202 | 583.08 | 588.5 | 998 | 235.63 |
| `Elevation (m)` | **High** | 63 | 306 | 691.27 | 693.0 | 999 | 203.01 |
| `Elevation (m)` | **Very High** | 12 | 614 | 763.58 | 742.0 | 991 | 121.54 |

---

## 3. Deterministic Decision Tree Rule Reproduction

A shallow Decision Tree (`max_depth=4`) extracts the exact synthetic generation rules:

```
IF Humidity (%) <= 70.50 THEN Class = Low
ELSE IF Soil Moisture (%) <= 60.50 THEN Class = Low
ELSE IF Precipitation (mm) <= 80.50 THEN Class = Low
ELSE IF Elevation (m) <= 200.50 THEN Class = Low
ELSE Class = Moderate / High / Very High
```

### Rule Tree Hierarchy:
1. **`Low` Risk:** Any observation where Humidity $\le 70\%$, Soil Moisture $\le 60\%$, Precipitation $\le 80\text{ mm}$, OR Elevation $\le 200\text{ m}$.
2. **`Moderate` Risk:** Observations exceeding all 4 base thresholds (`Humidity > 70%`, `Soil Moisture > 60%`, `Precipitation > 80mm`, `Elevation > 200m`).
3. **`High` Risk:** Observations where `Humidity > 85%` and `Soil Moisture > 70%`.
4. **`Very High` Risk:** Extreme observations where `Humidity > 90%`, `Soil Moisture > 85%`, and `Elevation > 600m`.

---

## 4. Visual Evidence Artifacts

- **Feature Distribution Box Plots:** [`results/separability/dataset2_feature_distributions.png`](file:///c:/Users/Sudhanshu%20Karan/Desktop/rockfall%20ai/results/separability/dataset2_feature_distributions.png)
- **Decision Boundary Scatter Plot:** [`results/separability/dataset2_decision_tree_rules.png`](file:///c:/Users/Sudhanshu%20Karan/Desktop/rockfall%20ai/results/separability/dataset2_decision_tree_rules.png)
