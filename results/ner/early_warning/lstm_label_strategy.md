# Future LSTM Label Strategy & Target Formulation

## Executive Summary
This document specifies the rigorous mathematical target formulation and labeling strategy for the future **Phase 3 Temporal LSTM Early Warning Model**.

---

## 1. Positive Event Definition

A positive event timestep ($y_t = 1$) is defined as a verified date ($t$) where an authoritative Tier 1/Tier 2 landslide failure occurred in the study region.

---

## 2. Handling Date Precision Differences

1. **Exact-Date Events (`Exact Day`)**:
   - Assigned directly to the matching daily timestep $t$ in `environmental_timeseries.csv`.
   - Used as primary positive target instances for supervised sequence training.
2. **Month-Only Events (`Month-Year`)**:
   - Excluded from binary daily classification ($y_t$) to avoid false label assignment.
   - Retained as seasonal background validation indicators.

---

## 3. Negative / Background Day Selection Strategy

- **Non-Event Days ($y_t = 0$)**: Daily timesteps in the 2,557-day environmental series where no slope failure incident was recorded.
- **Buffer Zone**: To prevent false negative labels due to pre-failure ground creeping, timesteps within $t-1$ to $t-2$ days preceding a major event are designated as a **Pre-Warning Buffer Zone** ($y_t = 1$ or soft-label $y_t = 0.5$).

---

## 4. Forecast Horizon & Temporal Leakage Prevention

- **Input Sequence Window**: Past $T = 14 	ext{ to } 30	ext{ days}$ ($t-29, \dots, t$).
- **Target Forecast Horizon ($H$)**: Future $24	ext{ to }72	ext{ hours}$ ($t+1, t+2, t+3$).
- **Data Leakage Prevention**: Chronological non-overlapping splits (Train: 2018–2022, Val: 2023, Test: 2024). Standardized scaling parameters derived strictly from the training slice.
