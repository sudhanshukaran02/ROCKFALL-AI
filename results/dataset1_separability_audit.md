# Dataset 1 Separability & Target Generation Audit Report

> **Dataset Analyzed:** `data/dataset1.csv` (2,000 observations)  
> **Target Column:** `Landslide` (Binary: 0 or 1)  
> **Date:** August 20, 2026  
> **Status:** AUDIT COMPLETED — Synthetic Benchmark Dataset Confirmed  

---

## 1. Executive Summary

An in-depth separability and target generation audit was performed on `data/dataset1.csv`. The audit revealed that **Dataset 1 is a synthetically generated benchmark dataset featuring perfect, non-overlapping threshold splits across multiple independent features**.

- **Key Finding:** Four individual features (`Soil_Saturation`, `Earthquake_Activity`, `Vegetation_Cover`, `Proximity_to_Water`) exhibit **zero numerical overlap** between `Landslide=0` and `Landslide=1`.
- **Single-Feature Accuracy:** A simple 1-rule decision stump on `Earthquake_Activity > 4.00` achieves **100.00% Accuracy, 100.00% Recall, and 100.00% F1-Score**.
- **Implication:** The near-perfect performance of ML models (100% accuracy across Logistic Regression, Random Forest, XGBoost, CatBoost) is **not** due to advanced AI modeling, but because the dataset was generated using a simple deterministic step function.

---

## 2. Feature Distribution & Range Analysis (Class 0 vs Class 1)

| Feature Name | Class 0 Min | Class 0 Mean | Class 0 Max | Class 1 Min | Class 1 Mean | Class 1 Max | Overlap Range | Separability Verdict |
|---|---|---|---|---|---|---|---|---|
| `Soil_Saturation` | 0.0007 | 0.2825 | **0.5997** | **0.6001** | 0.7982 | 0.9988 | **0.0000** | **100% Perfectly Separable** |
| `Earthquake_Activity` | 0.0016 | 1.9742 | **3.9928** | **4.0001** | 5.2353 | 6.4987 | **0.0000** | **100% Perfectly Separable** |
| `Vegetation_Cover` | **0.5006** | 0.7481 | 0.9998 | 0.1000 | 0.2976 | **0.4997** | **0.0000** | **100% Perfectly Separable** |
| `Proximity_to_Water` | **1.0002** | 1.5029 | 1.9996 | 0.0007 | 0.5008 | **0.9993** | **0.0000** | **100% Perfectly Separable** |
| `Slope_Angle` | 5.0039 | 17.7174 | 29.9829 | 25.0392 | 42.2534 | 59.9667 | 4.9437 | 92.25% Separable |
| `Rainfall_mm` | 50.0362 | 127.1113 | 199.8514 | 150.2019 | 226.2656 | 299.9191 | 49.6495 | 84.35% Separable |
| `Soil_Type_Gravel` | 0.0000 | 0.5170 | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | Class 1 has 0 Gravel |
| `Soil_Type_Sand` | 0.0000 | 0.4830 | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | Class 1 has 0 Sand |
| `Soil_Type_Silt` | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.5220 | 1.0000 | 0.0000 | Class 0 has 0 Silt |

---

## 3. Single-Feature Decision Stumps (Depth=1)

Training simple 1-rule decision trees (`max_depth=1`) on individual features confirms that multiple individual features can classify the target with 100% accuracy:

| Rank | Feature | Split Rule | Accuracy | Recall | F1-Score |
|---|---|---|---|---|---|
| **1** | `Earthquake_Activity` | `IF Earthquake_Activity > 3.9964 THEN Landslide=1 ELSE 0` | **100.00%** | **1.0000** | **1.0000** |
| **2** | `Soil_Saturation` | `IF Soil_Saturation > 0.5999 THEN Landslide=1 ELSE 0` | **100.00%** | **1.0000** | **1.0000** |
| **3** | `Vegetation_Cover` | `IF Vegetation_Cover <= 0.5002 THEN Landslide=1 ELSE 0` | **100.00%** | **1.0000** | **1.0000** |
| **4** | `Proximity_to_Water` | `IF Proximity_to_Water <= 0.9998 THEN Landslide=1 ELSE 0` | **100.00%** | **1.0000** | **1.0000** |
| **5** | `Slope_Angle` | `IF Slope_Angle > 29.9869 THEN Landslide=1 ELSE 0` | 92.25% | 0.8450 | 0.9160 |
| **6** | `Rainfall_mm` | `IF Rainfall_mm > 199.9764 THEN Landslide=1 ELSE 0` | 84.35% | 0.6870 | 0.8145 |

---

## 4. Visual Evidence Artifacts

- **Feature Distribution Plot:** [`results/separability/dataset1_feature_distributions.png`](file:///c:/Users/Sudhanshu%20Karan/Desktop/rockfall%20ai/results/separability/dataset1_feature_distributions.png)
- **Decision Boundary Plot:** [`results/separability/dataset1_decision_boundary.png`](file:///c:/Users/Sudhanshu%20Karan/Desktop/rockfall%20ai/results/separability/dataset1_decision_boundary.png)
