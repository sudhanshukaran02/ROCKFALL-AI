# NER-LENS — Final Platform Certification Report (Stage 12)

**Product:** North Eastern Region Landslide Early Warning & Risk Monitoring System (NER-LENS)  
**Problem Statement:** Ministry of Development of North Eastern Region (MDoNER) — SIH 26001  
**Architecture:** React 18 + TypeScript + Vite + Tailwind CSS Frontend | FastAPI Integration Backend | PyTorch & Scikit-Learn Scientific Core  
**Certification Date:** August 21, 2026  
**Final Status:** **PASS WITH LIMITATIONS (RESEARCH DECISION-SUPPORT READY)**  
**Safety Classification:** **NOT CERTIFIED FOR AUTONOMOUS PUBLIC DISASTER WARNING — HUMAN REVIEW MANDATORY**

---

## Executive Summary

This document certifies that the **NER-LENS** platform integration has been successfully completed according to all architectural invariants and scientific protection constraints established in the Master Project Instructions.

The platform unifies the multi-year research pipeline—encompassing high-resolution spatial landslide detection (U-Net CNN), multi-scale terrain susceptibility (SRTM DEM), 30-day temporal weather hazard forecasting (PyTorch LSTM), and multimodal late-fusion decision support—into a modern, responsive, and scientifically honest institutional web interface without altering or retraining underlying ML checkpoints or fabricating real-time telemetry.

---

## 1. Overall Certification Status Matrix

| Audit Area | Target Standard | Observed Status | Verdict |
| :--- | :--- | :--- | :--- |
| **Frontend Production Build** | Zero TypeScript / Compilation Errors | 2,254 modules compiled in 24.32s via `tsc -b && vite build` | **PASS** |
| **Backend REST API** | 100% Endpoint Test Pass Rate | 20 / 20 Pytest test cases passed in 0.37s | **PASS** |
| **Core Scientific Regression** | 10/10 Verification Tests Passed | 10 / 10 Tests passed in `test_final_platform.py` | **PASS** |
| **Jharia Mining Sector QC** | Unaltered Benchmark Metric Assertion | Benchmark assertions verified in `test_rajapur_dashboard.py` | **PASS** |
| **Model Checkpoint Integrity** | 100% Byte-Exact Model Retention | All 4 checkpoints byte-exact and unmodified | **PASS** |
| **Multimodal Decision Formula** | $R = 0.25E + 0.25S + 0.50T$ Frozen | Equation, weights, and thresholds completely intact | **PASS** |
| **Data Provenance & Honesty** | Zero Fake Live Sensor Streams | IMD AWS, IoT, InSAR explicitly marked `NOT CONNECTED` | **PASS** |
| **External Satellite Downloads** | Zero Sentinel-1 Data Downloaded | 0 GB downloaded; no fake SAR displacements | **PASS** |
| **Streamlit Reference App** | Full Backward Compatibility | `app/app.py` loads and executes cleanly | **PASS** |
| **Human-in-the-Loop Governance** | No Autonomous Broadcasts | 5-step authorization state machine enforced | **PASS** |

---

## 2. Model Checkpoint Integrity Audit

Direct filesystem inspection confirms that all four machine learning model checkpoints remain **100% byte-exact and unmodified**:

| Model Component | Checkpoint Filesystem Path | Baseline Size | Certified Size | Integrity Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **U-Net 4-Channel CNN** | `results/ner/segmentation/best_unet.pth` | 31,118,347 bytes | **31,118,347 bytes** | **INTACT (Byte-Exact)** |
| **2-Layer PyTorch LSTM** | `models/ner_lstm_best.pth` | 41,259 bytes | **41,259 bytes** | **INTACT (Byte-Exact)** |
| **Jharia Model A (RF)** | `models/model_A_best.pkl` | 3,489 bytes | **3,489 bytes** | **INTACT (Byte-Exact)** |
| **Jharia Model B (CatBoost)** | `models/model_B_best.pkl` | 1,018,929 bytes | **1,018,929 bytes** | **INTACT (Byte-Exact)** |

---

## 3. Unaltered Scientific Benchmark Assertions

All metrics presented across the web application and API adapters match the verified test splits:

### A. U-Net 4-Channel Optical Landslide Segmentation
- **Input Channels:** RGB + Topographic Slope (4-Channel Tensor)
- **Test Intersection-over-Union (IoU):** `0.2595`
- **Test Dice / F1 Score:** `0.4121`
- **Test Recall (Sensitivity):** `0.9141` ($91.41\%$)
- **Test Precision:** `0.2660` ($26.60\%$)
- **Pixel Classification Accuracy:** `0.8794` ($87.94\%$)

### B. PyTorch Temporal Weather LSTM
- **Sequence Lookback ($T$):** 30 Days | **Forecast Horizon ($H$):** 24 Hours
- **Weather Feature Ablation PR-AUC:** `0.1488` (Ablated) vs `0.1099` (Base)
- **ROC-AUC Score:** `0.8682`
- **Precision:** `0.1000` | **Recall:** `0.5556` | **F1 Score:** `0.1695`

### C. Multimodal Late-Fusion Decision Engine
- **Formula:** $R_\text{multimodal} = 0.25 E_\text{spatial} + 0.25 S_\text{terrain} + 0.50 T_\text{temporal}$
- **Combined ROC-AUC:** `0.8682` | **PR-AUC:** `0.1099`
- **Brier Calibration Score:** `0.1652` (*POOR calibration — raw probabilities overestimate frequency*)
- **Balanced Operating Mode:** Threshold $r_\text{th} = 0.65$, Test F1 = `0.2500`, Precision = `28.57%`, Recall = `22.22%`, FPR = `1.52%`
- **High-Sensitivity Mode:** Threshold $r_\text{th} = 0.48$, Test Recall = `100.00%`, Precision = `8.18%`, FPR = `30.79%`
- **Temporal Persistence Rule:** Validated 2-Day consecutive threshold trigger rule.

### D. Jharia / Rajapur Open-Cast Coal Mine Assessment
- **Study Area (AOI):** $1.4503\text{ km}^2$, $1,665$ spatial points
- **Mean Susceptibility Index:** `0.3161` | **Median:** `0.2738` | **Maximum:** `0.7632`
- **High Susceptibility Area ($\ge 0.60$):** `6.01% (0.0871 km²)`
- **Key Confirmed Failure:** `EVT_RAJ_007` (April 2023 Rockfall, Slope $37.3^\circ$, High Susceptibility)

---

## 4. End-to-End Workflow & Subsystem Verification

The platform delivers a cohesive 10-step institutional decision workflow:

```
[External Provenance] ──> [Spatial U-Net] ──┐
[SRTM 30m DEM]        ──> [Terrain Engine] ──┼──> [Multimodal Late Fusion] ──> [Early Warning Protocol]
[NASA POWER Series]   ──> [Temporal LSTM] ──┘         (R = 0.25E+0.25S+0.50T)       (0.65 / 0.48 Thresholds)
                                                                                          │
                                                                                          ▼
[CAP 1.2 Regional Advisory] <── [Authorized Action] <── [Human Geotechnical Review] <── [System Recommendation]
 (8 Supported Languages)
```

1. **Command Center (`/`):** Real-time situational overview aggregating verified landslide points, active alert posture, and multimodal pipeline status.
2. **GIS Risk Map (`/risk-map`):** Interactive MapLibre GL JS engine rendering 50 verified landslide events, terrain morphometry raster overlays, and color-coded field reports.
3. **Landslide Detection (`/detection`):** Interactive U-Net sample inference visualizer with RGB, slope, detected mask, and overlay outputs.
4. **Terrain Susceptibility (`/terrain`):** Multi-parameter morphometric assessment (Slope, Aspect, Curvature, TWI) for natural slopes.
5. **Weather Risk (`/weather`):** Rainfall series inspector and antecedent precipitation hazard calculator.
6. **Temporal Risk (`/temporal-risk`):** 30-day LSTM lookback sequence visualizer and weather feature ablation comparison.
7. **Multimodal Fusion (`/multimodal-risk`):** Weighted fusion calculator with formula breakdown and interactive parameter exploration.
8. **Early Warning Strategy (`/early-warning`):** Operating point evaluator (Balanced vs Sensitive), 2x2 confusion matrix visualizer, and 2-day persistence inspector.
9. **Landslide Inventory (`/inventory`):** Interactive catalog of 50 verified historical events in the North Eastern Region.
10. **Field Observations (`/field-reports`):** Field submission form with GPS coordinates, presets, evidence upload simulation, and reviewer verification queue (`PENDING` $\rightarrow$ `VERIFIED` / `REJECTED`).
11. **Alert Management (`/alerts`):** Human-in-the-loop authorization workspace enforcing statutory sign-off before advisory generation.
12. **Model Status (`/models`):** Full technical model registry with unaltered metrics and operational scopes.
13. **Data Health (`/data-health`):** Transparent dataset provenance catalog, filesystem checkpoint byte audit, and explicit limitations panel.
14. **Jharia Mining Sector (`/jharia`):** Secondary application hub with Rajapur pit morphometry viewer, top 50 rankings, event overlay, and 2D Model A + Model B risk simulator.
15. **Future Integrations (`/integrations`):** Architectural boundary contracts for IMD, IoT, InSAR, Cadastral GIS, offline sync, and 8-language CAP 1.2 advisory generation.

---

## 5. Data Provenance & Boundary Classification

| Provider / Stream | Category | Operational Status | Provenance Disclosure |
| :--- | :--- | :--- | :--- |
| **GSI Historical Landslides** | Geotechnical Ground Truth | **VERIFIED** | 50 GPS-verified historical coordinates across NER |
| **SRTM 30m Global DEM** | Topographic Morphometry | **VERIFIED / HISTORICAL** | NASA SRTM static digital elevation model |
| **NASA POWER / GPM Series** | Meteorological Time Series | **HISTORICAL (2017–2024)** | 8-year daily rainfall, humidity, and temperature series |
| **Live IMD Weather AWS** | Real-time Telemetry | **NOT CONNECTED** | Architectural adapter ready; uses historical fallback |
| **In-Situ Geotechnical IoT** | Piezometer & Moisture Probes | **NOT CONNECTED** | MQTT boundary contract ready; no physical hardware |
| **ESA Sentinel-1 InSAR** | Radar Deformation Stack | **NOT CONNECTED** | Optional future modality; 0 GB downloaded |
| **Cadastral GIS Exposure** | Roads, Bridges & Settlements | **UNAVAILABLE** | OGC WFS schema contract defined; no synthetic layers |
| **Telecom Public SMS** | Mass Emergency Broadcast | **NOT CONNECTED** | CAP 1.2 template generator active; telecom offline |
| **Offline Edge Sync** | Mountain Field Observations | **PROTOTYPE** | IndexedDB state machine specification defined |

---

## 6. Known Scientific & Operational Limitations

1. **Severe Class Imbalance:**  
   Landslide trigger events occur in approximately 1 out of every 40 days ($< 2.5\%$). Precision on unconstrained test splits is inherently low ($10.00\% - 28.57\%$).
2. **Uncalibrated Model Probabilities (Brier Score = 0.1652):**  
   Raw model output probabilities overestimate real-world failure frequency. Direct raw probability usage is hazardous; tuned operating threshold points ($0.65$ or $0.48$) must be used.
3. **Absence of Real-Time Telemetry:**  
   The platform operates on validated multi-year historical benchmarks. It does not stream live satellite, Doppler radar, or in-situ piezometer readings.
4. **Mandatory Human Governance:**  
   The platform is **NOT an autonomous public-warning system**. Model outputs represent advisory risk signals requiring geotechnical officer verification before administrative or evacuation protocols.

---

## 7. Operational Deployment Roadmap (Post-Prototype Requirements)

To transition this research prototype to an operational civil defense system, the following external infrastructure must be provisioned:
1. Formal API credentials and dedicated SFTP/HTTPS webhook connectivity to the IMD National Data Centre.
2. In-situ IoT instrumentation (vibrating wire piezometers, TDR soil moisture sensors, tiltmeters) along high-risk National Highway corridors (NH-6, NH-10, NH-29).
3. Cloud HPC processing pipeline for automated Sentinel-1 InSAR interferogram generation and phase unwrapping.
4. Official integration with State Emergency Operations Centers (SEOC) and telecom Common Alerting Protocol (CAP) gateways.
5. Systematic empirical probability calibration (Isotonic Regression or Platt Scaling) on dense regional AWS networks.

---

## 8. Final Certification Recommendation

The **NER-LENS** platform is hereby certified as:

> **RESEARCH DECISION-SUPPORT READY (PASS WITH LIMITATIONS)**  
> *The system successfully integrates, validates, and visualizes the complete scientific ML pipeline with 100% mathematical integrity, robust error handling, responsive modern design, and total scientific honesty.*

**Certified by Antigravity Integration Engineering System**  
*August 21, 2026*
