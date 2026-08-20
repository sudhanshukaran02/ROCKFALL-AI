# Model A Calibration & Audit Report

> **Target Model:** Model A — Ground Instability / Landslide Susceptibility Model  
> **Dataset:** `data/dataset1.csv` (2,000 observations)  
> **Date:** August 20, 2026  
> **Status:** Audit Completed & Verified  

---

## 1. Executive Summary

A comprehensive audit and probability calibration analysis was performed on Model A. All 4 candidate algorithms (Logistic Regression, Random Forest, XGBoost, CatBoost) were evaluated across train, validation, and held-out test splits. 

- **Best Model:** `LogisticRegression` (Selected based on validation F1 score).
- **Test Performance:** Accuracy = 1.0000, Recall = 1.0000, F1-Score = 1.0000, ROC-AUC = 1.0000.
- **Brier Score (Uncalibrated):** `0.000020` (indicating exceptionally accurate and well-calibrated probabilities).
- **Probability Bimodal Distribution Cause:** `dataset1.csv` exhibits near-perfect linear separability in feature space. The scaled logistic regression log-odds magnitude $|w^T x + b| \gg 5$, pushing sigmoid probabilities $\sigma(z)$ to extreme values near 0.0 or 1.0.

---

## 2. Quantitative Model Metrics Comparison

All models were evaluated on the held-out test set (300 samples, 15% of dataset):

| Model Name | Validation F1 | Test Accuracy | Test Precision | Test Recall | Test F1-Score | Test ROC-AUC | Test Brier Score | Test Log-Loss |
|---|---|---|---|---|---|---|---|---|
| **Logistic Regression** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **0.000020** | **0.001634** |
| **Random Forest** | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.000020 | 0.000543 |
| **XGBoost** | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.000002 | 0.001415 |
| **CatBoost** | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.000000 | 0.000557 |

---

## 3. Probability Distribution & Extreme Value Investigation

### Why Probabilities Cluster Near 0.0 or 1.0
On the 300 test samples for Logistic Regression:
- **148 samples** have predicted probability $P < 0.01$ (True Negative class).
- **146 samples** have predicted probability $P > 0.99$ (True Positive class).
- Only **6 samples** fall in the intermediate transition zone $[0.01, 0.99]$.

#### Mathematical Root Cause Analysis
Logistic Regression computes probabilities as $P(y=1|x) = \frac{1}{1 + e^{-(w^T x + b)}}$. Inspection of the scaled feature weights reveals strong weights:

| Feature Name | Scaled Weight ($w$) | Directional Impact |
|---|---|---|
| `Vegetation_Cover` | **-1.6315** | Strong Protection (Reduces Instability) |
| `Proximity_to_Water` | **-1.5569** | Strong Protection (Greater distance reduces risk) |
| `Soil_Saturation` | **+1.5892** | Strong Instability Trigger |
| `Earthquake_Activity` | **+1.5435** | Strong Seismic Trigger |
| `Slope_Angle` | **+1.3185** | Strong Geotechnical Trigger |
| `Rainfall_mm` | **+1.0481** | Hydrological Trigger |

Because positive and negative ground instability instances in `dataset1.csv` are geographically and physical distinct, the linear predictor $w^T x + b$ regularly exceeds $+10$ or $-10$. Consequently, $\sigma(z)$ naturally approaches $1.0$ or $0.0$.

---

## 4. Probability Calibration Analysis

Probability calibration was conducted using the **Validation set ONLY** (300 samples) via Platt Scaling (`CalibratedClassifierCV(method='sigmoid')`) and Isotonic Regression (`CalibratedClassifierCV(method='isotonic')`). The test set was strictly held out for evaluation.

### Calibration Metric Comparison on Held-Out Test Data

| Calibration Method | Test Brier Score | Test Log-Loss | Calibration Notes |
|---|---|---|---|
| **Uncalibrated Logistic Regression** | **0.000020** | **0.001634** | Baseline fitted model |
| **Sigmoid Calibration (Platt)** | **0.000193** | **0.003412** | Fitted on Validation Set |
| **Isotonic Calibration** | **0.000000** | **0.000045** | Fitted on Validation Set |

### Key Findings & Visual Artifacts
- **Reliability Diagram:** The uncalibrated reliability curve aligns perfectly along the $y = x$ diagonal.
- **Visual Plots Saved:**
  - Reliability Diagram: [`results/model_A/calibration/model_A_calibration_curve.png`](file:///c:/Users/Sudhanshu%20Karan/Desktop/rockfall%20ai/results/model_A/calibration/model_A_calibration_curve.png)
  - Probability Distribution Comparison: [`results/model_A/calibration/model_A_prob_distribution.png`](file:///c:/Users/Sudhanshu%20Karan/Desktop/rockfall%20ai/results/model_A/calibration/model_A_prob_distribution.png)
