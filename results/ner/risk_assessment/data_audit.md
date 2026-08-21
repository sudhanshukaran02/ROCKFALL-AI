# Real Data Audit: NER Landslide Risk Assessment

## Executive Summary
This document presents an audit of all real datasets available in the repository for the North Eastern Region (NER) Landslide Detection and Risk Assessment Platform. 

In strict compliance with scientific integrity guidelines:
- **No missing values or variables have been fabricated.**
- Unavailable features are explicitly identified and documented.
- The risk assessment framework is built strictly around genuine, verifiable data sources.

---

## 1. Dataset Availability & Suitability Table

| Feature | Available? | Source | Spatial / Temporal | Units | Resolution | Suitable for Phase 2 Risk Assessment? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Satellite Imagery Tiles** | **YES** | Landslide4Sense / Kaggle (`data/dataset/`) | Spatial | Reflectance ($[0, 255]$) | 128 x 128 tile, 4-channels (RGBA) | **YES** — Primary spatial input for U-Net detector |
| **Landslide Segmentation Masks** | **YES** | Landslide4Sense / Kaggle (`data/dataset/`) | Spatial | Binary ($0$ / $255$) | 128 x 128 tile | **YES** — Ground truth for U-Net detection |
| **U-Net Spatial Probability** | **YES** | Trained U-Net (`results/ner/segmentation/best_unet.pth`) | Spatial | Probability ($[0.0, 1.0]$) | 128 x 128 pixel map | **YES** — Spatial landslide evidence metric |
| **Daily Rainfall ($R_t$)** | **YES** | NASA POWER Agroclimatology (`data/environment/rainfall.csv`) | Temporal | mm / day | 365 daily steps (2023) | **YES** — Primary environmental trigger variable |
| **Cumulative 3-Day Rainfall ($CR_3$)** | **YES** | Derived from NASA POWER series | Temporal | mm | 3-day sliding sum | **YES** — Short-term saturation trigger |
| **Cumulative 7-Day Rainfall ($CR_7$)** | **YES** | Derived from NASA POWER series | Temporal | mm | 7-day sliding sum | **YES** — Medium-term saturation trigger |
| **Cumulative 30-Day Rainfall ($CR_{30}$)**| **YES** | Derived from NASA POWER series | Temporal | mm | 30-day sliding sum | **YES** — Seasonal saturation background |
| **Digital Elevation Model (DEM)** | **YES** | SRTM 1-ArcSec GeoTIFF (`data/mine_dem.tif`) | Spatial | Meters (m) | 30-meter spatial resolution | **YES** — Terrain derivative reference |
| **Slope Gradient** | **YES** | Computed from GeoTIFF / Spatial Image Texture | Spatial | Degrees ($^\circ$) / Gradient Index | 30-meter / Tile pixel level | **YES** — Terrain susceptibility indicator |
| **Profile & Planform Curvature** | **YES** | Computed from GeoTIFF DEM | Spatial | $\text{m}^{-1}$ | 30-meter spatial resolution | **YES** — Terrain curvature indicator |
| **Surface Roughness** | **YES** | Computed from GeoTIFF DEM | Spatial | Index ($[0, 1]$) | 30-meter spatial resolution | **YES** — Terrain texture indicator |
| **Topographic Wetness Index (TWI)** | **YES** | Computed from GeoTIFF DEM | Spatial | Index | 30-meter spatial resolution | **YES** — Hydrological accumulation index |
| **Soil Moisture** | **NO** | Not present in `rainfall.csv` | - | - | - | **NO** — Explicitly declared unavailable |
| **Relative Humidity** | **NO** | Not present in `rainfall.csv` | - | - | - | **NO** — Explicitly declared unavailable |
| **Vegetation Index (NDVI)** | **NO** | Raw NIR band not calibrated | - | - | - | **NO** — Explicitly declared unavailable |
| **Labeled Risk Ground-Truth** | **NO** | No operational risk labels for image tiles | - | - | - | **NO** — Supervised risk training is NOT justified |

---

## 2. Key Audit Conclusions

1. **Spatial Input**: 1,980 multi-channel satellite image tiles provide spatial evidence via U-Net inference (`best_unet.pth`).
2. **Environmental Input**: 365 days of real precipitation data from NASA POWER API (`data/environment/rainfall.csv`) provide the environmental triggering series.
3. **Terrain Input**: SRTM 30m DEM derivatives provide physical slope gradient, curvature, roughness, and TWI.
4. **Supervised Risk Training Justification**:
   - Because no continuous risk score labels or operational risk zonation labels exist for the Landslide4Sense spatial tiles, **training a supervised machine learning classifier for risk scoring is NOT scientifically justified.**
   - Instead, a transparent, multi-criteria normalized **Risk Index** ($R$) is implemented.

---

## 3. Scientific Boundary & Scope

- **Landslide Probability vs. Risk Index**: U-Net pixel probability reflects spatial detection evidence based on surface reflectance. Slope gradient reflects terrain susceptibility. Rainfall reflects environmental triggering.
- **Not an Early Warning System Yet**: This phase produces a spatial-environmental **Risk Assessment Index**, answering *"WHERE is terrain/environmental condition susceptible to risk?"*. It does not forecast future temporal initiation timing (which requires the Phase 3 LSTM).
