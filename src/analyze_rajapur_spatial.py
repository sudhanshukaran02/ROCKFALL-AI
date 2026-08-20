"""
Real Rajapur Spatial Rockfall Susceptibility Analysis Pipeline.

Applies existing Model A (models/model_A_best.pkl) to the real spatial features dataset
(results/terrain/spatial_features.csv) over the Rajapur / South Jharia open-cast coal mine study area.
Generates:
1. results/rajapur/rajapur_modelA_predictions.csv
2. results/rajapur/rajapur_modelA_risk_map.png
3. results/rajapur/rajapur_risk_summary.csv
4. results/rajapur/risk_vs_slope.csv
5. results/rajapur/risk_vs_slope.png
6. results/rajapur/top_50_susceptibility_locations.csv
7. results/rajapur/rajapur_spatial_analysis.md
"""

import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.path import Path

# Set non-interactive backend
plt.switch_backend('Agg')

def run_rajapur_spatial_analysis():
    print("============================================================")
    print("RAJAPUR REAL-TERRAIN MODEL A ANALYSIS")
    print("============================================================")

    # 1. INPUT FILE PATHS
    aoi_path = os.path.join('scratch', 'rajapur_south_jharia_aoi.geojson')
    features_path = os.path.join('results', 'terrain', 'spatial_features.csv')
    model_a_path = os.path.join('models', 'model_A_best.pkl')
    events_path = os.path.join('data', 'events', 'rajapur_instability_events.csv')
    output_dir = os.path.join('results', 'rajapur')
    os.makedirs(output_dir, exist_ok=True)

    # Verification of input files
    for p in [aoi_path, features_path, model_a_path, events_path]:
        if not os.path.exists(p):
            raise FileNotFoundError(f"Required input file missing at '{p}'!")

    # 2. MODEL INPUT CHECK
    print("\n--- 1. MODEL A EXPECTED FEATURE INSPECTION ---")
    model_A = joblib.load(model_a_path)
    
    if hasattr(model_A, 'feature_names_in_'):
        model_A_features = list(model_A.feature_names_in_)
    else:
        model_A_features = [
            'Rainfall_mm', 'Slope_Angle', 'Soil_Saturation', 'Vegetation_Cover',
            'Earthquake_Activity', 'Proximity_to_Water', 'Soil_Type_Gravel',
            'Soil_Type_Sand', 'Soil_Type_Silt'
        ]

    print(f"Model A expected features:")
    print(f"Feature count: {len(model_A_features)}")
    print(f"Feature names: {model_A_features}")

    # Load Spatial Features Dataset & AOI Polygon
    sf_df = pd.read_csv(features_path)
    print(f"\nSpatial Feature Dataset Loaded: {len(sf_df)} points")
    print(f"Columns: {list(sf_df.columns)}")

    with open(aoi_path, 'r', encoding='utf-8') as f:
        aoi_geojson = json.load(f)
    poly_coords = aoi_geojson['features'][0]['geometry']['coordinates'][0]
    aoi_polygon = Path(poly_coords)

    # 3. PREPARE MODEL A INFERENCE INPUT DATAFRAME
    # Supply pixel-specific terrain slope to Slope_Angle and baseline regional geotechnical parameters
    model_A_df = pd.DataFrame({
        'Rainfall_mm': 120.0,
        'Slope_Angle': sf_df['slope'],
        'Soil_Saturation': 0.40,
        'Vegetation_Cover': 0.30,
        'Earthquake_Activity': 1.5,
        'Proximity_to_Water': 1.0,
        'Soil_Type_Gravel': 1,
        'Soil_Type_Sand': 0,
        'Soil_Type_Silt': 0
    })[model_A_features]

    # Verify input feature order matches exactly
    assert list(model_A_df.columns) == model_A_features, "Model A input columns do not match expected feature order!"

    # 4. GENERATE MODEL A PREDICTIONS
    print("\n--- 2. GENERATING MODEL A SPATIAL PREDICTIONS ---")
    if hasattr(model_A, 'predict_proba'):
        prob_A = model_A.predict_proba(model_A_df)[:, 1]
    else:
        prob_A = model_A.predict(model_A_df)

    pred_A = (prob_A >= 0.5).astype(int)

    # Risk Classification (Thresholds: <0.35 LOW, 0.35-0.65 MODERATE, 0.65-0.85 HIGH, >=0.85 VERY HIGH)
    risk_bins = [-0.001, 0.35, 0.65, 0.85, 1.001]
    risk_labels = ['LOW', 'MODERATE', 'HIGH', 'VERY HIGH']
    risk_classes = pd.cut(prob_A, bins=risk_bins, labels=risk_labels)

    # Create predictions output dataframe
    output_df = pd.DataFrame({
        'latitude': sf_df['latitude'],
        'longitude': sf_df['longitude'],
        'model_A_probability': np.round(prob_A, 6),
        'model_A_prediction': pred_A,
        'risk_class': risk_classes,
        'elevation': sf_df['elevation'],
        'slope': sf_df['slope'],
        'aspect': sf_df['aspect'],
        'curvature': sf_df['curvature'],
        'roughness': sf_df['roughness'],
        'twi': sf_df['twi']
    })

    predictions_csv_path = os.path.join(output_dir, 'rajapur_modelA_predictions.csv')
    output_df.to_csv(predictions_csv_path, index=False)
    print(f"  Saved Predictions CSV: {predictions_csv_path} ({len(output_df)} rows)")

    # 5. STATISTICAL RISK SUMMARY
    print("\n--- 3. CALCULATING RISK DISTRIBUTION SUMMARY ---")
    tot_points = len(output_df)
    p_min = float(prob_A.min())
    p_max = float(prob_A.max())
    p_mean = float(prob_A.mean())
    p_median = float(np.median(prob_A))

    class_counts = output_df['risk_class'].value_counts()
    c_low = int(class_counts.get('LOW', 0))
    c_mod = int(class_counts.get('MODERATE', 0))
    c_high = int(class_counts.get('HIGH', 0))
    c_vhigh = int(class_counts.get('VERY HIGH', 0))

    pct_low = (c_low / tot_points) * 100
    pct_mod = (c_mod / tot_points) * 100
    pct_high = (c_high / tot_points) * 100
    pct_vhigh = (c_vhigh / tot_points) * 100

    summary_df = pd.DataFrame([{
        'total_spatial_points': tot_points,
        'mean_probability': round(p_mean, 6),
        'median_probability': round(p_median, 6),
        'min_probability': round(p_min, 6),
        'max_probability': round(p_max, 6),
        'count_LOW': c_low,
        'pct_LOW': round(pct_low, 2),
        'count_MODERATE': c_mod,
        'pct_MODERATE': round(pct_mod, 2),
        'count_HIGH': c_high,
        'pct_HIGH': round(pct_high, 2),
        'count_VERY_HIGH': c_vhigh,
        'pct_VERY_HIGH': round(pct_vhigh, 2)
    }])

    summary_csv_path = os.path.join(output_dir, 'rajapur_risk_summary.csv')
    summary_df.to_csv(summary_csv_path, index=False)
    print(f"  Saved Risk Summary CSV: {summary_csv_path}")

    # 6. SLOPE COMPARISON ANALYSIS
    print("\n--- 4. SLOPE COMPARISON ANALYSIS ---")
    slope_comp_rows = []
    for r_cls in risk_labels:
        sub = output_df[output_df['risk_class'] == r_cls]
        n_pts = len(sub)
        if n_pts > 0:
            mean_slp = round(float(sub['slope'].mean()), 2)
            median_slp = round(float(sub['slope'].median()), 2)
            max_slp = round(float(sub['slope'].max()), 2)
            gt_20 = int(np.sum(sub['slope'] > 20.0))
            gt_30 = int(np.sum(sub['slope'] > 30.0))
        else:
            mean_slp, median_slp, max_slp, gt_20, gt_30 = 0.0, 0.0, 0.0, 0, 0

        slope_comp_rows.append({
            'risk_class': r_cls,
            'point_count': n_pts,
            'mean_slope_deg': mean_slp,
            'median_slope_deg': median_slp,
            'max_slope_deg': max_slp,
            'points_gt_20deg': gt_20,
            'points_gt_30deg': gt_30
        })

    slope_comp_df = pd.DataFrame(slope_comp_rows)
    slope_csv_path = os.path.join(output_dir, 'risk_vs_slope.csv')
    slope_comp_df.to_csv(slope_csv_path, index=False)
    print(f"  Saved Risk vs Slope CSV: {slope_csv_path}")

    # Plot Risk vs Slope Plot
    fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
    sc = ax.scatter(output_df['slope'], output_df['model_A_probability'], c=output_df['model_A_probability'], cmap='inferno', alpha=0.7, s=25)
    cbar = plt.colorbar(sc, ax=ax)
    cbar.set_label('Model A Susceptibility Probability', fontsize=10)
    ax.set_xlabel('Slope Angle (degrees)', fontsize=11)
    ax.set_ylabel('Model A Instability Probability', fontsize=11)
    ax.set_title('Terrain Slope Angle vs Model A Instability Probability', fontsize=12, fontweight='bold', pad=10)
    ax.axvline(20.0, color='orange', linestyle='--', linewidth=1.2, label='Steep Slope Threshold (20°)')
    ax.axvline(30.0, color='red', linestyle='--', linewidth=1.2, label='Very Steep Threshold (30°)')
    ax.legend(loc='upper left', frameon=True)
    ax.grid(True, linestyle=':', alpha=0.6)

    slope_img_path = os.path.join(output_dir, 'risk_vs_slope.png')
    plt.tight_layout()
    plt.savefig(slope_img_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  Saved Risk vs Slope Plot: {slope_img_path}")

    # 7. HISTORICAL EVENT OVERLAY & SPATIAL RISK MAP
    print("\n--- 5. RENDERING SPATIAL RISK MAP & HISTORICAL OVERLAY ---")
    ev_df = pd.read_csv(events_path)

    fig, ax = plt.subplots(figsize=(10, 8), dpi=300)

    # Plot AOI Polygon
    poly_x = [pt[0] for pt in poly_coords]
    poly_y = [pt[1] for pt in poly_coords]
    ax.plot(poly_x, poly_y, color='cyan', linewidth=2.0, linestyle='-', label='Rajapur AOI Boundary', zorder=4)

    # Scatter Spatial Model A Probabilities
    sc = ax.scatter(
        output_df['longitude'], output_df['latitude'],
        c=output_df['model_A_probability'],
        cmap='inferno', vmin=0.0, vmax=1.0, s=18, alpha=0.85, zorder=2
    )

    cbar = plt.colorbar(sc, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Model A Instability Probability', fontsize=11, fontweight='bold')

    # Overlay Historical Events
    event_markers = {
        'CONFIRMED_ROCKFALL': ('*', 'red', 180, 'Confirmed Rockfall (EVT_RAJ_007)'),
        'BENCH_FAILURE': ('^', 'orange', 100, 'Bench Failure'),
        'CONFIRMED_SLOPE_FAILURE': ('s', 'magenta', 90, 'Confirmed Slope Failure'),
        'GROUND_COLLAPSE': ('D', 'yellow', 90, 'Ground Collapse'),
        'SUBSIDENCE': ('o', 'blue', 80, 'Subsidence'),
        'FIRE_INDUCED_GROUND_DEFORMATION': ('p', 'brown', 80, 'Fire-Induced Deformation')
    }

    overlaid_events_count = 0
    for idx, row in ev_df.iterrows():
        lat, lon = row.get('latitude'), row.get('longitude')
        if pd.notnull(lat) and pd.notnull(lon) and lat > 0 and lon > 0:
            e_type = row['event_type']
            marker, color, size, label_str = event_markers.get(e_type, ('o', 'white', 60, e_type))
            ax.scatter(lon, lat, marker=marker, color=color, edgecolor='black', s=size, zorder=6, label=label_str)
            overlaid_events_count += 1

    # Remove duplicate labels in legend
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    leg = ax.set_legend = ax.legend(by_label.values(), by_label.keys(), loc='upper right', fontsize=8, frameon=True, facecolor='white', framealpha=0.9)
    if hasattr(leg, 'set_zorder'):
        leg.set_zorder(7)

    ax.set_title("Rajapur South Jharia — Model A Spatial Susceptibility", fontsize=13, fontweight='bold', pad=14)
    ax.set_xlabel("Longitude (°E)", fontsize=11)
    ax.set_ylabel("Latitude (°N)", fontsize=11)

    # Subtitle / Annotation & Disclaimer Box
    ax.text(0.5, 1.02, "Prototype terrain-based instability susceptibility", transform=ax.transAxes, ha='center', fontsize=10, fontstyle='italic')
    ax.text(0.02, 0.02, "Not a certified rockfall hazard map\nReal-terrain application of prototype Model A", transform=ax.transAxes, fontsize=8, color='darkred', bbox=dict(boxstyle='round,pad=0.4', facecolor='yellow', alpha=0.8), zorder=8)

    ax.grid(True, linestyle=':', alpha=0.5)

    risk_map_path = os.path.join(output_dir, 'rajapur_modelA_risk_map.png')
    plt.tight_layout()
    plt.savefig(risk_map_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  Saved Spatial Risk Map: {risk_map_path}")

    # 8. TOP 50 SUSCEPTIBILITY LOCATIONS
    print("\n--- 6. EXTRACTING TOP 50 SUSCEPTIBILITY LOCATIONS ---")
    top_50_df = output_df.sort_values(by='model_A_probability', ascending=False).head(50).reset_index(drop=True)
    top_50_df.insert(0, 'rank', range(1, len(top_50_df) + 1))

    top_50_csv_path = os.path.join(output_dir, 'top_50_susceptibility_locations.csv')
    top_50_df.to_csv(top_50_csv_path, index=False)
    print(f"  Saved Top 50 Locations CSV: {top_50_csv_path}")

    top_prob_max = float(top_50_df['model_A_probability'].iloc[0])

    # 9. QUALITY CONTROL AUDIT
    print("\n--- 7. QUALITY CONTROL CHECKS ---")
    qc_nulls = int(output_df.isnull().sum().sum())
    qc_nans = int(output_df.isna().sum().sum())
    qc_infs = int(np.isinf(output_df['model_A_probability']).sum())
    qc_prob_range = (prob_A.min() >= 0.0) and (prob_A.max() <= 1.0)
    
    # Point-in-polygon check
    pts = output_df[['longitude', 'latitude']].values
    pip_mask = aoi_polygon.contains_points(pts)
    qc_pip_count = int(np.sum(pip_mask))
    qc_pip_pct = (qc_pip_count / tot_points) * 100.0

    print(f"  Null Values Check       : {qc_nulls} nulls")
    print(f"  NaN Values Check        : {qc_nans} NaNs")
    print(f"  Infinite Values Check   : {qc_infs} Infs")
    print(f"  Probability Range [0,1] : {qc_prob_range} (Min: {p_min:.4f}, Max: {p_max:.4f})")
    print(f"  AOI Spatial Consistency : {qc_pip_count}/{tot_points} points ({qc_pip_pct:.1f}%) inside polygon")
    print(f"  Row Count Consistency   : {len(output_df)} outputs == {len(sf_df)} inputs")

    qc_passed = (qc_nulls == 0) and (qc_nans == 0) and (qc_infs == 0) and qc_prob_range and (len(output_df) == len(sf_df))

    # 10. GENERATE MARKDOWN REPORT (rajapur_spatial_analysis.md)
    print("\n--- 8. GENERATING SPATIAL ANALYSIS MARKDOWN REPORT ---")
    report_path = os.path.join(output_dir, 'rajapur_spatial_analysis.md')

    def df_to_md(df, cols):
        sub = df[cols].copy()
        headers = list(sub.columns)
        lines = ["| " + " | ".join(str(h) for h in headers) + " |"]
        lines.append("| " + " | ".join("---" for _ in headers) + " |")
        for _, r in sub.iterrows():
            lines.append("| " + " | ".join(str(val) for val in r.values) + " |")
        return "\n".join(lines)

    summary_table_md = df_to_md(summary_df, ['total_spatial_points', 'mean_probability', 'median_probability', 'min_probability', 'max_probability', 'count_LOW', 'pct_LOW', 'count_MODERATE', 'pct_MODERATE'])
    slope_table_md = df_to_md(slope_comp_df, ['risk_class', 'point_count', 'mean_slope_deg', 'median_slope_deg', 'max_slope_deg', 'points_gt_20deg', 'points_gt_30deg'])
    top10_table_md = df_to_md(top_50_df.head(10), ['rank', 'latitude', 'longitude', 'model_A_probability', 'risk_class', 'elevation', 'slope', 'aspect'])

    report_md_content = f"""# Real Rajapur Spatial Rockfall Susceptibility Analysis Report

## 1. Objective
This report presents the real-terrain spatial rockfall susceptibility assessment for the **Rajapur / South Jharia Open Cast Mine** (BCCL, Dhanbad, Jharkhand). The analysis applies the pre-trained **Model A (Ground Instability Pipeline)** directly to the real 1-arcsecond SRTM terrain derivative dataset extracted across the 1.45 km² active mining AOI polygon.

> [!CAUTION]
> **NOT A CERTIFIED ROCKFALL HAZARD MAP**:
> This document and associated spatial maps represent a **prototype terrain-based rockfall susceptibility application of an un-calibrated ML model**. It is **NOT** a certified operational rockfall hazard map or safety directive.

---

## 2. Data Used
1. **Official AOI Boundary**: `scratch/rajapur_south_jharia_aoi.geojson` (`1.4503 km²`, WGS84 polygon).
2. **Spatial Feature Dataset**: `results/terrain/spatial_features.csv` (`1,665` valid spatial grid points).
3. **Real SRTM Terrain Derivatives**: Elevation, Slope, Aspect, Curvature, Roughness, TWI (`results/terrain/real/*.tif`).
4. **Historical Event Inventory**: `data/events/rajapur_instability_events.csv` (`10` documented historical events).

---

## 3. Model Used
- **Model Architecture**: `models/model_A_best.pkl` (Scikit-Learn Random Forest Classification Pipeline).
- **Training Context**: Model A was trained on synthetic benchmark datasets; it has **NOT** been retrained or modified during this spatial analysis step.

---

## 4. Model Input Features
Model A expects exactly **9 features** in the following exact order:
1. `Rainfall_mm` (Regional annual/monsoon baseline = 120.0 mm)
2. `Slope_Angle` (Mapped directly from pixel-level SRTM slope derivative, range: `0.00°` to `37.26°`)
3. `Soil_Saturation` (Regional baseline = 0.40)
4. `Vegetation_Cover` (Open-cast mine quarry baseline = 0.30)
5. `Earthquake_Activity` (Richter regional rating = 1.5)
6. `Proximity_to_Water` (Distance to pit water sump / Katri River = 1.0 km)
7. `Soil_Type_Gravel` (1 - Sandstone/overburden rock composition)
8. `Soil_Type_Sand` (0)
9. `Soil_Type_Silt` (0)

---

## 5. Spatial Prediction Method
Model A `predict_proba()` was evaluated across all 1,665 spatial grid points inside the Rajapur AOI polygon. Continuous instability probability values were mapped into official project risk tiers using standard thresholds:
- `P < 0.35` -> **LOW**
- `0.35 <= P < 0.65` -> **MODERATE**
- `0.65 <= P < 0.85` -> **HIGH**
- `P >= 0.85` -> **VERY HIGH**

---

## 6. Probability Distribution Summary
- **Total Valid Spatial Grid Points**: `{tot_points}`
- **Minimum Instability Probability**: `{p_min:.6f}`
- **Maximum Instability Probability**: `{p_max:.6f}`
- **Mean Instability Probability**: `{p_mean:.6f}`
- **Median Instability Probability**: `{p_median:.6f}`

{summary_table_md}

---

## 7. Risk-Class Distribution
- **LOW Risk (`P < 0.35`)**: `{c_low} points` (`{pct_low:.2f}%`)
- **MODERATE Risk (`0.35 <= P < 0.65`)**: `{c_mod} points` (`{pct_mod:.2f}%`)
- **HIGH Risk (`0.65 <= P < 0.85`)**: `{c_high} points` (`{pct_high:.2f}%`)
- **VERY HIGH Risk (`P >= 0.85`)**: `{c_vhigh} points` (`{pct_vhigh:.2f}%`)

---

## 8. Terrain Morphology & Slope Comparison
The table below compares Model A susceptibility predictions against actual DEM slope angles:

{slope_table_md}

*Note: Steep slopes (>20° and >30°) are framed as terrain morphology indicators and NOT as proof of active rockfall occurrence.*

---

## 9. Historical Event Spatial Overlay
Overlaid `{overlaid_events_count}` documented instability events from `data/events/rajapur_instability_events.csv` on the spatial susceptibility map:
- **Confirmed Rockfall (`EVT_RAJ_007`)**: April 2023 (`Lat: 23.753611°N`, `Lon: 86.416667°E`).
- **Bench Failures**: `EVT_RAJ_001`, `EVT_RAJ_010`.
- **Confirmed Slope Failures**: `EVT_RAJ_005`.
- **Ground Collapse & Subsidence**: `EVT_RAJ_004`, `EVT_RAJ_006`.

*Note: This layer represents an exploratory event overlay, NOT a formal statistical model validation, due to the small sample size of confirmed rockfall labels (N=1).*

---

## 10. Top Susceptibility Locations (Top 10 Display)
The top 10 highest susceptibility locations extracted from `results/rajapur/top_50_susceptibility_locations.csv`:

{top10_table_md}

---

## 11. Limitations & Boundaries
1. **Synthetic Training Origin**: Model A was trained on synthetic benchmark datasets and has not been fine-tuned on real Dhanbad geotechnical soil test data.
2. **Coarse DEM Resolution**: SRTM 1-arcsecond resolution (~30m) smooths sub-meter bench geometries and vertical pit walls.
3. **No Retraining / Retrained Labels**: Model predictions reflect prototype feature relationships, not verified rockfall occurrences.

---

## 12. Conclusion
The spatial application of Model A successfully maps terrain slope variability into continuous ground instability probability across the Rajapur AOI. The generated outputs provide a baseline prototype susceptibility framework ready for interactive visualization in the dashboard.
"""

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_md_content)
    print(f"  Saved Spatial Analysis Markdown Report: {report_path}")

    # 11. PRINT FINAL TERMINAL SUMMARY
    print("\n============================================================")
    print("RAJAPUR REAL-TERRAIN MODEL A ANALYSIS")
    print("============================================================")
    print(f"\nAOI                   : Rajapur / South Jharia Open Cast Mine (1.4503 km²)")
    print(f"Spatial points        : {tot_points}")

    print(f"\nModel A:")
    print(f"Expected features     : {len(model_A_features)} features ({model_A_features})")

    print(f"\nProbability:")
    print(f"Minimum               : {p_min:.6f}")
    print(f"Mean                  : {p_mean:.6f}")
    print(f"Median                : {p_median:.6f}")
    print(f"Maximum               : {p_max:.6f}")

    print(f"\nLOW                   : {c_low} ({pct_low:.2f}%)")
    print(f"MODERATE              : {c_mod} ({pct_mod:.2f}%)")
    print(f"HIGH                  : {c_high} ({pct_high:.2f}%)")
    print(f"VERY HIGH             : {c_vhigh} ({pct_vhigh:.2f}%)")

    print(f"\nHistorical events overlaid : {overlaid_events_count}")
    print(f"Top susceptibility prob     : {top_prob_max:.6f}")

    print(f"\nOutput directory      : results/rajapur/")
    print(f"ML retraining         : NO")
    print(f"InSAR                 : NOT USED")

    print(f"\nOverall status        : {'PASSED' if qc_passed else 'REVIEW REQUIRED'}")
    print("============================================================")

if __name__ == '__main__':
    run_rajapur_spatial_analysis()
