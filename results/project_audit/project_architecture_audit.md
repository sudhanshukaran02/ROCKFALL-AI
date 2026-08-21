# ROCKFALL-AI Architecture Audit: Project Redesign for SIH Problem Statement 26001

## Problem Statement Overview
- **Problem Statement ID**: 26001
- **Title**: AI-Based Early Warning and Landslide Risk Monitoring System in NER
- **Organization**: Ministry of Development of North Eastern Region (MDONER)
- **Primary Goal**: Early warning and spatial landslide risk monitoring tailored for the North Eastern Region (NER) of India.
- **Secondary Application**: Jharia / Rajapur Open-Cast Mining Slope Instability Monitoring (Preserved intact).

---

## 1. Audit of Existing Codebase & Assets

### 1. Existing ML Models
- **models/model_A_best.pkl**: Random Forest / Gradient Boosting classifier trained on Rajapur mine DEM derivatives (Slope, Aspect, Curvature, Roughness, TWI). Maps terrain slope susceptibility.
- **models/model_B_best.pkl**: CatBoost classifier trained on tabular environmental features (Rainfall, Temperature, Humidity, Soil Moisture, Elevation).
- *Audit Status*: **PRESERVED INTACT**. Do NOT retrain or alter model files.

### 2. Existing Training Datasets
- **data/dataset1.csv**: 2,000 synthetic rows containing rainfall, slope angle, soil saturation, vegetation cover, earthquake activity, proximity to water, soil type, and binary landslide label.
- **data/dataset2.csv**: 5,000 synthetic rows containing temperature, humidity, precipitation, soil moisture, elevation, and landslide risk score.
- *Audit Status*: Used for baseline tabular prototyping. To be superseded for NER by genuine temporal environmental series (NASA POWER / ERA5) and optical imagery.

### 3. Existing Model A / Model B Pipeline
- Model A evaluates physical slope susceptibility from DEM rasters.
- Model B evaluates environmental triggering factors from tabular data.
- *Audit Status*: Preserved for Jharia secondary application. Common risk fusion logic will be adapted for NER multi-modal fusion.

### 4. Existing Terrain / DEM Pipeline
- **data/mine_dem.tif**: High-resolution (25.9 MB) GeoTIFF of the Rajapur open-cast coal mining area.
- **src/process_real_dem.py**, **src/terrain_analysis.py**, **src/terrain_features.py**: Computes elevation, slope, aspect, profile/planform curvature, surface roughness, and Topographic Wetness Index (TWI).
- *Audit Status*: **REUSABLE**. The DEM processing pipeline can ingest any regional DEM (e.g. SRTM 30m / ALOS PALSAR 12.5m for NER regions) to generate spatial slope susceptibility maps.

### 5. Existing Jharia / Rajapur Spatial Analysis
- **src/analyze_rajapur_spatial.py**, **src/validate_rajapur_spatial.py**: Identifies top 50 steep slope locations and evaluates risk overlays.
- *Audit Status*: **PRESERVED INTACT**. Formulates the foundation of Application 2 (Mining Slope Instability).

### 6. Existing Historical Event Inventory
- **data/events/rajapur_instability_events.csv**: 10 georeferenced slope movement events in Rajapur mine with evidence quotes, confidence levels, slope, elevation, and TWI coordinates.
- *Audit Status*: **PRESERVED**. Serves as benchmark validation for Jharia mining application.

### 7. Existing Streamlit Dashboard
- **pp/app.py**: Streamlit dashboard presenting interactive maps, risk controls, DEM slope visualizer, and InSAR readiness.
- *Audit Status*: To be restructured into a multi-application platform with dual tabs:
  1. Primary: NER Landslide Early Warning System
  2. Secondary: Mining Slope Instability (Jharia / Rajapur)

### 8. Existing Sentinel-1 / InSAR Work
- **src/investigate_sentinel1_insar.py**, **src/download_sentinel1_stack.py**, **src/verify_sentinel1_metadata_v2.py**: Download scripts and metadata audit of 100+ GB ASF Sentinel-1 SLC/GRD acquisitions.
- *Audit Status*: **NOT DOWNLOADING 100+ GB DATASET FOR MVP**. InSAR feasibility is documented; MVP relies on satellite optical spatial segmentation + temporal environmental LSTM.

### 9. Existing Risk-Fusion Logic
- **src/risk_fusion_engine.py**, **src/evaluate_fusion_layer.py**: Multi-layer risk fusion combining spatial terrain risk (Model A), environmental risk (Model B), and event proximity.
- *Audit Status*: **HIGHLY REUSABLE**. Re-architected for NER to fuse Spatial Segmentation Probability + Temporal LSTM Risk + Regional DEM Susceptibility.

### 10. Existing Requirements & Dependencies
- 
equirements.txt: streamlit, pandas, 
umpy, scikit-learn, catboost, 
asterio, matplotlib, seaborn, olium, streamlit-folium.
- *Audit Status*: Needs 	orch and 	orchvision (or segmentation-models-pytorch) added for spatial segmentation training/inference.

---

## 2. Reusability & Restructuring Matrix

| Component | Status | Action / Role in New Architecture |
| :--- | :--- | :--- |
| **Model A (model_A_best.pkl)** | Unchanged | Secondary application (Jharia Mining Susceptibility) |
| **Model B (model_B_best.pkl)** | Unchanged | Secondary baseline / Reference tabular engine |
| **DEM Processing Pipeline** | Reused | Extract terrain features (Slope, Curvature, TWI) for NER DEMs |
| **Risk Fusion Engine** | Reused & Extended | Fuse Spatial Segmentation + Temporal LSTM + Slope Susceptibility |
| **Rajapur Event Inventory** | Unchanged | Validation ground truth for Jharia Mining module |
| **Synthetic CSVs (dataset1/2)**| Deprecated for NER | Replaced by Landslide4Sense tiles + NASA POWER NER rainfall series |
| **100 GB Sentinel-1 Download**| Deferred / Deprecated | Replaced by lightweight SAR / Optical spatial segmentation for MVP |
| **Streamlit UI (pp.py)** | Restructured | Dual-tab dashboard (Tab 1: NER Landslides, Tab 2: Mining Jharia) |

---

## 3. Recommended New Platform Architecture

`
                    ROCKFALL-AI / EARTHWATCH PLATFORM
                                    |
            +-----------------------+-----------------------+
            |                                               |
  APPLICATION 1 (PRIMARY)                         APPLICATION 2 (SECONDARY)
  NER LANDSLIDE EARLY WARNING                     MINING INSTABILITY (JHARIA)
            |                                               |
  +-------------------+                           +-------------------+
  | Spatial Model     |                           | DEM Terrain       |
  | (U-Net 128x128x4) |                           | Susceptibility    |
  +-------------------+                           +-------------------+
            |                                               |
  +-------------------+                           +-------------------+
  | Temporal Model    |                           | Event Proximity   |
  | (LSTM 7/14-Day)   |                           | & Slope Audit     |
  +-------------------+                           +-------------------+
            |                                               |
            +-----------------------+-----------------------+
                                    |
                             COMMON AI ENGINE
                         (Multi-Modal Risk Fusion)
                                    |
                            EARLY WARNING UI
                    (LOW / MODERATE / HIGH / CRITICAL)
`
