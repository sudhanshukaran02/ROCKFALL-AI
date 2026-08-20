"""
Unified Evaluation Script for the Prototype Risk-Fusion System.

IMPORTANT DISCLAIMER:
Because Dataset 1 (Geotechnical) and Dataset 2 (Meteorological) lack spatial-temporal
joining keys (e.g. timestamps or lat/long), this evaluation generates paired synthetic
scenarios across test observations. This evaluation is strictly labeled as a
"Scenario-based prototype evaluation" and does NOT constitute real-world validation.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from src.config import DATASET_1_PATH, DATASET_2_PATH, FUSION_RESULTS_DIR, RISK_MATRIX
from src.risk_fusion_engine import RiskFusionEngine

# Ensure output folder exists
os.makedirs(FUSION_RESULTS_DIR, exist_ok=True)

print("="*70)
print("EXECUTING SCENARIO-BASED PROTOTYPE EVALUATION FOR RISK FUSION ENGINE")
print("="*70)

# Initialize Fusion Engine (without retraining any models)
engine = RiskFusionEngine()

# Load Datasets
df1 = pd.read_csv(DATASET_1_PATH)
df2 = pd.read_csv(DATASET_2_PATH)

# Feature Lists
features_A = engine.features_A
features_B = engine.features_B

# Create 500 Scenario Samples by pairing row samples from Dataset 1 and Dataset 2
np.random.seed(42)
num_scenarios = 500

sample_indices_1 = np.random.choice(len(df1), size=num_scenarios, replace=True)
sample_indices_2 = np.random.choice(len(df2), size=num_scenarios, replace=True)

scenarios = []

for idx in range(num_scenarios):
    row1 = df1.iloc[sample_indices_1[idx]].to_dict()
    row2 = df2.iloc[sample_indices_2[idx]].to_dict()
    
    # Run Fusion Engine
    out = engine.predict(row1, row2)
    
    res = {
        'Scenario_ID': idx + 1,
        'Dataset1_Row': sample_indices_1[idx],
        'Dataset2_Row': sample_indices_2[idx],
        'Ground_Instability_Prob': out['instability_probability'],
        'Instability_Class': out['instability_class'],
        'Weather_Risk_Class': out['weather_risk'],
        'Prob_Weather_Low': out['weather_probabilities']['Low'],
        'Prob_Weather_Moderate': out['weather_probabilities']['Moderate'],
        'Prob_Weather_High': out['weather_probabilities']['High'],
        'Prob_Weather_VeryHigh': out['weather_probabilities']['Very High'],
        'Final_Risk_Level': out['final_risk_level'],
        'Rockfall_Hazard_Index': out['risk_score'],
        'Top_Risk_Factors': " | ".join(out['top_risk_factors'])
    }
    scenarios.append(res)

scenario_df = pd.DataFrame(scenarios)

# Save Scenario Results CSV
scenario_csv_path = os.path.join(FUSION_RESULTS_DIR, 'scenario_results.csv')
scenario_df.to_csv(scenario_csv_path, index=False)
print(f"\n[Saved] {scenario_csv_path} ({num_scenarios} scenarios)")

# Generate Summary Metrics
risk_counts = scenario_df['Final_Risk_Level'].value_counts()
risk_pcts = (scenario_df['Final_Risk_Level'].value_counts(normalize=True) * 100).round(2)

summary_rows = []
for level in ['LOW', 'MODERATE', 'HIGH', 'CRITICAL']:
    count = int(risk_counts.get(level, 0))
    pct = float(risk_pcts.get(level, 0.0))
    summary_rows.append({
        'Risk_Level': level,
        'Count': count,
        'Percentage': pct,
        'Evaluation_Note': 'Scenario-based prototype evaluation'
    })

summary_df = pd.DataFrame(summary_rows)
summary_csv_path = os.path.join(FUSION_RESULTS_DIR, 'fusion_summary.csv')
summary_df.to_csv(summary_csv_path, index=False)
print(f"[Saved] {summary_csv_path}")

print("\n--- PROTOTYPE EVALUATION RISK DISTRIBUTION ---")
print(summary_df.to_string(index=False))

# -------------------------------------------------------------
# PLOT 1: Risk Level Distribution Chart
# -------------------------------------------------------------
plt.figure(figsize=(9, 6))
colors = {'LOW': '#2ecc71', 'MODERATE': '#f39c12', 'HIGH': '#e67e22', 'CRITICAL': '#e74c3c'}
bar_colors = [colors.get(l, '#3498db') for l in summary_df['Risk_Level']]

bars = plt.bar(summary_df['Risk_Level'], summary_df['Count'], color=bar_colors, edgecolor='black', alpha=0.85)

for bar in bars:
    yval = bar.get_height()
    pct = (yval / num_scenarios) * 100
    plt.text(bar.get_x() + bar.get_width()/2.0, yval + 5, f'{yval} ({pct:.1f}%)', ha='center', va='bottom', fontweight='bold')

plt.title('Prototype Risk Fusion: Final Risk Level Distribution (500 Scenarios)')
plt.xlabel('Final Rockfall Risk Level')
plt.ylabel('Scenario Count')
plt.ylim(0, max(summary_df['Count']) * 1.18)
plt.grid(axis='y', linestyle='--', alpha=0.4)
plt.tight_layout()

dist_plot_path = os.path.join(FUSION_RESULTS_DIR, 'risk_distribution.png')
plt.savefig(dist_plot_path, dpi=300)
plt.close()
print(f"[Saved] {dist_plot_path}")

# -------------------------------------------------------------
# PLOT 2: Heatmap of 2D Risk Matrix Cross-Tabulation
# -------------------------------------------------------------
matrix_crosstab = pd.crosstab(
    scenario_df['Instability_Class'],
    scenario_df['Weather_Risk_Class'],
    margins=False
)

# Reorder index and columns
instability_order = ['LOW', 'MODERATE', 'HIGH', 'VERY HIGH']
weather_order = ['Low', 'Moderate', 'High', 'Very High']

matrix_crosstab = matrix_crosstab.reindex(index=instability_order, columns=weather_order, fill_value=0)

plt.figure(figsize=(9, 7))
sns.heatmap(matrix_crosstab, annot=True, fmt='d', cmap='YlOrRd', cbar=True, linewidths=1, linecolor='white')
plt.title('Prototype 2D Risk Matrix Cross-Tabulation (Scenario Frequencies)')
plt.xlabel('Model B Meteorological Risk Class')
plt.ylabel('Model A Ground Instability Class')
plt.tight_layout()

matrix_plot_path = os.path.join(FUSION_RESULTS_DIR, 'risk_matrix.png')
plt.savefig(matrix_plot_path, dpi=300)
plt.close()
print(f"[Saved] {matrix_plot_path}")

print("\nUnified Fusion Layer Evaluation successfully completed!")
