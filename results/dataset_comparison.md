# Dataset Analysis & Comparison Report: Rockfall AI Prediction

> **Project:** AI-Based Rockfall Prediction System  
> **Report File:** `results/dataset_comparison.md`  
> **Source Files Analyzed:** `data/dataset1.csv` (`landslide.csv.csv`) & `data/dataset2.csv` (`landslidep.csv.csv`)  
> **Date:** August 20, 2026  
> **Status:** Pending User Approval (No files modified, merged, or trained)

---

## 1. Executive Summary

An independent exploratory data analysis (EDA) was performed on both rockfall datasets (`dataset1.csv` and `dataset2.csv`). Both datasets are complete and clean with zero missing values and zero exact duplicate rows. However, **they represent fundamentally different observation types, feature spaces, target definitions, and granularity levels**. 

- **Dataset 1** (`data/dataset1.csv`) contains **2,000 observations** focused on **physical terrain, soil mechanics, seismic activity, and binary event occurrences** (`Landslide`: 0 or 1). It has a perfectly balanced target (50/50).
- **Dataset 2** (`data/dataset2.csv`) contains **5,000 observations** focused on **macro-meteorological conditions and elevation profile paired with multi-class ordinal risk prediction** (`Landslide Risk Prediction`: Low, Moderate, High, Very High). It is severely class-imbalanced (91.82% Low risk).
- **Conclusion:** The datasets **cannot be merged directly** via row-stacking or row-joining due to mismatched schema, target mismatch, and the lack of primary/foreign keys (e.g., timestamps, location IDs, or coordinates). They must be utilized as distinct components within a dual-model ML architecture or harmonized via task-specific feature mapping.

---

## 2. Dataset 1 Independent Inspection (`data/dataset1.csv`)

### 2.1 Basic Structure & Dimensions
- **File Name:** `dataset1.csv` (Original: `landslide.csv.csv`)
- **Row Count:** 2,000 rows
- **Column Count:** 10 columns
- **Memory Footprint:** ~176 KB

### 2.2 Column Schema & Data Types
| # | Column Name | Data Type | Non-Null Count | Missing (%) | Description |
|---|---|---|---|---|---|
| 1 | `Rainfall_mm` | `float64` | 2,000 | 0.00% | Continuous rainfall amount in millimeters |
| 2 | `Slope_Angle` | `float64` | 2,000 | 0.00% | Slope gradient in degrees |
| 3 | `Soil_Saturation` | `float64` | 2,000 | 0.00% | Normalized soil saturation ratio (0.0 to 1.0) |
| 4 | `Vegetation_Cover` | `float64` | 2,000 | 0.00% | Normalized vegetation density index (0.1 to 1.0) |
| 5 | `Earthquake_Activity` | `float64` | 2,000 | 0.00% | Seismic magnitude / activity level |
| 6 | `Proximity_to_Water` | `float64` | 2,000 | 0.00% | Distance to nearest water body (in km) |
| 7 | `Landslide` | `int64` | 2,000 | 0.00% | Target: Binary event outcome (0 = No, 1 = Yes) |
| 8 | `Soil_Type_Gravel` | `int64` | 2,000 | 0.00% | One-hot encoded binary indicator for Gravel soil |
| 9 | `Soil_Type_Sand` | `int64` | 2,000 | 0.00% | One-hot encoded binary indicator for Sand soil |
| 10 | `Soil_Type_Silt` | `int64` | 2,000 | 0.00% | One-hot encoded binary indicator for Silt soil |

### 2.3 Feature Categorization
- **Numerical Features (Continuous):** `Rainfall_mm`, `Slope_Angle`, `Soil_Saturation`, `Vegetation_Cover`, `Earthquake_Activity`, `Proximity_to_Water` (6 features).
- **Numerical Features (Binary / One-Hot):** `Soil_Type_Gravel`, `Soil_Type_Sand`, `Soil_Type_Silt` (3 features). *(Note: ~23.9% of rows have 0 across all three, indicating an unlisted baseline soil type such as Clay or Bedrock).*
- **Categorical Features:** None in raw string format (pre-encoded into binary columns).
- **Target Column:** `Landslide` (Binary integer: `0` or `1`).

### 2.4 Data Quality Checks
- **Missing Values:** `0` missing values across all columns.
- **Duplicate Rows:** `0` exact duplicate rows.
- **Outliers & Validity:**
  - `Rainfall_mm`: Range `[50.04, 299.92]` mm. No negative or non-physical values. 0 IQR outliers.
  - `Slope_Angle`: Range `[5.00, 59.97]` degrees. Realistic slope angles. 0 IQR outliers.
  - `Soil_Saturation`: Range `[0.0007, 0.9988]`. Scaled correctly between 0% and 100%. 0 IQR outliers.
  - `Vegetation_Cover`: Range `[0.1000, 0.9998]`. Scaled correctly. 0 IQR outliers.
  - `Earthquake_Activity`: Range `[0.0016, 6.5000]`. Realistic Richter scale values. 0 IQR outliers.
  - `Proximity_to_Water`: Range `[0.0007, 1.9996]` km. 0 IQR outliers.

### 2.5 Target Class Distribution
| Target Class | Meaning | Count | Percentage |
|---|---|---|---|
| `0` | No Landslide / Rockfall | 1,000 | 50.00% |
| `1` | Landslide / Rockfall Occurred | 1,000 | 50.00% |
- **Distribution Assessment:** Perfectly balanced binary dataset.

### 2.6 Descriptive Statistics (Dataset 1)
| Feature | Count | Mean | Std Dev | Min | 25% | Median (50%) | 75% | Max |
|---|---|---|---|---|---|---|---|---|
| `Rainfall_mm` | 2000 | 176.6885 | 65.7247 | 50.0362 | 128.3798 | 177.0138 | 228.7423 | 299.9191 |
| `Slope_Angle` | 2000 | 29.9854 | 15.1759 | 5.0039 | 18.0181 | 27.7728 | 41.6832 | 59.9667 |
| `Soil_Saturation` | 2000 | 0.5403 | 0.2957 | 0.0007 | 0.2656 | 0.5999 | 0.8020 | 0.9988 |
| `Vegetation_Cover` | 2000 | 0.5229 | 0.2604 | 0.1000 | 0.2955 | 0.5002 | 0.7407 | 0.9998 |
| `Earthquake_Activity` | 2000 | 3.6048 | 1.8960 | 0.0016 | 1.9734 | 3.9964 | 5.2339 | 6.4987 |
| `Proximity_to_Water` | 2000 | 1.0019 | 0.5800 | 0.0007 | 0.5008 | 0.9998 | 1.5053 | 1.9996 |
| `Landslide` | 2000 | 0.5000 | 0.5001 | 0.0000 | 0.0000 | 0.5000 | 1.0000 | 1.0000 |
| `Soil_Type_Gravel` | 2000 | 0.2585 | 0.4379 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 |
| `Soil_Type_Sand` | 2000 | 0.2415 | 0.4281 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1.0000 |
| `Soil_Type_Silt` | 2000 | 0.2610 | 0.4393 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 |

### 2.7 Location & Time Identifiers
- **Spatial Identifiers:** None (No latitude, longitude, site ID, sensor ID, or coordinates).
- **Temporal Identifiers:** None (No timestamp, date, time of day, or year).

---

## 3. Dataset 2 Independent Inspection (`data/dataset2.csv`)

### 3.1 Basic Structure & Dimensions
- **File Name:** `dataset2.csv` (Original: `landslidep.csv.csv`)
- **Row Count:** 5,000 rows
- **Column Count:** 6 columns
- **Memory Footprint:** ~104 KB

### 3.2 Column Schema & Data Types
| # | Column Name | Data Type | Non-Null Count | Missing (%) | Description |
|---|---|---|---|---|---|
| 1 | `Temperature (°C)` | `int64` | 5,000 | 0.00% | Atmospheric ambient temperature in °C |
| 2 | `Humidity (%)` | `int64` | 5,000 | 0.00% | Relative humidity percentage (30% to 95%) |
| 3 | `Precipitation (mm)` | `int64` | 5,000 | 0.00% | Rainfall / precipitation amount in millimeters |
| 4 | `Soil Moisture (%)` | `int64` | 5,000 | 0.00% | Volumetric soil moisture percentage (20% to 90%) |
| 5 | `Elevation (m)` | `int64` | 5,000 | 0.00% | Terrain elevation above sea level in meters |
| 6 | `Landslide Risk Prediction` | `object` | 5,000 | 0.00% | Target: Ordinal risk category (Low, Moderate, High, Very High) |

### 3.3 Feature Categorization
- **Numerical Features (Discrete Integers):** `Temperature (°C)`, `Humidity (%)`, `Precipitation (mm)`, `Soil Moisture (%)`, `Elevation (m)` (5 features).
- **Categorical Features:** `Landslide Risk Prediction` (1 string feature).
- **Target Column:** `Landslide Risk Prediction` (Categorical ordinal target with 4 distinct risk tiers).

### 3.4 Data Quality Checks
- **Missing Values:** `0` missing values across all columns.
- **Duplicate Rows:** `0` exact duplicate rows.
- **Outliers & Validity:**
  - `Temperature (°C)`: Range `[15, 35]` °C. Realistic surface temperature. 0 IQR outliers.
  - `Humidity (%)`: Range `[30, 95]` %. Realistic humidity values. 0 IQR outliers.
  - `Precipitation (mm)`: Range `[0, 250]` mm. Realistic precipitation range. 0 IQR outliers.
  - `Soil Moisture (%)`: Range `[20, 90]` %. Realistic soil moisture values. 0 IQR outliers.
  - `Elevation (m)`: Range `[0, 1000]` m. Realistic elevation readings. 0 IQR outliers.

### 3.5 Target Class Distribution
| Risk Tier | Count | Percentage | Risk Level Interpretation |
|---|---|---|---|
| `Low` | 4,591 | 91.82% | Negligible / Standard condition |
| `Moderate` | 334 | 6.68% | Elevated risk |
| `High` | 63 | 1.26% | High hazard potential |
| `Very High` | 12 | 0.24% | Critical hazard / imminent risk |
- **Distribution Assessment:** Highly imbalanced multi-class dataset (91.82% majority class vs 0.24% minority class).

### 3.6 Descriptive Statistics (Dataset 2)
| Feature | Count | Mean | Std Dev | Min | 25% | Median (50%) | 75% | Max |
|---|---|---|---|---|---|---|---|---|
| `Temperature (°C)` | 5000 | 24.8158 | 6.0529 | 15.0000 | 20.0000 | 25.0000 | 30.0000 | 35.0000 |
| `Humidity (%)` | 5000 | 62.6140 | 19.1085 | 30.0000 | 46.0000 | 63.0000 | 79.0000 | 95.0000 |
| `Precipitation (mm)` | 5000 | 123.1264 | 72.1447 | 0.0000 | 61.0000 | 121.0000 | 186.0000 | 250.0000 |
| `Soil Moisture (%)` | 5000 | 54.9158 | 20.3458 | 20.0000 | 37.0000 | 55.0000 | 72.2500 | 90.0000 |
| `Elevation (m)` | 5000 | 503.0158 | 288.7007 | 0.0000 | 253.0000 | 505.0000 | 757.0000 | 1000.0000 |

### 3.7 Location & Time Identifiers
- **Spatial Identifiers:** Contains top-level topographic height (`Elevation (m)`), but lacks specific spatial coordinates (latitude/longitude, site ID).
- **Temporal Identifiers:** None (No timestamp, date, season, or weather observation timestamp).

---

## 4. Dataset Comparison & Detailed Assessment

### Q1: What information Dataset 1 provides
Dataset 1 captures **site-specific geo-mechanical, structural, and trigger event parameters**:
- Physical terrain steepness (`Slope_Angle`)
- Seismic hazard intensity (`Earthquake_Activity`)
- Soil composition breakdown (`Soil_Type_Gravel`, `Sand`, `Silt`)
- Local hydrology & vegetation protection (`Proximity_to_Water`, `Vegetation_Cover`)
- Precise historical occurrence binary ground truth (`Landslide`: 0 or 1)

### Q2: What information Dataset 2 provides
Dataset 2 captures **regional weather & atmospheric climate dynamics paired with elevation profile**:
- Thermal & atmospheric conditions (`Temperature (°C)`, `Humidity (%)`)
- Regional precipitation & moisture state (`Precipitation (mm)`, `Soil Moisture (%)`)
- Macro-topographic elevation (`Elevation (m)`)
- Ordinal multi-tier risk level classification (`Landslide Risk Prediction`)

### Q3: Which columns overlap
- **Direct Column Name Overlap:** `0` columns overlap verbatim.
- **Conceptual Feature Overlap:**
  - Moisture: `Soil_Saturation` (Dataset 1, continuous 0–1 ratio) $\longleftrightarrow$ `Soil Moisture (%)` (Dataset 2, integer 20–90%).
  - Water/Rainfall: `Rainfall_mm` (Dataset 1, continuous 50–300 mm) $\longleftrightarrow$ `Precipitation (mm)` (Dataset 2, integer 0–250 mm).

### Q4: Which columns are unique
- **Unique to Dataset 1:** `Slope_Angle`, `Vegetation_Cover`, `Earthquake_Activity`, `Proximity_to_Water`, `Soil_Type_Gravel`, `Soil_Type_Sand`, `Soil_Type_Silt`, `Landslide` (Binary Target).
- **Unique to Dataset 2:** `Temperature (°C)`, `Humidity (%)`, `Elevation (m)`, `Landslide Risk Prediction` (Categorical Multi-class Target).

### Q5: Whether they represent the same type of observations
**No.** They represent two distinct observation types:
1. **Dataset 1:** Geomorphological micro-site slope hazard observations.
2. **Dataset 2:** Macro-climate regional weather vulnerability observations.

### Q6: Whether they can be merged
**No, they cannot be merged directly as-is.**
- **Row-wise Concatenation (Stacking) Error:** Mismatched column names, incompatible feature definitions, continuous vs integer precision, and conflicting target columns (`Landslide` binary int vs `Landslide Risk Prediction` ordinal string).
- **Column-wise Merging (Joining) Error:** Lack of relational primary/foreign keys (e.g. `Location_ID` or `Timestamp`).

### Q7: If they can be merged, what key should be used
Currently, **no common key exists** in the raw datasets. 
If future data collection is conducted, the following keys must be recorded to enable safe merging:
1. `Timestamp` / `Date` (Temporal key)
2. `Latitude` & `Longitude` or `Location_ID` (Spatial key)

### Q8: How both datasets should be used in the Machine Learning Pipeline
Since direct merging is unviable without spatial-temporal keys, we propose three viable ML architectural strategies:

```
                          ┌────────────────────────────────────────────────────────┐
                          │         RECOMMENDED DUAL-PIPELINE ARCHITECTURE          │
                          └────────────────────────────────────────────────────────┘

        ┌──────────────────────────────────────┐        ┌──────────────────────────────────────┐
        │              DATASET 1               │        │              DATASET 2               │
        │       (Physical & Geotechnical)      │        │       (Climate & Elevation)          │
        └──────────────────┬───────────────────┘        └──────────────────┬───────────────────┘
                           │                                               │
                           ▼                                               ▼
        ┌──────────────────────────────────────┐        ┌──────────────────────────────────────┐
        │               MODEL A                │        │               MODEL B                │
        │    Physical Hazard Classifier        │        │      Weather Risk Predictor          │
        │  (Random Forest / XGBoost / LightGBM)│        │   (Balanced Random Forest / Cost-  │
        │       Target: Binary (0 / 1)         │        │    Sensitive Multi-Class / SMOTE)    │
        │     Metrics: ROC-AUC, F1-Score       │        │   Target: Ordinal (Low..Very High)   │
        └──────────────────┬───────────────────┘        └──────────────────┬───────────────────┘
                           │                                               │
                           └───────────────────────┬───────────────────────┘
                                                   │
                                                   ▼
                                ┌──────────────────────────────────────┐
                                │       META-ENSEMBLE / AGGREGATOR     │
                                │   Combines Physical Hazard Score (A) │
                                │    with Macro Weather Risk Level (B) │
                                └──────────────────┬───────────────────┘
                                                   │
                                                   ▼
                                ┌──────────────────────────────────────┐
                                │  FINAL ROCKFALL PREDICTION & ALERT   │
                                └──────────────────────────────────────┘
```

#### Strategy Option A: Dual-Model Meta-Ensemble (Recommended)
1. **Model A (Site Physical Hazard Model):** Trained on Dataset 1 to evaluate site-specific physical vulnerability and output a continuous probability score $P(\text{Rockfall})$.
2. **Model B (Atmospheric Risk Model):** Trained on Dataset 2 (using SMOTE or class-weights to handle extreme class imbalance) to output an atmospheric risk level vector.
3. **Meta-Inference Engine:** Combines Model A's physical probability score with Model B's weather risk level to produce a unified Rockfall Hazard Index.

#### Strategy Option B: Hierarchical Multi-Stage Cascade
- **Stage 1 (Macro Screening):** Model B filters regional areas by climate/elevation risk tier.
- **Stage 2 (Micro Evaluation):** For high-risk weather alerts, Model A evaluates specific slope profiles using geotechnical factors.

#### Strategy Option C: Target Harmonization & Unified Feature Alignment
- Map Dataset 2 target to binary (`Low` $\rightarrow 0$, `Moderate/High/Very High` $\rightarrow 1$).
- Scale & align overlapping features (`Rainfall_mm` $\leftrightarrow$ `Precipitation (mm)`, `Soil_Saturation` $\leftrightarrow$ `Soil Moisture (%)`).
- Impute non-overlapping features using domain defaults or synthetic feature alignment.

---

## 5. Summary Matrix & Comparison Table

| Metric / Dimension | Dataset 1 (`landslide.csv.csv`) | Dataset 2 (`landslidep.csv.csv`) |
|---|---|---|
| **Total Rows** | 2,000 | 5,000 |
| **Total Columns** | 10 | 6 |
| **Data Types** | `float64` (continuous), `int64` (binary) | `int64` (discrete), `object` (string) |
| **Missing Values** | 0 (0.00%) | 0 (0.00%) |
| **Duplicate Rows** | 0 (0.00%) | 0 (0.00%) |
| **Target Variable** | `Landslide` (Binary: 0 or 1) | `Landslide Risk Prediction` (4 Ordinal Tiers) |
| **Class Balance** | 50% / 50% (Perfectly Balanced) | 91.82% Low, 6.68% Mod, 1.26% High, 0.24% Very High |
| **Domain Scope** | Geotechnical, Terrain & Seismic | Meteorological & Elevation |
| **Spatial Identifiers** | None | Elevation (m) only |
| **Temporal Identifiers**| None | None |
| **Merge Suitability** | Cannot merge directly | Cannot merge directly |

---

## 6. Next Steps & Action Plan (Awaiting Approval)

To proceed with model building, please review this report and provide your approval on the preferred modeling strategy:

1. **Option 1 (Recommended):** Build two dedicated ML models (Binary classifier for Dataset 1, Imbalance-handled Ordinal classifier for Dataset 2) and combine them into an ensemble pipeline.
2. **Option 2:** Harmonize targets into a single unified binary dataset and train a single model.
3. **Option 3:** Train on Dataset 1 first as the core physical rockfall predictor, using Dataset 2 for secondary validation.

*Standing by for your feedback and approval before proceeding with model development!*
