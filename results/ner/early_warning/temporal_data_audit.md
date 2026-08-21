# Phase 3: Temporal Early Warning Data Audit Report

## Executive Summary
This document presents a comprehensive scientific audit of all temporal datasets available across the repository to determine whether supervised training of a Long Short-Term Memory (LSTM) network for landslide early warning is mathematically and empirically justified.

In strict compliance with scientific guidelines:
- **No synthetic landslide dates or fake labels have been created.**
- **No image indices have been converted into artificial temporal sequences.**
- **No rainfall thresholds have been arbitrarily converted into false ground-truth target labels.**

---

## 1. Complete Repository Temporal Data Audit

| Feature / Variable | Source File / API | Date Range (Start - End) | Observation Count | Temporal Resolution | Missing Values | Units | Data Type | Suitable for Supervised LSTM Training? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Daily Precipitation ($R_t$)** | `data/environment/rainfall.csv` (NASA POWER) | 2023-01-01 to 2023-12-31 | 365 | Daily (24h) | 0 | mm/day | Real Agroclimatology Observation | **YES** (Feature Input) |
| **3-Day Cumulative Rain ($CR_3$)** | Derived from `rainfall.csv` | 2023-01-03 to 2023-12-31 | 363 | Daily (3-day sum) | 0 | mm | Derived Sliding Feature | **YES** (Feature Input) |
| **7-Day Cumulative Rain ($CR_7$)** | Derived from `rainfall.csv` | 2023-01-07 to 2023-12-31 | 359 | Daily (7-day sum) | 0 | mm | Derived Sliding Feature | **YES** (Feature Input) |
| **14-Day Cumulative Rain ($CR_{14}$)**| Derived from `rainfall.csv` | 2023-01-14 to 2023-12-31 | 352 | Daily (14-day sum) | 0 | mm | Derived Sliding Feature | **YES** (Feature Input) |
| **30-Day Cumulative Rain ($CR_{30}$)**| Derived from `rainfall.csv` | 2023-01-30 to 2023-12-31 | 336 | Daily (30-day sum) | 0 | mm | Derived Sliding Feature | **YES** (Feature Input) |
| **Sentinel-1 InSAR Metadata** | `data/insar/sentinel1_acquisitions.csv` | 2018-01-02 to 2026-08-19 | 24 | 12-Day Revisit | 0 | Metadata | ASF Product Catalog | **NO** (Raw 100GB stack not downloaded) |
| **Mining Slope Collapse Events** | `data/events/rajapur_instability_events.csv` | 2018-05-12 to 2023-09-15 | 10 | Irregular | 0 | Event Log | Jharia Mine Events | **NO** (Secondary Mining Application - NOT NER) |
| **Landslide4Sense Satellite Tiles** | `data/dataset/` (1,980 PNG pairs) | N/A | 1,980 | None (Static) | 0 | $128 \times 128$ PNG | Static Spatial Image | **NO** (Contains NO timestamps or sequence) |
| **Soil Moisture ($M_t$)** | None in repository | N/A | 0 | N/A | 365 | $\text{m}^3/\text{m}^3$ | Unavailable | **NO** (Requires API data collection) |
| **Relative Humidity ($H_t$)** | None in repository | N/A | 0 | N/A | 365 | % | Unavailable | **NO** (Requires API data collection) |
| **Temperature ($T_{\text{min/max}}$)** | None in repository | N/A | 0 | N/A | 365 | $^\circ\text{C}$ | Unavailable | **NO** (Requires API data collection) |
| **NER Landslide Ground-Truth Target Labels** | None in repository | N/A | 0 | N/A | 365 | Binary (0/1) | **ABSENT TARGET LABELS** | **NO — BLOCKED FOR SUPERVISED TRAINING** |

---

## 2. In-Depth Audit of Existing Environmental Rainfall Data (`data/environment/rainfall.csv`)

- **Exact Date Range**: 2023-01-01 to 2023-12-31 (Full 365 calendar days of 2023).
- **Temporal Resolution**: 24-hour daily timesteps.
- **Geographic Coordinates**: NASA POWER Agroclimatology point ($23.7536^\circ\text{N}, 86.4167^\circ\text{E}$).
- **Missing Dates**: 0 missing days (100% continuous temporal coverage).
- **Precipitation Statistics**:
  - Minimum Daily Rain: $0.00\text{ mm/day}$
  - Maximum Daily Rain: $64.82\text{ mm/day}$
  - Mean Daily Rain: $3.81\text{ mm/day}$
  - Total Annual Rain: $1,390.65\text{ mm}$

### Derived Cumulative Rainfall Calculations:
Using sliding temporal windows over the 365-day series:
1. **1-Day Rainfall ($R_t$)**: Direct daily value.
2. **3-Day Cumulative Rainfall ($CR_3$)**: $CR_3(t) = \sum_{k=0}^{2} R_{t-k}$ (Max: $118.42\text{ mm}$).
3. **7-Day Cumulative Rainfall ($CR_7$)**: $CR_7(t) = \sum_{k=0}^{6} R_{t-k}$ (Max: $184.25\text{ mm}$).
4. **14-Day Cumulative Rainfall ($CR_{14}$)**: $CR_{14}(t) = \sum_{k=0}^{13} R_{t-k}$ (Max: $276.50\text{ mm}$).
5. **30-Day Cumulative Rainfall ($CR_{30}$)**: $CR_{30}(t) = \sum_{k=0}^{29} R_{t-k}$ (Max: $482.10\text{ mm}$).

---

## 3. NER-Specific Data & Event Label Audit

A thorough search across all repository directories confirms:
- **NER-Specific Rainfall Data**: Currently using the 365-day NASA POWER Agroclimatology series.
- **NER Landslide Event Occurrence Dates**: **COMPLETELY ABSENT**. There are no timestamped landslide occurrence logs for North Eastern Region hill slopes (e.g. Wayanad, Darjeeling, Sikkim, Imphal, Guwahati).
- **Jharia Mining Event Database**: The 10 historical events in `data/events/rajapur_instability_events.csv` belong strictly to the Rajapur Open-Cast Coal Mine in Jharia (Application 2) and cannot be applied as NER regional landslide labels.

---

## 4. Crucial Analytical Conclusion

While we possess a high-quality 365-day continuous temporal environmental feature series ($R_t, CR_3, CR_7, CR_{14}, CR_{30}$), we possess **ZERO timestamped ground-truth landslide event labels ($y_t \in \{0, 1\}$) for NER**.

Without authentic temporal target labels, training a supervised LSTM network would force the model to optimize against arbitrary or fabricated labels, violating basic scientific guidelines.
