# A Multimodal AI-Based System for Landslide Detection, Risk Assessment, and Early Warning

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-red.svg)](https://pytorch.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

An integrated multimodal AI decision-support platform designed for regional landslide monitoring, susceptibility assessment, and temporal early warning in the **North Eastern Region (NER) of India** (Ministry of Development of North Eastern Region — **MDONER SIH Problem Statement ID 26001**).

> **IMPORTANT RESEARCH DISCLAIMER:**  
> This platform is a **RESEARCH PROTOTYPE DECISION-SUPPORT SYSTEM**. It is **NOT** an autonomous operational warning system and has **NOT** been certified for public emergency management or civil defense alerts.

---

## 📐 Multimodal System Architecture

```text
                               ┌──────────────────────────────────────────────────────────┐
                               │           MULTIMODAL LATE FUSION RISK ENGINE             │
                               │        R(t) = 0.25 E_spatial + 0.25 S_terrain + 0.50 T_temporal │
                               └────────────────────────────┬─────────────────────────────┘
                                                            │
         ┌──────────────────────────────────────────────────┼──────────────────────────────────────────────────┐
         │                                                  │                                                  │
         ▼                                                  ▼                                                  ▼
┌─────────────────────────┐                        ┌─────────────────────────┐                        ┌─────────────────────────┐
│     SPATIAL STREAM      │                        │     TERRAIN STREAM      │                        │     TEMPORAL STREAM     │
│   4-Channel U-Net CNN   │                        │   SRTM 30m DEM Analysis │                        │   2-Layer PyTorch LSTM  │
└────────────┬────────────┘                        └────────────┬────────────┘                        └────────────┬────────────┘
             │                                                  │                                                  │
             │  Spatial Evidence E_spatial                      │  Terrain Susceptibility S_terrain                │  Temporal Risk T_temporal
             ▼                                                  ▼                                                  ▼
 ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │                                              DECISION SUPPORT & ALERT ENGINE                                                 │
 │                                                                                                                              │
 │   Prototype Alert Thresholds:                                                                                                │
 │   • LOW       : R < 0.35  (Baseline background monitoring)                                                                    │
 │   • WATCH     : 0.35 ≤ R < 0.50  (Moderate pre-monsoon / cumulative precipitation)                                            │
 │   • WARNING   : 0.50 ≤ R < 0.70  (High dynamic temporal risk & slope susceptibility)                                          │
 │   • CRITICAL  : R ≥ 0.70  (Immediate risk escalation under extreme precipitation)                                             │
 └──────────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────┘
                                                                │
                                                                ▼
                                           ┌──────────────────────────────────────────┐
                                           │    STREAMLIT INTERACTIVE DASHBOARD &     │
                                           │       PROTOTYPE FIELD REPORTING          │
                                           └──────────────────────────────────────────┘
```

---

## 🔬 AI Components & Performance Metrics

### 1. Spatial Landslide Evidence ($E_{\text{spatial}}$) — U-Net CNN
* **Architecture**: 4-Channel U-Net CNN (`models/ner/best_unet.pth`) tailored for $128 \times 128$ remote sensing tiles.
* **Test Performance**: **IoU**: `0.2595` | **Dice/F1**: `0.4121` | **Recall**: `0.9141` | **Precision**: `0.2660` | **Pixel Accuracy**: `0.8794`.

### 2. Terrain Susceptibility ($S_{\text{terrain}}$) — SRTM DEM Morphometry
* **Source**: 30m SRTM DEM topographic derivatives (Elevation, Slope, Aspect, Curvature, Roughness, Topographic Wetness Index).
* **Regional Susceptibility Baseline**: $S_{\text{terrain}} = 0.52$.

### 3. Temporal Risk ($T_{\text{temporal}}$) — 2-Layer PyTorch Weather LSTM
* **Architecture**: 2-Layer PyTorch LSTM ($T=30$ lookback window, features: precipitation, temp, humidity, rolling rainfall $1\text{d}..30\text{d}$, month sin/cos).
* **Test Performance (2024 Test Set, 366 days)**: **PR-AUC**: `0.1488` | **ROC-AUC**: `0.8404` | **Precision**: `0.1000` | **Recall**: `0.4444` | **F1**: `0.1633`.
* **Baseline Improvement**: Outperforms 7-day cumulative rainfall threshold baseline (`0.0889` PR-AUC) by **+67.4% PR-AUC**.

### 4. Multimodal Late Fusion & Strategy
* **Validated Fusion Scheme**: **Exp D (Temporal-focused)** ($w_{\text{spatial}}=0.25, w_{\text{terrain}}=0.25, w_{\text{temporal}}=0.50$, Validation PR-AUC = `0.1833`).
* **Untouched 2024 Test Evaluation**: **PR-AUC**: `0.1099` | **ROC-AUC**: `0.8682` | **Recall**: `0.8889` (8/9 event days detected) | **Precision**: `0.0769`.
* **Prototype Operating Thresholds**:
  - **Balanced Mode**: $r_{\text{th}} = 0.65$ (Test F1 = `0.2500`, Test Precision = `28.57%`, Test Recall = `22.22%`, FPR = `1.52%`).
  - **High-Sensitivity Mode**: $r_{\text{th}} = 0.48$ (Test Recall = `100.0%`, FPR = `30.79%`).
* **Persistence Rule**: **2 Consecutive Days** (reduces sporadic false alarms by ~20%).

---

## 🗺️ Dual Application Pathways

The platform architecture maintains strict separation between primary regional landslide warning and secondary mining sector applications:

```text
               GENERAL MULTIMODAL FUSION FRAMEWORK
                               │
        ┌──────────────────────┴──────────────────────┐
        ▼                                             ▼
PRIMARY APPLICATION:                           SECONDARY APPLICATION:
NER LANDSLIDE MONITORING &                     JHARIA / RAJAPUR MINING
EARLY WARNING (MDONER SIH 26001)               SLOPE INSTABILITY MONITORING
────────────────────────────────               ────────────────────────────
- 4-Channel U-Net Landslide Segmentation      - Random Forest (Model A) Terrain Model
- SRTM 30m DEM Terrain Susceptibility          - CatBoost (Model B) Mine Risk Engine
- 2-Layer PyTorch Weather LSTM                 - Rajapur Open-Cast Mine Instability Data
- NASA POWER 7-Year Climatology                - 10 Documented Georeferenced Pit Events
```

> **Note**: The NER weather LSTM model is **NOT** directly validated for Jharia open-cast mining conditions. Jharia is maintained as a secondary mining-sector demonstration of the general late-fusion framework.

---

## ⚡ Quick Start & Execution Guide

### 2. Launch FastAPI Backend & React Frontend
Start the modern institutional decision platform:

**Terminal 1 — FastAPI Backend:**
```bash
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 — React 18 + Vite Frontend:**
```bash
cd frontend
npm run dev
```

### 3. Run Automated Certification Test Suites
Verify all backend endpoints, scientific models, and frontend builds:
```bash
# Frontend strict production build & type check
cd frontend && npm run build && cd ..

# FastAPI Backend REST API test suite (20/20 passed)
pytest backend/tests/

# Core NER scientific platform regression test (10/10 passed)
python src/ner/test_final_platform.py

# Jharia mining sector QC regression test
python src/test_rajapur_dashboard.py
```

### 4. Launch Reference Streamlit Application
```bash
streamlit run app/app.py
```

---

## 📁 Directory Structure

```text
rockfall-ai/
├── backend/                       # FastAPI REST Integration & Adapter Layer
│   ├── app/
│   │   ├── main.py                # FastAPI Application Entrypoint & CORS Config
│   │   ├── config.py              # Central Backend Configuration & Path Registry
│   │   ├── api/
│   │   │   └── api_router.py      # REST Router (20 Certified API Endpoints)
│   │   ├── schemas/
│   │   │   └── all_schemas.py     # Pydantic Schemas & Data Contracts
│   │   └── adapters/
│   │       └── all_adapters.py    # Zero-Retraining Adapters around Scientific Models
│   └── tests/
│       └── test_api_endpoints.py  # Automated Pytest Suite (20 Tests Passed)
├── frontend/                      # Modern React 18 + TypeScript + Vite + Tailwind UI
│   ├── src/
│   │   ├── App.tsx                # Client Routing (12 Major Institutional Pages)
│   │   ├── components/            # Reusable UI, MapLibre GIS, Metrics & Layouts
│   │   ├── pages/                 # Full Dashboard, GIS Map, ML Pages & Boundary Hubs
│   │   ├── services/api.ts        # Type-Safe REST API Integration Service
│   │   └── types/index.ts         # TypeScript Domain Data Contracts
│   └── package.json
├── app/
│   └── app.py                     # Streamlit Multimodal Reference Application
├── data/
│   ├── field_reports/             # Local CSV database for prototype field reports
│   └── ner/                       # Real NER environmental & verified landslide datasets
├── models/
│   ├── best_unet.pth              # 4-Channel U-Net CNN (31,118,347 bytes, Exact)
│   ├── ner_lstm_best.pth          # 2-Layer PyTorch LSTM (41,259 bytes, Exact)
│   ├── model_A_best.pkl           # Jharia Random Forest (3,489 bytes, Exact)
│   └── model_B_best.pkl           # CatBoost Mine Engine (1,018,929 bytes, Exact)
├── results/
│   ├── final_certification_report.md # Final Stage 12 Institutional Certification
│   └── ner/                       # Verified U-Net, LSTM, and Fusion outputs
├── src/
│   ├── ner/                       # Core NER Multimodal ML Pipelines
│   └── test_rajapur_dashboard.py  # Jharia QC Test Suite
└── README.md                      # Comprehensive Project Documentation
```

---

## ⚠️ Scientific Limitations & Transparency Disclosures

1. **Severe Class Imbalance**: Positive event ratio is extremely low (1:40 event-to-non-event ratio), leading to low precision ($10.0\%–28.6\%$).
2. **Probability Calibration**: Raw sigmoid probabilities overestimate empirical event frequency (Brier Score = `0.1652`). Tuned threshold operating points ($0.65$ Balanced / $0.48$ Sensitive) must be used.
3. **No Fabricated Live External Feeds**: IMD AWS, in-situ IoT piezometers, and satellite SAR deformation are explicitly marked `NOT CONNECTED`.
4. **Sentinel-1 InSAR Status**: Classified as **`OPTIONAL FUTURE DEFORMATION MODALITY`** (0 GB downloaded).
5. **Human-in-the-Loop Mandatory**: The platform is **NOT an autonomous public disaster warning system**. Geotechnical officer review is legally and operationally required prior to public notification.