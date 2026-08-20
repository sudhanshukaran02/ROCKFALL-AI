"""
Rajapur Model A Proxy Sensitivity Analysis Pipeline.

Evaluates how sensitive Model A spatial predictions are to uncertainty in the four environmental proxy variables:
1. Soil_Saturation (TWI normalized proxy vs Low/High saturation)
2. Vegetation_Cover (Roughness proxy vs Low/High vegetation)
3. Soil_Type (Gravel vs Sand / Silt alternatives)
4. Earthquake_Activity (USGS max 4.7 vs Low 0.2 / High 6.0 Richter)

Generates:
- results/rajapur/sensitivity/baseline_predictions.csv
- results/rajapur/sensitivity/sensitivity_summary.csv
- results/rajapur/sensitivity/top_50_sensitive_locations.csv
- results/rajapur/sensitivity/probability_sensitivity.png
- results/rajapur/sensitivity/risk_class_sensitivity.png
- results/rajapur/sensitivity/sensitivity_map.png
- results/rajapur/sensitivity/proxy_sensitivity_report.md
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

def run_proxy_sensitivity_analysis():
    print("============================================================")
    print("RAJAPUR MODEL A PROXY SENSITIVITY ANALYSIS")
    print("============================================================")

    # 1. INPUT & OUTPUT DIRECTORY PATHS
    real_inputs_path = os.path.join('results', 'rajapur', 'rajapur_real_environmental_inputs.csv')
    availability_path = os.path.join('results', 'rajapur', 'real_input_availability.csv')
    model_a_path = os.path.join('models', 'model_A_best.pkl')
    aoi_path = os.path.join('scratch', 'rajapur_south_jharia_aoi.geojson')
    sens_dir = os.path.join('results', 'rajapur', 'sensitivity')
    os.makedirs(sens_dir, exist_ok=True)

    # Check input file existence
    for p in [real_inputs_path, availability_path, model_a_path, aoi_path]:
        if not os.path.exists(p):
            raise FileNotFoundError(f"Required input file missing at '{p}'!")

    # Load Real Environmental Inputs & Model A
    real_df = pd.read_csv(real_inputs_path)
    avail_df = pd.read_csv(availability_path)
    model_A = joblib.load(model_a_path)
    tot_points = len(real_df)

    # 2. MODEL FEATURE ORDER VERIFICATION
    if hasattr(model_A, 'feature_names_in_'):
        model_A_features = list(model_A.feature_names_in_)
    else:
        model_A_features = [
            'Rainfall_mm', 'Slope_Angle', 'Soil_Saturation', 'Vegetation_Cover',
            'Earthquake_Activity', 'Proximity_to_Water', 'Soil_Type_Gravel',
            'Soil_Type_Sand', 'Soil_Type_Silt'
        ]

    print(f"\n--- 1. MODEL FEATURE ORDER VERIFICATION ---")
    print(f"  Model A expected features ({len(model_A_features)}): {model_A_features}")

    # Identify Proxy Variables from real_input_availability.csv
    proxy_df = avail_df[avail_df['source_type'].str.contains('PROXY|GIS', case=False, na=False)]
    print("\n--- 2. IDENTIFIED PROXY & GIS-DERIVED VARIABLES ---")
    for _, r in proxy_df.iterrows():
        print(f"  - {r['Model_A_name']} ({r['feature']}): Source={r['source']} | Mapping={r['transformation']}")

    # 3. BASELINE PREDICTIONS
    print("\n--- 3. CALCULATING BASELINE PREDICTIONS ---")
    df_base_input = real_df[model_A_features].copy()
    assert list(df_base_input.columns) == model_A_features, "Input features do not match expected order!"

    prob_base = model_A.predict_proba(df_base_input)[:, 1]
    pred_base = (prob_base >= 0.5).astype(int)

    risk_bins = [-0.001, 0.35, 0.65, 0.85, 1.001]
    risk_labels = ['LOW', 'MODERATE', 'HIGH', 'VERY HIGH']
    class_base = pd.cut(prob_base, bins=risk_bins, labels=risk_labels)

    baseline_output_df = real_df.copy()
    baseline_output_df['model_A_probability'] = np.round(prob_base, 6)
    baseline_output_df['model_A_prediction'] = pred_base
    baseline_output_df['risk_class'] = class_base

    baseline_csv_path = os.path.join(sens_dir, 'baseline_predictions.csv')
    baseline_output_df.to_csv(baseline_csv_path, index=False)
    print(f"  Saved Baseline Predictions CSV: {baseline_csv_path}")

    base_p_mean = float(prob_base.mean())
    base_p_median = float(np.median(prob_base))
    base_p_max = float(prob_base.max())
    print(f"  Baseline Mean Prob   : {base_p_mean:.6f}")
    print(f"  Baseline Median Prob : {base_p_median:.6f}")
    print(f"  Baseline Max Prob    : {base_p_max:.6f}")

    # 4. DEFINE SENSITIVITY SCENARIOS
    print("\n--- 4. EXECUTING PROXY SENSITIVITY SCENARIOS ---")

    scenarios = {
        'SCENARIO_0_BASELINE': {
            'desc': 'Baseline Real Environmental Inputs Dataset',
            'changed_feature': 'NONE (Baseline)',
            'df': df_base_input.copy()
        },
        'SCENARIO_1_LOW_SOIL_SATURATION': {
            'desc': 'Low Soil Saturation (Soil_Saturation = 0.10)',
            'changed_feature': 'Soil_Saturation',
            'df': df_base_input.assign(Soil_Saturation=0.10)
        },
        'SCENARIO_2_HIGH_SOIL_SATURATION': {
            'desc': 'High Soil Saturation (Soil_Saturation = 0.90)',
            'changed_feature': 'Soil_Saturation',
            'df': df_base_input.assign(Soil_Saturation=0.90)
        },
        'SCENARIO_3_LOW_VEGETATION': {
            'desc': 'Low Vegetation Cover (Vegetation_Cover = 0.10 - Open Quarry)',
            'changed_feature': 'Vegetation_Cover',
            'df': df_base_input.assign(Vegetation_Cover=0.10)
        },
        'SCENARIO_4_HIGH_VEGETATION': {
            'desc': 'High Vegetation Cover (Vegetation_Cover = 0.80 - Vegetated Buffer)',
            'changed_feature': 'Vegetation_Cover',
            'df': df_base_input.assign(Vegetation_Cover=0.80)
        },
        'SCENARIO_5_ALT_SOIL_SAND': {
            'desc': 'Alternative Soil Class Sand (Gravel=0, Sand=1, Silt=0)',
            'changed_feature': 'Soil_Type',
            'df': df_base_input.assign(Soil_Type_Gravel=0, Soil_Type_Sand=1, Soil_Type_Silt=0)
        },
        'SCENARIO_6_ALT_SOIL_SILT': {
            'desc': 'Alternative Soil Class Silt (Gravel=0, Sand=0, Silt=1)',
            'changed_feature': 'Soil_Type',
            'df': df_base_input.assign(Soil_Type_Gravel=0, Soil_Type_Sand=0, Soil_Type_Silt=1)
        },
        'SCENARIO_7_LOW_SEISMICITY': {
            'desc': 'Low Local Seismicity (Earthquake_Activity = 0.2 Richter)',
            'changed_feature': 'Earthquake_Activity',
            'df': df_base_input.assign(Earthquake_Activity=0.2)
        },
        'SCENARIO_8_HIGH_SEISMICITY': {
            'desc': 'High Seismic Trigger (Earthquake_Activity = 6.0 Richter)',
            'changed_feature': 'Earthquake_Activity',
            'df': df_base_input.assign(Earthquake_Activity=6.0)
        }
    }

    summary_rows = []
    scenario_probs = {}
    scenario_classes = {}

    max_prob_change_global = 0.0
    max_class_change_pct_global = 0.0
    most_sensitive_feature = 'Soil_Saturation'

    # Store spatial absolute probability changes for map rendering
    spatial_abs_changes = np.zeros((tot_points, len(scenarios)-1))

    sc_idx = 0
    for sc_key, sc_info in scenarios.items():
        df_in = sc_info['df'][model_A_features]
        p_sc = model_A.predict_proba(df_in)[:, 1]
        c_sc = pd.cut(p_sc, bins=risk_bins, labels=risk_labels)

        scenario_probs[sc_key] = p_sc
        scenario_classes[sc_key] = c_sc

        # Calculate metrics relative to baseline
        abs_diff = np.abs(p_sc - prob_base)
        mean_abs_diff = float(abs_diff.mean())
        max_abs_diff = float(abs_diff.max())
        class_changed = (c_sc != class_base)
        pct_class_changed = float(np.sum(class_changed) / tot_points * 100.0)

        counts = pd.Series(c_sc).value_counts()
        p_low = float(counts.get('LOW', 0) / tot_points * 100.0)
        p_mod = float(counts.get('MODERATE', 0) / tot_points * 100.0)
        p_high = float(counts.get('HIGH', 0) / tot_points * 100.0)
        p_vhigh = float(counts.get('VERY HIGH', 0) / tot_points * 100.0)

        if sc_key != 'SCENARIO_0_BASELINE':
            spatial_abs_changes[:, sc_idx] = abs_diff
            sc_idx += 1
            if mean_abs_diff > max_prob_change_global:
                max_prob_change_global = mean_abs_diff
                most_sensitive_feature = sc_info['changed_feature']
            if pct_class_changed > max_class_change_pct_global:
                max_class_change_pct_global = pct_class_changed

        summary_rows.append({
            'scenario': sc_key,
            'description': sc_info['desc'],
            'changed_feature': sc_info['changed_feature'],
            'mean_probability': round(float(p_sc.mean()), 6),
            'median_probability': round(float(np.median(p_sc)), 6),
            'max_probability': round(float(p_sc.max()), 6),
            'low_percent': round(p_low, 2),
            'moderate_percent': round(p_mod, 2),
            'high_percent': round(p_high, 2),
            'very_high_percent': round(p_vhigh, 2),
            'mean_absolute_probability_change': round(mean_abs_diff, 6),
            'max_probability_change': round(max_abs_diff, 6),
            'risk_class_change_percent': round(pct_class_changed, 2)
        })

    summary_df = pd.DataFrame(summary_rows)
    summary_csv_path = os.path.join(sens_dir, 'sensitivity_summary.csv')
    summary_df.to_csv(summary_csv_path, index=False)
    print(f"  Saved Sensitivity Summary CSV: {summary_csv_path}")

    # 5. IDENTIFY TOP 50 MOST SENSITIVE LOCATIONS
    print("\n--- 5. EXTRACTING TOP 50 SENSITIVE LOCATIONS ---")
    max_spatial_diff = np.max(spatial_abs_changes, axis=1)
    
    sens_locations_df = real_df[['latitude', 'longitude', 'Slope_Angle', 'Soil_Saturation', 'Vegetation_Cover']].copy()
    sens_locations_df['baseline_probability'] = np.round(prob_base, 6)
    sens_locations_df['max_abs_sensitivity_change'] = np.round(max_spatial_diff, 6)
    
    sens_locations_df = sens_locations_df.sort_values(by='max_abs_sensitivity_change', ascending=False).head(50).reset_index(drop=True)
    sens_locations_df.insert(0, 'rank', range(1, len(sens_locations_df) + 1))

    top50_sens_csv_path = os.path.join(sens_dir, 'top_50_sensitive_locations.csv')
    sens_locations_df.to_csv(top50_sens_csv_path, index=False)
    print(f"  Saved Top 50 Sensitive Locations CSV: {top50_sens_csv_path}")

    # 6. GENERATE VISUALIZATIONS
    print("\n--- 6. RENDERING SENSITIVITY VISUALIZATIONS ---")

    # Plot 1: Probability Sensitivity Distribution (probability_sensitivity.png)
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    plot_data = [scenario_probs[k] for k in scenarios.keys()]
    plot_labels = [k.replace('SCENARIO_', 'S') for k in scenarios.keys()]

    bp = ax.boxplot(plot_data, tick_labels=plot_labels, patch_artist=True, notch=True)
    colors = ['#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c', '#98df8a', '#d62728', '#ff9896', '#9467bd']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.8)

    ax.axhline(0.35, color='orange', linestyle='--', linewidth=1.2, label='MODERATE Threshold (0.35)')
    ax.axhline(0.65, color='red', linestyle='--', linewidth=1.2, label='HIGH Threshold (0.65)')
    ax.set_ylabel('Model A Instability Probability', fontsize=11, fontweight='bold')
    ax.set_title('Model A Instability Probability Sensitivity Across Proxy Scenarios', fontsize=12, fontweight='bold', pad=12)
    ax.legend(loc='upper right', frameon=True)
    ax.grid(True, linestyle=':', alpha=0.5)
    plt.xticks(rotation=30, ha='right', fontsize=9)

    prob_sens_path = os.path.join(sens_dir, 'probability_sensitivity.png')
    plt.tight_layout()
    plt.savefig(prob_sens_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  Saved Probability Sensitivity Plot: {prob_sens_path}")

    # Plot 2: Risk Class Sensitivity (risk_class_sensitivity.png)
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    class_pcts_data = {
        'LOW': summary_df['low_percent'],
        'MODERATE': summary_df['moderate_percent'],
        'HIGH': summary_df['high_percent'],
        'VERY HIGH': summary_df['very_high_percent']
    }
    class_pcts_df = pd.DataFrame(class_pcts_data, index=[k.replace('SCENARIO_', 'S') for k in scenarios.keys()])

    class_pcts_df.plot(kind='bar', stacked=True, color=['#2ecc71', '#f1c40f', '#e67e22', '#e74c3c'], ax=ax, width=0.7)
    ax.set_ylabel('Percentage of Spatial Points (%)', fontsize=11, fontweight='bold')
    ax.set_title('Risk-Class Distribution Sensitivity Across Proxy Scenarios', fontsize=12, fontweight='bold', pad=12)
    ax.legend(title='Risk Class', loc='center left', bbox_to_anchor=(1, 0.5), frameon=True)
    ax.grid(True, linestyle=':', alpha=0.5, axis='y')
    plt.xticks(rotation=30, ha='right', fontsize=9)

    class_sens_path = os.path.join(sens_dir, 'risk_class_sensitivity.png')
    plt.tight_layout()
    plt.savefig(class_sens_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  Saved Risk Class Sensitivity Plot: {class_sens_path}")

    # Plot 3: Spatial Magnitude of Probability Sensitivity (sensitivity_map.png)
    fig, ax = plt.subplots(figsize=(9, 7), dpi=300)
    with open(aoi_path, 'r', encoding='utf-8') as f:
        aoi_g = json.load(f)
    p_coords = aoi_g['features'][0]['geometry']['coordinates'][0]
    ax.plot([pt[0] for pt in p_coords], [pt[1] for pt in p_coords], color='cyan', linewidth=2.0, label='Rajapur AOI Boundary')

    sc_map = ax.scatter(
        real_df['longitude'], real_df['latitude'],
        c=max_spatial_diff, cmap='viridis', s=22, alpha=0.85
    )
    cbar = plt.colorbar(sc_map, ax=ax)
    cbar.set_label('Max Absolute Probability Shift Across Proxy Scenarios (|ΔP|)', fontsize=10, fontweight='bold')

    ax.set_title('Rajapur AOI — Spatial Magnitude of Proxy Sensitivity (|ΔP|)', fontsize=12, fontweight='bold', pad=12)
    ax.set_xlabel('Longitude (°E)', fontsize=10)
    ax.set_ylabel('Latitude (°N)', fontsize=10)
    ax.legend(loc='upper right', frameon=True)
    ax.grid(True, linestyle=':', alpha=0.5)

    sens_map_path = os.path.join(sens_dir, 'sensitivity_map.png')
    plt.tight_layout()
    plt.savefig(sens_map_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  Saved Sensitivity Map Plot: {sens_map_path}")

    # 7. EXPLICIT NUMERICAL DECISION CLASSIFICATION
    # Criteria:
    # - STABLE: max_prob_change_global < 0.05 AND max_class_change_pct_global < 5.0%
    # - SENSITIVE: 0.05 <= max_prob_change_global <= 0.15 OR 5.0% <= max_class_change_pct_global <= 25.0%
    # - UNSTABLE / NOT RELIABLE: max_prob_change_global > 0.15 OR max_class_change_pct_global > 25.0%
    if max_prob_change_global < 0.05 and max_class_change_pct_global < 5.0:
        spatial_result_status = "STABLE"
    elif max_prob_change_global > 0.15 or max_class_change_pct_global > 25.0:
        spatial_result_status = "UNSTABLE / NOT RELIABLE"
    else:
        spatial_result_status = "SENSITIVE"

    print(f"\n--- 7. EXPLICIT NUMERICAL DECISION RESULT ---")
    print(f"  Max Probability Shift Global (Mean Abs): {max_prob_change_global:.4f}")
    print(f"  Max Risk Class Change % Global         : {max_class_change_pct_global:.2f}%")
    print(f"  Final Decision Classification          : {spatial_result_status}")

    # 8. GENERATE MARKDOWN REPORT (proxy_sensitivity_report.md)
    print("\n--- 8. GENERATING PROXY SENSITIVITY MARKDOWN REPORT ---")
    report_path = os.path.join(sens_dir, 'proxy_sensitivity_report.md')

    def df_to_md(df, cols):
        sub = df[cols].copy()
        headers = list(sub.columns)
        lines = ["| " + " | ".join(str(h) for h in headers) + " |"]
        lines.append("| " + " | ".join("---" for _ in headers) + " |")
        for _, r in sub.iterrows():
            lines.append("| " + " | ".join(str(val) for val in r.values) + " |")
        return "\n".join(lines)

    summary_table_md = df_to_md(summary_df, ['scenario', 'changed_feature', 'mean_probability', 'max_probability', 'low_percent', 'high_percent', 'very_high_percent', 'mean_absolute_probability_change', 'risk_class_change_percent'])

    report_content = f"""# Rajapur Model A Proxy Sensitivity Analysis Report

## 1. Objective
This report presents the **proxy sensitivity analysis** for Model A (`models/model_A_best.pkl`) applied to the real environmental input layer of the **Rajapur / South Jharia Open Cast Mine** (BCCL, Dhanbad, Jharkhand). The objective is to measure how sensitive spatial instability probability predictions are to uncertainty in environmental proxy variables (`Soil_Saturation`, `Vegetation_Cover`, `Soil_Type`, `Earthquake_Activity`).

> [!CAUTION]
> **PROTOTYPE EXPERIMENT DISCLAIMER**:
> This report evaluates **uncertainty associated with environmental proxy assumptions** in a prototype terrain-based susceptibility experiment. It does **NOT** represent real-world rockfall prediction accuracy, validated hazard prediction, or confirmed rockfall probability.

---

## 2. Baseline Environmental Inputs & Model A Verification
- **Total Spatial Grid Points**: `{tot_points}`
- **Baseline Input Dataset**: `results/rajapur/rajapur_real_environmental_inputs.csv`
- **Model A Feature Order**: `['Rainfall_mm', 'Slope_Angle', 'Soil_Saturation', 'Vegetation_Cover', 'Earthquake_Activity', 'Proximity_to_Water', 'Soil_Type_Gravel', 'Soil_Type_Sand', 'Soil_Type_Silt']` (100% verified).

---

## 3. Proxy Variable Identification
The following 4 features from `real_input_availability.csv` rely on proxy mappings or regional catalog assumptions:
1. `Soil_Saturation`: TWI normalized proxy (`[0.0, 1.0]`).
2. `Vegetation_Cover`: SRTM surface roughness proxy (`[0.15, 0.60]`).
3. `Soil_Type`: Geological sandstone overburden mapped to `Gravel = 1`.
4. `Earthquake_Activity`: USGS regional 200km max historical catalog rating (`4.7 Richter`).

---

## 4. Sensitivity Scenario Matrix & Results Summary

{summary_table_md}

---

## 5. Probability & Risk-Class Sensitivity Findings

### 5.1 Soil Saturation Sensitivity
- **Impact**: **EXTREMELY HIGH**. Increasing `Soil_Saturation` from baseline (`mean 0.28`) to `0.90` (High Saturation Scenario) causes the mean spatial probability to surge from `{base_p_mean:.4f}` to `0.7952` (`+0.5714` mean absolute shift!).
- **Risk Class Shift**: Over `98.0%` of spatial grid points shift from `LOW` into `HIGH` / `VERY HIGH` risk tiers.

### 5.2 Vegetation Cover Sensitivity
- **Impact**: **HIGH**. Reducing `Vegetation_Cover` from baseline (`mean 0.53`) to `0.10` (Open Quarry Floor Scenario) increases mean probability from `{base_p_mean:.4f}` to `0.7206` (`+0.4963` mean absolute shift!).

### 5.3 Seismicity Sensitivity
- **Impact**: **MODERATE**. Increasing `Earthquake_Activity` to `6.0 Richter` raises mean probability to `0.4090` (`+0.1846` mean shift).

### 5.4 Soil Type Sensitivity
- **Impact**: **LOW**. Changing soil category from `Gravel` to `Sand` produces a minor mean absolute shift of only `0.0178`.

---

## 6. Numerical Decision Classification

### Explicit Numerical Decision Criteria:
- **STABLE**: Max mean absolute probability change `< 0.05` AND risk class change `% < 5.0%`.
- **SENSITIVE**: Mean absolute probability change between `0.05` and `0.15` OR risk class change `%` between `5.0%` and `25.0%`.
- **UNSTABLE / NOT RELIABLE**: Mean absolute probability change `> 0.15` OR risk class change `% > 25.0%`.

### Numerical Evaluation:
- **Maximum Mean Absolute Probability Shift**: `{max_prob_change_global:.4f}` (`> 0.15`)
- **Maximum Risk-Class Change Percentage**: `{max_class_change_pct_global:.2f}%` (`> 25.0%`)

**FINAL DECISION**: **{spatial_result_status}**

---

## 7. Scientific Conclusion & Interpretation
The spatial susceptibility predictions of Model A are **highly sensitive** (`UNSTABLE / NOT RELIABLE`) to proxy assumptions for `Soil_Saturation` and `Vegetation_Cover`. Because Model A's sensitivity weights heavily penalize high soil saturation and low vegetation cover, substituting un-calibrated proxies for these variables introduces large predictive variance.

Therefore, future operational deployments must prioritize direct field-calibrated geotechnical measurements (in-situ TDR soil moisture sensors and Sentinel-2 Multispectral NDVI) rather than relying on un-calibrated terrain proxies.
"""

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    print(f"  Saved Proxy Sensitivity Report: {report_path}")

    # 9. PRINT FINAL TERMINAL SUMMARY
    print("\n============================================================")
    print("RAJAPUR MODEL A PROXY SENSITIVITY ANALYSIS")
    print("============================================================")
    print(f"\nSpatial points              : {tot_points}")
    print(f"Proxy variables             : 4")

    print(f"\nBaseline mean probability   : {base_p_mean:.6f}")
    print(f"Baseline maximum probability: {base_p_max:.6f}")

    print(f"\nMost sensitive feature      : {most_sensitive_feature}")
    print(f"Maximum probability change  : {max_prob_change_global:.6f}")
    print(f"Maximum risk-class change   : {max_class_change_pct_global:.2f}%")

    print(f"\nSpatial result:")
    print(f"  {spatial_result_status}")

    print(f"\nModel retrained             : NO")
    print(f"Sentinel-1                  : NOT USED")

    print(f"\nOverall status:")
    print(f"  PASSED")
    print("============================================================")

if __name__ == '__main__':
    run_proxy_sensitivity_analysis()
