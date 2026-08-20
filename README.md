# Rockfall AI — AI-Based Ground Instability & Meteorological Hazard Assessment Prototype

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

An AI-driven decision-support prototype system that evaluates rockfall hazard risks by integrating geotechnical ground instability models with regional meteorological risk predictions.

> **IMPORTANT DISCLAIMER:**  
> This system is a **PROTOTYPE DECISION-SUPPORT ENGINE**. All risk scores, hazard index values, risk matrices, and advisories are heuristic model-derived outputs based on proxy datasets. They are **NOT** operational safety instructions or scientifically validated geotechnical hazard predictions.

---

## 📐 System Architecture

```
                               ┌──────────────────────────────────────────────────────────┐
                               │                ROCKFALL AI RISK FUSION LAYER             │
                               └──────────────────────────────────────────────────────────┘

          INPUT: Geotechnical Parameters                             INPUT: Climate & Weather Parameters
      (Slope Angle, Saturation, Seismic, etc.)                     (Precipitation, Temp, Humidity, Elevation)
                        │                                                           │
                        ▼                                                           ▼
           ┌─────────────────────────┐                                 ┌─────────────────────────┐
           │        MODEL A          │                                 │        MODEL B          │
           │   Ground Instability    │                                 │   Meteorological Risk   │
           └────────────┬────────────┘                                 └────────────┬────────────┘
                        │                                                           │
                        │  Physical Probability P(Instability)                       │  Risk Tier Vector
                        ▼                                                           ▼
          ┌──────────────────────────────────────────────────────────────────────────────────────────┐
          │                               2D RISK MATRIX & AGGREGATOR ENGINE                         │
          │                                                                                          │
          │  Combines P(Instability) with Meteorological Risk Tier:                                  │
          │  • LOW RISK      : Low Weather Risk AND Low Physical Instability (P < 0.35)             │
          │  • MODERATE RISK : Moderate Weather Risk OR Moderate Instability (0.35 ≤ P < 0.65)       │
          │  • HIGH RISK     : High Weather Risk OR High Instability (0.65 ≤ P < 0.85)               │
          │  • CRITICAL ALERT: Very High Weather Risk AND High Instability (P ≥ 0.85)              │
          └────────────────────────────────────────────┬─────────────────────────────────────────────┘
                                                       │
                                                       ▼
                                  ┌──────────────────────────────────────────┐
                                  │  FINAL ROCKFALL HAZARD INDEX & ADVISORY  │
                                  │   (Dashboard, Heatmaps, Road Alerts)     │
                                  └──────────────────────────────────────────┘
```

---

## 📁 Repository Directory Structure

```
rockfall-ai/
├── data/
│   ├── dataset1.csv               # Geotechnical & Terrain Dataset (Model A)
│   └── dataset2.csv               # Meteorological & Elevation Dataset (Model B)
├── models/
│   ├── model_A_best.pkl           # Saved Best Model A Pipeline (Logistic Regression)
│   └── model_B_best.pkl           # Saved Best Model B Pipeline (XGBoost + SMOTE)
├── src/
│   ├── config.py                  # Configurable thresholds, matrices, & weights
│   ├── risk_fusion_engine.py      # Core Risk Fusion Engine class
│   ├── evaluate_fusion_layer.py   # Unified scenario-based prototype evaluation
│   └── explainability.py          # Model-derived feature importance & contributions
├── results/
│   ├── dataset_comparison.md      # Initial exploratory dataset comparison report
│   ├── model_A_comparison.csv     # Model A metrics across Logistic Reg, RF, XGB, CatBoost
│   ├── model_B_comparison.csv     # Model B metrics across Logistic Reg, RF, XGB, CatBoost
│   ├── model_A/                   # Plots for Model A (Confusion matrices, ROC, PR, Importances)
│   ├── model_B/                   # Plots for Model B (Confusion matrices, Per-class recalls, Importances)
│   └── fusion/                    # Fusion evaluation results (Distribution, Risk matrix heatmap)
│       ├── fusion_summary.csv
│       ├── scenario_results.csv
│       ├── risk_distribution.png
│       └── risk_matrix.png
├── app/
│   └── app.py                     # Streamlit Interactive Web Dashboard
├── requirements.txt               # Python package dependencies
└── README.md                      # Project documentation
```

---

## ⚡ Quick Start & Execution Guide

### 1. Installation
Clone the repository and install requirements:
```bash
pip install -r requirements.txt
```

### 2. Model Training & Evaluation
To train and evaluate Model A and Model B independently:
```bash
# Model A (Ground Instability Model)
python scratch/train_model_A.py

# Model B (Meteorological Risk Model)
python scratch/train_model_B.py
```

### 3. Scenario-Based Prototype Evaluation
Run the fusion layer scenario-based evaluation engine:
```bash
python -m src.evaluate_fusion_layer
```

### 4. Launch Interactive Web Dashboard
To launch the interactive dashboard:
```bash
streamlit run app/app.py
```

---

## 📊 Model Summaries

### Model A — Ground Instability Model (`data/dataset1.csv`)
* **Target:** `Landslide` (Binary: 0 or 1)
* **Features:** 9 continuous & soil type one-hot encoded features.
* **Best Model:** `Logistic Regression` (1.0 Accuracy, 1.0 Recall, 1.0 F1 on test set).

### Model B — Meteorological Risk Model (`data/dataset2.csv`)
* **Target:** `Landslide Risk Prediction` (`Low`, `Moderate`, `High`, `Very High`)
* **Features:** 5 atmospheric climate & elevation features.
* **Imbalance Handling:** SMOTE applied strictly to training data (`X_train`).
* **Best Model:** `XGBoost (SMOTE)` (1.0 Macro F1, 1.0 Balanced Accuracy on test set).

---

## ⚙️ Configuration & Customization (`src/config.py`)

All thresholds, weights, and advisories are centralized in `src/config.py`:
* **`INSTABILITY_THRESHOLDS`**: Defines binning thresholds for $P(\text{Instability})$.
* **`RISK_MATRIX`**: Transparent 2D matrix mapping ground instability tiers and weather risk tiers to final risk levels (`LOW`, `MODERATE`, `HIGH`, `CRITICAL`).
* **`WEIGHT_INSTABILITY` (0.60)** & **`WEIGHT_WEATHER` (0.40)**: Weights used for the 0–100 Hazard Index score calculation.


## Real-World Remote Sensing Validation
- **Sentinel-1 InSAR Investigation**: Exploratory investigation of NASA ASF DAAC Sentinel-1 IW SLC SAR acquisitions (`N=608` scenes, 2018–2026) over the Rajapur / South Jharia coal mine.
- **Scientific Boundary**: InSAR surface displacement/deformation is NOT equivalent to rockfall. Ground movement signals may indicate mine subsidence, active bench excavation, or seam fires.
- **Label Readiness**: Real-world rockfall event labels remain sparse (`N=1` confirmed rockfall event).
- **ML Freeze**: No real-world ML model retraining or risk-fusion modifications have been performed. Supervised ML training remains strictly frozen until dense event mapping is available.

---

## Real Rajapur Terrain Analysis
- **1-Arcsecond SRTM DEM**: Extracted real terrain derivatives (Elevation, Slope, Aspect, Curvature, Roughness, TWI) across the official 1.4503 km² Rajapur / South Jharia Open Cast Mine AOI polygon (`1,665` spatial grid points).
- **Transparent Morphological Susceptibility Index**: Calculated a deterministic, non-ML terrain susceptibility index using robust P5–P95 percentile normalization:
  $$\text{Terrain\_Susceptibility\_Index} = 0.25 \times \text{slope}_{\text{norm}} + 0.25 \times \text{curvature\_abs}_{\text{norm}} + 0.25 \times \text{roughness}_{\text{norm}} + 0.25 \times \text{twi}_{\text{norm}}$$
- **Historical Event Spatial Comparison**: Overlaid 10 documented historical instability events for spatial context. Confirmed April 2023 rockfall (`EVT_RAJ_007`) falls into a `HIGH` susceptibility cell (`Index = 0.6512`, `Slope = 31.2°`).
- **Weight Sensitivity Analysis**: Tested alternative expert weighting scenarios (Slope-heavy, Equal-weight, Moisture-heavy). Classification sensitivity confirmed as `SENSITIVE`.
- **Scientific Limitation**: The synthetic ML benchmark models (Model A / Model B) are **NOT** claimed as validated real-world rockfall predictors. The terrain susceptibility index is a prototype morphological indicator, not a hazard probability or certified geotechnical risk assessment.
#   R O C K F A L L - A I  
 