# Model B Audit & Imbalance Handling Report

> **Target Model:** Model B — Meteorological Risk Model  
> **Dataset:** `data/dataset2.csv` (5,000 observations)  
> **Date:** August 20, 2026  
> **Status:** Audit Completed & Verified  

---

## 1. Executive Summary

Model B evaluates multi-class meteorological risk tiers (`Low`, `Moderate`, `High`, `Very High`) under severe class imbalance. A comprehensive audit verified model selection criteria, resample partitioning, class probability behavior, and held-out test set performance.

- **Best Model:** `XGBoost (SMOTE)` (Selected based on validation Macro F1 score of 1.0000).
- **Test Performance:** Macro F1 = 1.0000, Weighted F1 = 1.0000, Balanced Accuracy = 1.0000, Accuracy = 1.0000.
- **Class Probabilities Behavior:** All predicted class probability vectors sum strictly to 1.0 across all samples.
- **Resampling Verification:** SMOTE was applied **STRICTLY to the Training split (`X_train`)**, ensuring zero resampling leakage into validation or test data.

---

## 2. Quantitative Model Performance Comparison

All models were evaluated on the held-out test set (750 samples, 15% of dataset):

| Model Name | Validation Macro F1 | Test Macro F1 | Test Weighted F1 | Test Balanced Acc | Test Accuracy | Per-Class Recalls (Low / Mod / High / VeryHigh) |
|---|---|---|---|---|---|---|
| **Logistic Regression (Class-Wtd)** | 0.5428 | 0.6828 | 0.8946 | 0.8682 | 0.8707 | 0.8752 / 0.8200 / 0.7778 / 1.0000 |
| **Random Forest (Class-Wtd)** | 0.8335 | 0.9917 | 0.9959 | 0.9850 | 0.9960 | 1.0000 / 0.9400 / 1.0000 / 1.0000 |
| **CatBoost (Auto-Weighted)** | 0.9004 | 0.9947 | 0.9974 | 0.9993 | 0.9973 | 0.9971 / 1.0000 / 1.0000 / 1.0000 |
| **XGBoost (SMOTE)** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000 / 1.0000 / 1.0000 / 1.0000** |

---

## 3. Imbalance Handling & SMOTE Verification Audit

### Class Imbalance Baseline in Dataset 2
- Total Dataset: 5,000 observations
- `Low` Risk: 4,591 (91.82%)
- `Moderate` Risk: 334 (6.68%)
- `High` Risk: 63 (1.26%)
- `Very High` Risk: 12 (0.24%)

### Split & Resampling Verification Checklist
1. **70% Training Set (`X2_train`):** 3,500 observations
   - Class Breakdown before SMOTE: `Low`: 3,214, `Moderate`: 234, `High`: 44, `Very High`: 8.
   - SMOTE Resampling (`k_neighbors=1`): Oversampled minority classes strictly within `X2_train` to 3,214 samples each (Total: 12,856 samples).
2. **15% Validation Set (`X2_val`):** 750 observations
   - Class Breakdown: `Low`: 688, `Moderate`: 50, `High`: 10, `Very High`: 2.
   - Resampling Status: **UNTOUCHED (0% Resampling)**. Evaluated on original imbalanced distribution.
3. **15% Test Set (`X2_test`):** 750 observations
   - Class Breakdown: `Low`: 689, `Moderate`: 50, `High`: 9, `Very High`: 2.
   - Resampling Status: **UNTOUCHED (0% Resampling)**. Evaluated on original imbalanced distribution.

---

## 4. Multi-Class Probability Calibration & Behavior

- **Probability Normalization:** Verified that $\sum_{k=1}^4 P(\text{Class}_k) = 1.0000$ for 100% of test samples.
- **Mean Classification Entropy:** `0.0058` for `XGBoost (SMOTE)`, indicating decisive and sharp class boundaries between weather risk levels (`Temperature`, `Humidity`, `Precipitation`, `Soil Moisture`, `Elevation`).
- **Mean Maximum Probability:** `0.9990` across test set predictions.
