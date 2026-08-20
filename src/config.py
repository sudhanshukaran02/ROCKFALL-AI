"""
Configuration parameters for the Prototype Risk-Fusion System.

IMPORTANT DISCLAIMER:
This system is a PROTOTYPE decision-support engine. All thresholds, risk matrices,
and scoring weights are model-derived heuristic prototypes and are NOT operational
safety instructions or scientifically validated hazard thresholds.
"""

import os

# Model File Paths
MODEL_A_PATH = os.path.join('models', 'model_A_best.pkl')
MODEL_B_PATH = os.path.join('models', 'model_B_best.pkl')

# Dataset Paths
DATASET_1_PATH = os.path.join('data', 'dataset1.csv')
DATASET_2_PATH = os.path.join('data', 'dataset2.csv')

# Output Directories
FUSION_RESULTS_DIR = os.path.join('results', 'fusion')

# Model Features
MODEL_A_FEATURES = [
    'Rainfall_mm', 'Slope_Angle', 'Soil_Saturation', 'Vegetation_Cover',
    'Earthquake_Activity', 'Proximity_to_Water', 'Soil_Type_Gravel',
    'Soil_Type_Sand', 'Soil_Type_Silt'
]

MODEL_B_FEATURES = [
    'Temperature (°C)', 'Humidity (%)', 'Precipitation (mm)',
    'Soil Moisture (%)', 'Elevation (m)'
]

MODEL_B_CLASS_NAMES = ['Low', 'Moderate', 'High', 'Very High']

# ---------------------------------------------------------
# PROTOTYPE RISK MATRIX & THRESHOLDS (Configurable)
# ---------------------------------------------------------

# Instability Probability Bins for Model A
INSTABILITY_THRESHOLDS = {
    'LOW': (0.0, 0.35),
    'MODERATE': (0.35, 0.65),
    'HIGH': (0.65, 0.85),
    'VERY HIGH': (0.85, 1.0)
}

# Transparent 2D Risk Matrix
# Structure: RISK_MATRIX[Instability_Class][Weather_Risk_Class] -> Final_Risk_Level
RISK_MATRIX = {
    'LOW': {
        'Low': 'LOW',
        'Moderate': 'MODERATE',
        'High': 'MODERATE',
        'Very High': 'HIGH'
    },
    'MODERATE': {
        'Low': 'MODERATE',
        'Moderate': 'MODERATE',
        'High': 'HIGH',
        'Very High': 'HIGH'
    },
    'HIGH': {
        'Low': 'HIGH',
        'Moderate': 'HIGH',
        'High': 'HIGH',
        'Very High': 'CRITICAL'
    },
    'VERY HIGH': {
        'Low': 'HIGH',        # Ensures P >= 0.85 NEVER results in LOW or MODERATE risk
        'Moderate': 'HIGH',
        'High': 'CRITICAL',
        'Very High': 'CRITICAL'
    }
}

# ---------------------------------------------------------
# TRANSPARENT HAZARD INDEX SCORE WEIGHTS (0-100 Scale)
# ---------------------------------------------------------
# Hazard Index = (W_INSTABILITY * P_instability + W_WEATHER * Weather_Score) * 100
WEIGHT_INSTABILITY = 0.60
WEIGHT_WEATHER = 0.40

# Normalized Weather Class Scores (0.0 to 1.0)
WEATHER_CLASS_SCORES = {
    'Low': 0.15,
    'Moderate': 0.45,
    'High': 0.75,
    'Very High': 0.95
}

# ---------------------------------------------------------
# PROTOTYPE ADVISORY MESSAGES
# ---------------------------------------------------------
PROTOTYPE_DISCLAIMER = (
    "\n\n[NOTICE: This is an automated prototype advisory based on proxy models. "
    "It does not constitute operational geotechnical or emergency safety advice.]"
)

ADVISORIES = {
    'LOW': "Normal monitoring recommended." + PROTOTYPE_DISCLAIMER,
    'MODERATE': "Increase monitoring of slope and environmental conditions." + PROTOTYPE_DISCLAIMER,
    'HIGH': "Enhanced monitoring recommended. Inspect vulnerable slope zones." + PROTOTYPE_DISCLAIMER,
    'CRITICAL': "Immediate review of slope stability conditions recommended." + PROTOTYPE_DISCLAIMER
}
