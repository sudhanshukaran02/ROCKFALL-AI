# ML Label Readiness Audit Report — Rajapur / South Jharia Coal Mine

## Executive Audit Summary
- **Target Study Area**: Rajapur / South Jharia Open Cast Mine, Dhanbad, Jharkhand
- **Audit Objective**: Determine whether sufficient real-world observed instability data exists to train, validate, or evaluate a supervised machine learning rockfall susceptibility model.
- **Audit Status**: **NOT READY FOR SUPERVISED ML TRAINING**

---

## Key Audit Questions & Answers

### 1. How many confirmed rockfall events exist?
**Answer**: **1 event** (`EVT_RAJ_007`).
- In April 2023, blast vibrations triggered the detachment of weathered sandstone boulders from upper highwall Bench 2 at Rajapur OCP (`Lat: 23.753611°N`, `Lon: 86.416667°E`).

### 2. How many confirmed slope-failure events exist?
**Answer**: **3 events**.
- `EVT_RAJ_001`: Bench slope failure along jointed highwall face (June 2015).
- `EVT_RAJ_005`: Rainfall-induced overburden dump slope slump (July 2021).
- `EVT_RAJ_010`: Bench slope spalling during highwall miner portal preparation (February 2024).

### 3. How many have reliable coordinates?
**Answer**: **9 out of 10 events (90.0%)**.
- 1 event (`EVT_RAJ_008`, historical underground roof collapse) lacks event-level coordinates (`latitude = NaN`, `longitude = NaN`).

### 4. How many fall inside the Rajapur AOI?
**Answer**: **9 out of 10 events (90.0%)**.
- All 9 georeferenced events fall strictly inside the official Rajapur / South Jharia AOI boundary.

### 5. How many have terrain features?
**Answer**: **9 out of 10 events (90.0%)**.
- Terrain features (`elevation`, `slope`, `aspect`, `curvature`, `roughness`, `twi`) were sampled from real SRTM rasters for all 9 georeferenced events.

### 6. Are there enough positive samples for supervised ML?
**Answer**: **NO**.
- Standard machine learning practice requires at least dozens to hundreds of positive instances (`rockfall_label = 1`) across diverse spatial and environmental conditions. With only **1 confirmed positive rockfall sample**, training any classifier (RandomForest, XGBoost, CatBoost, Neural Network) would result in extreme overfitting, mathematical instability, and zero generalization capability.

### 7. Do we have reliable negative samples?
**Answer**: **NO**.
- While 7 events are classified as confirmed non-rockfall instabilities (`rockfall_label = 0`, e.g., dump slumps, roof falls, floor subsidence), "absence of documented rockfall" across un-failed terrain pixels cannot be treated as a true negative sample without continuous field monitoring.

### 8. Is spatial/temporal leakage a concern?
**Answer**: **YES (HIGH CONCERN)**.
- Historical reporting spans 2014 to 2024. Active opencast mining continuously alters pit geometry, bench elevations, and slope angles. Spatial features derived from a static SRTM DEM (2020 snapshot) do not match the historical pit topography at the exact moment of early events (2015–2018).

### 9. What additional data is required?
**Answer**:
1. High-resolution drone LiDAR or photogrammetry DEMs captured at multi-temporal intervals.
2. Systematic daily/weekly pit inspection logs from BCCL safety engineers.
3. Multi-temporal InSAR displacement time series (2018–2026) to detect mm-scale ground movement preceding failure.
4. Geotechnical borehole data (RQD, RMR, joint spacing, porewater pressure).

---

## Final Recommendation & Next Steps

> [!CAUTION]
> **DO NOT TRAIN A SUPERVISED ROCKFALL ML MODEL**.
> Attempting to train or retrain Model A or Model B on this real-world dataset is scientifically invalid.

### Recommended Path Forward:
1. **Maintain Supervised Training Freeze**: Preserve the existing benchmark Model A and Model B strictly for demonstration and synthetic pipeline validation.
2. **Prioritize Unsupervised / Physics-Based Susceptibility**: Utilize kinematic joint analysis, Slope Mass Rating (SMR), and morphological steepness thresholding (>20° slope mask) for real-world Rajapur hazard framing.
3. **Expand Remote-Sensing Inventory**: Execute InSAR deformation processing to discover un-reported ground movement zones across the Jharia Coalfield.
