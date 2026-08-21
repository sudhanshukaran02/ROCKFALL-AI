# Implementation Plan: Redesigning ROCKFALL-AI for SIH Problem Statement 26001

## Problem Statement Overview
- **Problem Statement ID**: 26001
- **Title**: AI-Based Early Warning and Landslide Risk Monitoring System in NER
- **Organization**: Ministry of Development of North Eastern Region (MDONER)
- **Primary Focus**: AI-driven spatial landslide detection and multi-day early warning system for the North Eastern Region of India.
- **Secondary Application**: Transferable open-cast mining slope instability monitoring (Jharia / Rajapur Coalfield).

---

## 1. Current Project Capabilities
- **DEM Derivative Pipeline**: Complete spatial feature extraction (Elevation, Slope, Aspect, Curvature, Roughness, TWI) from GeoTIFF rasters (`data/mine_dem.tif`).
- **Pre-Trained Machine Learning Models**:
  - `models/model_A_best.pkl`: Random Forest slope susceptibility classifier.
  - `models/model_B_best.pkl`: CatBoost tabular environmental classifier.
- **Mining Site Geodatabase**: Georeferenced database of 10 historical slope instability events in Rajapur mine.
- **Risk Fusion Engine**: Modular risk calculation engine combining terrain risk, environmental proxies, and event proximity.
- **Interactive Dashboard**: Streamlit application (`app/app.py`).

---

## 2. Dataset Findings (`data/dataset/`)
- **Dataset Source**: Kaggle `landslide-divided` benchmark (Landslide4Sense format).
- **Total Samples**: 1,980 image-mask tile pairs.
  - `train`: 1,385 pairs (69.95%)
  - `validation`: 396 pairs (20.00%)
  - `test`: 199 pairs (10.05%)
- **Data Specification**:
  - Image size: $128 \times 128 \times 4$ pixels (RGBA PNG, 8-bit `uint8`).
  - Mask size: $128 \times 128 \times 4$ pixels (RGBA PNG, binary `0` background, `255` landslide).
- **Class Imbalance**: 99.8% of tiles contain landslides, but overall pixel ratio is 95.5% background vs 4.5% landslide pixels.
- **Spatial vs Temporal Audit**:
  - **100% Spatial Data**: Independent multi-spectral image tiles.
  - **0% Temporal Data**: No timestamps, acquisition sequence, or time-series measurements exist in this dataset.
  - **Crucial Conclusion**: This image dataset CANNOT train an LSTM model. The LSTM model must be trained on genuine temporal environmental data (rainfall, soil moisture, humidity).

---

## 3. Component Reusability & Preservation Matrix
- **REUSE**: DEM terrain derivative extractor (`src/terrain_analysis.py`), Risk Fusion framework (`src/risk_fusion_engine.py`), Streamlit app shell.
- **PRESERVE INTACT**: `models/model_A_best.pkl`, `models/model_B_best.pkl`, `data/mine_dem.tif`, `data/events/rajapur_instability_events.csv`, all Jharia spatial validation code.
- **DEPRECATE / RESTRUCTURE**: Direct reliance on synthetic CSVs (`dataset1.csv`/`dataset2.csv`) for primary NER model training; 100+ GB Sentinel-1 download requirement for MVP.

---

## 4. New Architectural Modules To Add
1. **Spatial Landslide Segmentation Module** (`src/ner/dataset.py`, `train_segmentation.py`, `evaluate_segmentation.py`):
   - PyTorch U-Net / U-Net++ segmentation model on $128 \times 128 \times 4$ tiles.
2. **Temporal Environmental Data & LSTM Module** (`src/ner/prepare_timeseries.py`, `train_lstm.py`, `evaluate_lstm.py`):
   - NASA POWER daily rainfall, soil moisture, and humidity time-series for NER coordinates.
   - 2-Layer Many-to-One LSTM network for 7-day risk escalation forecasting.
3. **Multi-Modal Fusion Engine** (`src/ner/fusion.py`):
   - Fuses Spatial Segmentation Probability + Temporal LSTM Risk + Regional DEM Susceptibility into early warning levels (LOW, MODERATE, HIGH, CRITICAL).
4. **Dual-Application Streamlit Dashboard** (`app/app.py`):
   - Primary View: NER Landslide Early Warning Platform.
   - Secondary View: Mining Slope Instability Monitoring (Jharia).

---

## 5. Spatial Model Architecture & Loss Function
- **Model**: U-Net / U-Net++ with ResNet34 backbone.
- **Input**: $(B, 4, 128, 128)$ tensor normalized to $[0, 1]$.
- **Output**: $(B, 1, 128, 128)$ pixel probability map.
- **Loss Function**: Combined Focal Loss + Dice Loss ($\mathcal{L} = \mathcal{L}_{focal} + \mathcal{L}_{dice}$) to resolve the extreme 95.5% / 4.5% pixel class imbalance.
- **Metrics**: IoU (Jaccard Index), Dice Score ($F1$), Precision, Recall, Affected Area ($m^2$).

---

## 6. LSTM Early Warning Model Architecture
- **Model**: 2-Layer Many-to-One Recurrent Neural Network with LSTM cells + Dropout (0.2) + Linear Dense layer + Sigmoid.
- **Input**: $(B, T=7, F=6)$ time-series tensor ($[R_t, CR_3, CR_7, R_{max}, M_t, H_t]$).
- **Output**: Future 24h-72h landslide risk probability $P_{temporal} \in [0, 1]$.
- **Metrics**: ROC-AUC, PR-AUC, Early Warning Lead Time, False Alarm Rate.

---

## 7. Multi-Modal Risk Fusion Strategy
- **Composite Risk Index Formula**:
  $$R_{composite} = 0.40 \cdot P_{spatial} + 0.45 \cdot P_{temporal} + 0.15 \cdot S_{terrain}$$
- **Warning Classification Thresholds**:
  - $0.00 \le R_{composite} < 0.30$: **LOW** (Green - Normal Monitoring)
  - $0.30 \le R_{composite} < 0.55$: **MODERATE** (Yellow - Advisory Alert)
  - $0.55 \le R_{composite} < 0.75$: **HIGH** (Orange - Early Warning Triggered)
  - $0.75 \le R_{composite} \le 1.00$: **CRITICAL** (Red - Imminent Landslide Hazard)

---

## 8. Preserved Jharia Application Architecture
- Formulated as **Application 2: Mining Slope Instability (Jharia / Rajapur Open-Cast Mine)**.
- Evaluates pit wall slope steepness, DEM curvature/roughness/TWI, Model A slope susceptibility, and georeferenced historical collapse locations.
- Zero modification to existing trained model binaries or Rajapur CSV files.

---

## 9. Data Leakage Prevention & Scientific Validation
- **Spatial Leakage Prevention**: Strict tile-level train/validation/test split isolation. Image normalization computed strictly on training subset.
- **Temporal Leakage Prevention**: Chronological split for time-series data. No future observations included in sliding window features.
- **Scientific Caveats**:
  - Optical satellite images cannot penetrate thick monsoon cloud cover; temporal rainfall LSTM fills cloud-gap periods.
  - Static slope steepness is labeled strictly as "terrain susceptibility", not operational "rockfall probability".

---

## 10. Recommended Proposed File Structure
```
data/
    dataset/ (train/ val/ test/ 1980 PNG pairs)
    environment/ (rainfall.csv - NASA POWER series)
    events/ (rajapur_instability_events.csv)
    mine_dem.tif (Rajapur GeoTIFF)

models/
    model_A_best.pkl (Preserved Jharia Model A)
    model_B_best.pkl (Preserved Jharia Model B)

src/
    ner/
        dataset.py
        train_segmentation.py
        evaluate_segmentation.py
        prepare_timeseries.py
        train_lstm.py
        evaluate_lstm.py
        fusion.py
    jharia/
        terrain_analysis.py
        susceptibility.py

app/
    app.py (Dual-tab Dashboard)

results/
    project_audit/
        project_architecture_audit.md
    ner_landslide/
        dataset_audit.md
        dataset_inventory.csv
        implementation_plan.md
```
