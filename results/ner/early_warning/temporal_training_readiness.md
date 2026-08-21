# Temporal Training Readiness Evaluation: Phase 3B

## Executive Summary
This report evaluates whether the multi-year environmental time-series (`data/ner/environmental_timeseries.csv`) and authoritative landslide event inventory (`data/ner/landslide_events.csv`) justify immediate training of a PyTorch LSTM network.

> [!IMPORTANT]
> **CLASSIFICATION RESULT**: **`READY FOR FURTHER DATA COLLECTION`**
>
> Although we have successfully compiled a 7-year multi-variable environmental dataset (2,557 daily rows) and 15 georeferenced NER landslide events, **12 positive event timesteps across 2,557 days ($0.47\%$ positive ratio) is currently insufficient for deep learning sequence generalization.**
>
> In accordance with strict guidelines: **No LSTM training will be performed until further event instances ($\ge 50-100$ positive event days) are compiled.**

---

## 1. Readiness Audit Metrics

| Metric | Measured Value | Requirement for Supervised LSTM Training | Readiness Status |
| :--- | :--- | :--- | :--- |
| **Environmental Timeline** | 2018-01-01 to 2024-12-31 (7 Years) | $\ge 3 - 5$ Years | **PASS (EXCELLENT)** |
| **Daily Environmental Rows** | 2,557 continuous daily timesteps | $\ge 1,000$ timesteps | **PASS (EXCELLENT)** |
| **Missing Environmental Dates** | 0 missing dates ($100\%$ complete) | 0 missing dates | **PASS (EXCELLENT)** |
| **Rolling Rainfall Features** | 1d, 3d, 7d, 14d, 30d (No lookahead) | Computed without leakage | **PASS (EXCELLENT)** |
| **Georeferenced Landslide Events** | 15 authoritative events | $\ge 50 - 100$ events | **NEEDS EXPANSION** |
| **Events with Exact Daily Dates** | 12 precise daily events | $\ge 50$ precise daily events | **NEEDS EXPANSION** |
| **Positive Class Ratio** | $12 / 2557 = 0.47\%$ | $\ge 2.0 - 5.0\%$ | **EXTREME SPARSITY** |
| **Chronological Train/Val/Test Split** | 2018-2022 (Train) / 2023 (Val) / 2024 (Test) | Chronological non-overlapping | **PASS (STRUCTURE READY)** |

---

## 2. Temporal Merge & Labeling Protocol Design

When additional incident dates are ingested, the temporal dataset will be merged as follows:

```csv
date,precipitation,temp_mean,temp_min,temp_max,relative_humidity,rainfall_1d,rainfall_3d,rainfall_7d,rainfall_14d,rainfall_30d,terrain_susceptibility,spatial_evidence,risk_index,event_label
2022-06-29,145.2,24.5,20.1,28.2,95.0,145.2,280.4,410.2,590.1,890.2,0.65,0.40,0.85,0
2022-06-30,210.5,23.8,19.5,26.5,98.0,210.5,412.5,580.4,750.8,1050.4,0.65,0.40,0.92,1  <-- Tupul Event
2022-07-01,85.2,24.1,20.0,27.0,94.0,85.2,440.9,610.2,800.5,1100.2,0.65,0.40,0.78,0
```

### Labeling Rules:
- `event_label = 1`: Exact date of verified landslide event occurrence.
- `event_label = 0`: Verified background non-event day.
- **Pre-Event Warning Window**: Optional $t-1$ to $t-2$ pre-warning target buffer for 24h-48h lead-time forecasting.

---

## 3. Scientific Justification for Deferring LSTM Training

1. **Overfitting Risk**: Training a 2-layer LSTM network with 64 hidden units on only 12 positive event days across 2,557 steps would cause the optimizer to memorize those 12 specific rainfall peaks rather than learning general non-linear slope failure kinetics.
2. **False Generalization**: Claiming early-warning accuracy on an undersampled positive set would violate scientific standards.
3. **Data Integrity**: Refraining from training until $\ge 50-100$ verified event dates are compiled ensures that future LSTM metrics (ROC-AUC, PR-AUC, lead time) are statistically valid.
