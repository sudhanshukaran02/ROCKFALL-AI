# Updated LSTM Early Warning Architecture Design

## Executive Summary
This document provides the updated architectural specification and dataset split protocol for the **Phase 3 Temporal LSTM Early Warning Module**, incorporating the multi-year environmental time-series (`data/ner/environmental_timeseries.csv`) and real event inventory (`data/ner/landslide_events.csv`).

> [!NOTE]
> **Implementation Status**: **DESIGNED & PREPARED — UNTRAINED**
> 
> In accordance with Phase 3B scientific directives, this model will **NOT be trained** until the real event inventory is expanded to $\ge 50-100$ precise daily event instances to prevent extreme positive class overfitting.

---

## 1. Multi-Year Input Sequence Specification

- **Multi-Year Environmental Series**: 2,557 continuous daily rows (2018-01-01 to 2024-12-31).
- **Sequence Lookback Window ($T$)**: 14 to 30 days of past daily observations.
- **Forecast Horizon ($H$)**: 24 to 72 hours into the future.
- **Input Feature Vector ($\mathbf{x}_t \in \mathbb{R}^9$)**:
  1. `precipitation`: Daily rainfall (mm/day)
  2. `rainfall_3d`: 3-day cumulative rainfall (mm)
  3. `rainfall_7d`: 7-day cumulative rainfall (mm)
  4. `rainfall_14d`: 14-day cumulative rainfall (mm)
  5. `rainfall_30d`: 30-day cumulative rainfall (mm)
  6. `temperature_mean`: Daily mean temperature ($^\circ\text{C}$)
  7. `relative_humidity`: Relative humidity (%)
  8. `s_terrain`: Static DEM terrain susceptibility index ($[0, 1]$)
  9. `e_spatial`: U-Net spatial landslide probability ($[0, 1]$)

---

## 2. PyTorch 2-Layer LSTM Network Architecture

```
Input Sequence Tensor: (Batch, T=14..30 days, F=9 features)
                          │
                          ▼
       ┌────────────────────────────────────┐
       │   LSTM Layer 1 (64 hidden units)   │  (Dropout = 0.2, Return Sequences = True)
       └─────────────────┬──────────────────┘
                         │
                         ▼
       ┌────────────────────────────────────┐
       │   LSTM Layer 2 (32 hidden units)   │  (Dropout = 0.2, Return Sequences = False)
       └─────────────────┬──────────────────┘
                         │
                         ▼
       ┌────────────────────────────────────┐
       │   Linear Dense Layer 1 (16 units)  │  (ReLU Activation)
       └─────────────────┬──────────────────┘
                         │
                         ▼
       ┌────────────────────────────────────┐
       │     Output Linear Layer (1 unit)   │  (Sigmoid Activation)
       └─────────────────┬──────────────────┘
                         │
                         ▼
  Output Target: P_future ∈ [0.0, 1.0]  (24h - 72h Future Risk Escalation)
```

---

## 3. Chronological Non-Overlapping Dataset Splits

> [!CAUTION]
> **NO RANDOM SHUFFLING OF TIME-SERIES DATA**
>
> Random shuffling introduces severe look-ahead data leakage. Chronological splitting is strictly enforced.

| Split | Date Range | Duration | Observation Count | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Train Set** | 2018-01-01 to 2022-12-31 | 5 Full Years | 1,826 daily steps | Gradient optimization & weight learning |
| **Validation Set** | 2023-01-01 to 2023-12-31 | 1 Full Year | 365 daily steps | Hyperparameter tuning & early stopping |
| **Test Set** | 2024-01-01 to 2024-12-31 | 1 Full Year | 366 daily steps | **100% Untouched final evaluation** |

---

## 4. Prototype Early Warning Alert Zonation

| Alert Level | Predicted Probability ($P_{\text{future}}$) | System Status | Recommended Action |
| :--- | :--- | :--- | :--- |
| **NORMAL** | $0.00 \le P_{\text{future}} < 0.25$ | Green | Routine monitoring; standard meteorological tracking |
| **WATCH** | $0.25 \le P_{\text{future}} < 0.50$ | Yellow | Advisory notification; monitor automatic rain gauges & slope sensors |
| **WARNING** | $0.50 \le P_{\text{future}} < 0.75$ | Orange | Early warning triggered; alert regional emergency response teams |
| **CRITICAL** | $0.75 \le P_{\text{future}} \le 1.00$ | Red | Imminent hazard action; initiate traffic diversion & evacuation protocols |

---

## 5. Sentinel-1 SAR Modality Status

- **Status**: **OPTIONAL FUTURE MODALITY** (Not required for MVP).
- **Future Integration**: Sentinel-1 InSAR surface deformation velocity ($\text{mm/year}$) can be ingested as a 10th temporal feature ($d_t$) alongside rainfall to detect pre-failure slope creep.

---

## 6. Secondary Application (Jharia Mining Preservation)

All Jharia/Rajapur open-cast coal mine slope instability components (`data/mine_dem.tif`, `data/events/rajapur_instability_events.csv`, `models/model_A_best.pkl`, `models/model_B_best.pkl`) remain intact as Application 2 (Mining Slope Instability Monitoring).
