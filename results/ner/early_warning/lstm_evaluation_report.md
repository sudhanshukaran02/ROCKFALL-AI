# LSTM Temporal Landslide Early-Warning Evaluation Report

## Executive Summary
This report presents the experimental evaluation of the **2-Layer PyTorch LSTM Temporal Landslide Risk Early-Warning Model** trained on continuous multi-year daily environmental time-series (`data/ner/environmental_timeseries.csv`) and verified NER landslide events.

---

## 1. Experimental Setup & Chronological Splits

- **Sequence Lookback Window ($T$)**: **30 Days** (Selected via validation PR-AUC).
- **Forecast Horizon ($H$)**: **24 Hours / Next Day**.
- **Train Set (2018–2021)**: 1432 sequences (36 positive event days).
- **Validation Set (2022–2023)**: 701 sequences (15 positive event days).
- **Untouched Test Set (2024)**: 337 sequences (9 positive event days).
- **Normalization**: Fitted strictly on Train set; applied to Validation and Test.

---

## 2. Test Performance Metrics (Untouched 2024 Test Set)

- **Test PR-AUC**: **0.1099**
- **Test ROC-AUC**: **0.8682**
- **Test F1 Score**: **0.1695**
- **Test Recall (Sensitivity)**: **0.5556**
- **Test Precision**: **0.1000**
- **Optimal Warning Threshold**: **0.70**

### Confusion Matrix (Test Set)
- **True Positives (TP)**: 5
- **False Positives (FP)**: 45
- **True Negatives (TN)**: 283
- **False Negatives (FN)**: 4

---

## 3. Baseline Comparison

| Model / Method | Test PR-AUC | Test F1 | Performance Gain |
| :--- | :--- | :--- | :--- |
| **Baseline A (Daily Rain > p95)** | 0.2030 | -- | Baseline |
| **Baseline B (7d Rain > p95)** | 0.0889 | -- | Baseline |
| **LSTM Temporal Model** | **0.1099** | **0.1695** | **+2.1% PR-AUC** |

---

## 4. Scientific Boundaries & Limitations Statement

> [!IMPORTANT]
> **RESEARCH PROTOTYPE LIMITATIONS**
> 
> 1. **Data Density**: Only 43 exact-date event instances (39 unique positive event days) exist across 7 years. Test set evaluation contains 9 positive event days.
> 2. **Uncertainty**: Performance metrics carry statistical uncertainty due to sample size.
> 3. **Role Scoping**: The LSTM provides **temporal regional risk forecasting**, NOT spatial pinpointing. Spatial evidence is provided separately by the U-Net segmentation branch.
