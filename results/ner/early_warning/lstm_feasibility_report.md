# LSTM Feasibility Report: Temporal Early Warning System

## Executive Summary
This report evaluates the scientific feasibility of training a Long Short-Term Memory (LSTM) recurrent neural network for temporal landslide early warning under the **Ministry of Development of North Eastern Region (MDONER) Problem Statement 26001**.

> [!IMPORTANT]
> **CLASSIFICATION RESULT**: **`READY FOR LSTM DATA COLLECTION`**
>
> Supervised training of an LSTM network is **NOT SCIENTIFICALLY JUSTIFIED AT THIS STAGE**. 
> 
> While continuous temporal environmental features exist (365 daily rainfall observations), **authentic timestamped landslide occurrence ground-truth labels ($y_t$) for NER do not currently exist in the repository.**

---

## 1. Scientific Justification for Status Classification

To train a supervised sequence model (such as an LSTM), the dataset must contain paired tuples:
$$\mathcal{D} = \{ (\mathbf{X}_{1:T}^{(i)}, y_{T+H}^{(i)}) \}_{i=1}^N$$
where:
- $\mathbf{X}_{1:T}$ is a sequence of past environmental observations over $T$ lookback days.
- $y_{T+H} \in \{0, 1\}$ is an authentic ground-truth binary label indicating whether a landslide occurred within a forecast horizon $H$ (e.g. 24h, 48h, or 72h).

### Current Repository Audit Findings:
1. **Input Features ($\mathbf{X}_{1:T}$)**: **AVAILABLE**. The 365-day NASA POWER Agroclimatology series (`data/environment/rainfall.csv`) provides daily precipitation $R_t$ and derived cumulative rainfall metrics ($CR_3, CR_7, CR_{14}, CR_{30}$).
2. **Target Labels ($y_{T+H}$)**: **ABSENT**. The 1,980 Landslide4Sense image tiles (`data/dataset/`) are static spatial patches without acquisition timestamps. The 10 historical events in `data/events/rajapur_instability_events.csv` belong strictly to Jharia open-cast coal mining walls (Application 2).
3. **Data Integrity Directive**: Fabricating fake landslide dates or converting rainfall thresholds directly into target labels ($y_t = 1 \text{ if } R_t > 50\text{mm}$) is scientifically invalid because it would cause the model to merely memorize the hard-coded rainfall rule rather than learn true non-linear slope failure kinetics.

---

## 2. Standardized Schema for Future LSTM Data Collection

To transition from `READY FOR LSTM DATA COLLECTION` to `READY FOR LSTM TRAINING`, the following standardized temporal CSV schema must be compiled:

```csv
timestamp,rainfall_1d,rainfall_3d,rainfall_7d,rainfall_14d,rainfall_30d,temp_max,temp_min,humidity,soil_moisture,terrain_susceptibility,spatial_landslide_evidence,risk_index,landslide_event_label
2023-07-01,12.4,34.1,68.5,112.0,245.0,26.5,21.0,88.5,0.42,0.65,0.40,0.48,0
2023-07-02,48.6,82.5,135.2,180.4,310.2,25.0,20.5,94.2,0.58,0.65,0.40,0.72,1
```

### Field Definitions:
- `timestamp`: YYYY-MM-DD daily observation timestamp.
- `rainfall_1d`: Daily precipitation (mm/day).
- `rainfall_3d`: 3-day sliding cumulative precipitation (mm).
- `rainfall_7d`: 7-day sliding cumulative precipitation (mm).
- `rainfall_14d`: 14-day sliding cumulative precipitation (mm).
- `rainfall_30d`: 30-day sliding cumulative precipitation (mm).
- `temp_max / temp_min`: Daily maximum and minimum ambient temperature ($^\circ\text{C}$).
- `humidity`: Relative humidity (%).
- `soil_moisture`: Volumetric soil moisture ($\text{m}^3/\text{m}^3$).
- `terrain_susceptibility`: Static DEM slope/roughness susceptibility score ($[0, 1]$).
- `spatial_landslide_evidence`: U-Net predicted probability score ($[0, 1]$).
- `risk_index`: Phase 2 Multi-Criteria Risk Index ($[0, 1]$).
- `landslide_event_label`: **Authentic ground-truth binary label** (0: No event, 1: Verified landslide event occurrence).

---

## 3. Early Warning Target & Forecast Horizon Definition

Once authentic event dates are acquired (e.g. from Geological Survey of India / NDMA disaster reports for Sikkim, Wayanad, Guwahati, Imphal), the early warning target will be formulated as follows:

- **Lookback Input Window ($T$)**: 14 to 30 days of daily environmental observations ($t-29, \dots, t$).
- **Forecast Horizon ($H$)**: 24 to 72 hours into the future ($t+1, t+2, t+3$).
- **Target Formulation**:
  $$y_t^{(H)} = \begin{cases} 1 & \text{if a landslide occurs in period } (t, t+H] \\ 0 & \text{otherwise} \end{cases}$$

---

## 4. Next Steps & Implementation Roadmap

1. **Keep `train_lstm.py` Un-created**: In strict compliance with guidelines, `train_lstm.py` will not be created until ground-truth target labels are collected.
2. **Phase 3 Architecture Design Complete**: The theoretical architecture, temporal splitting protocol, and early warning threshold framework are documented in [`lstm_architecture.md`](file:///c:/Users/Sudhanshu%20Karan/Desktop/rockfall%20ai/results/ner/early_warning/lstm_architecture.md).
3. **Data Collection Priority**: Ingest GSI regional landslide incident dates for North Eastern Region corridors to unlock Phase 3 training.
