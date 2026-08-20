"""
Risk Fusion Engine for Prototype Rockfall Hazard Assessment.

IMPORTANT DISCLAIMER:
This module integrates predictions from Model A (Ground Instability) and Model B
(Meteorological Risk) using a configurable 2D risk matrix and heuristic scoring.
Outputs represent a "Rockfall Hazard Index" or "Rockfall Risk Level" and are NOT
scientifically validated operational hazard probabilities.
"""

import os
import joblib
import pandas as pd
import numpy as np

from src.config import (
    MODEL_A_PATH, MODEL_B_PATH,
    MODEL_A_FEATURES, MODEL_B_FEATURES,
    MODEL_B_CLASS_NAMES, INSTABILITY_THRESHOLDS,
    RISK_MATRIX, WEIGHT_INSTABILITY, WEIGHT_WEATHER,
    WEATHER_CLASS_SCORES, ADVISORIES
)
from src.explainability import get_sample_top_risk_factors

class RiskFusionEngine:
    def __init__(self, model_a_path=MODEL_A_PATH, model_b_path=MODEL_B_PATH):
        """Loads fitted pipelines for Model A and Model B."""
        if not os.path.exists(model_a_path):
            raise FileNotFoundError(f"Model A file not found at '{model_a_path}'. Train Model A first.")
        if not os.path.exists(model_b_path):
            raise FileNotFoundError(f"Model B file not found at '{model_b_path}'. Train Model B first.")
            
        self.model_A = joblib.load(model_a_path)
        self.model_B = joblib.load(model_b_path)
        
        self.features_A = MODEL_A_FEATURES
        self.features_B = MODEL_B_FEATURES
        self.class_names_B = MODEL_B_CLASS_NAMES

    def _classify_instability_prob(self, p):
        """Bins continuous instability probability into categorical tiers."""
        if p < INSTABILITY_THRESHOLDS['LOW'][1]:
            return 'LOW'
        elif p < INSTABILITY_THRESHOLDS['MODERATE'][1]:
            return 'MODERATE'
        elif p < INSTABILITY_THRESHOLDS['HIGH'][1]:
            return 'HIGH'
        else:
            return 'VERY HIGH'

    def predict(self, model_a_inputs, model_b_inputs):
        """
        Executes risk fusion for a given set of geotechnical and weather inputs.
        
        Parameters:
            model_a_inputs (dict or DataFrame): Geotechnical features for Model A
            model_b_inputs (dict or DataFrame): Meteorological features for Model B
            
        Returns:
            dict containing detailed inference, risk scores, matrix lookup, and advisory.
        """
        # Format Model A inputs
        if isinstance(model_a_inputs, dict):
            df_A = pd.DataFrame([model_a_inputs])
        else:
            df_A = model_a_inputs.copy()
            
        # Format Model B inputs
        if isinstance(model_b_inputs, dict):
            df_B = pd.DataFrame([model_b_inputs])
        else:
            df_B = model_b_inputs.copy()
            
        # Ensure all columns exist
        for col in self.features_A:
            if col not in df_A.columns:
                df_A[col] = 0.0
        df_A = df_A[self.features_A]
        
        for col in self.features_B:
            if col not in df_B.columns:
                df_B[col] = 0.0
        df_B = df_B[self.features_B]

        # --------------------------------------------------
        # 1. Model A Inference (Ground Instability)
        # --------------------------------------------------
        if hasattr(self.model_A, "predict_proba"):
            p_instability = float(self.model_A.predict_proba(df_A)[0, 1])
        else:
            p_instability = float(self.model_A.predict(df_A)[0])
            
        instability_class = self._classify_instability_prob(p_instability)

        # --------------------------------------------------
        # 2. Model B Inference (Meteorological Risk)
        # --------------------------------------------------
        b_pred_raw = self.model_B.predict(df_B)[0]
        
        # Handle string or integer predictions from Model B
        if isinstance(b_pred_raw, (int, np.integer)):
            weather_risk_class = self.class_names_B[b_pred_raw]
        else:
            weather_risk_class = str(b_pred_raw)
            
        # Class probabilities
        if hasattr(self.model_B, "predict_proba"):
            b_probs = self.model_B.predict_proba(df_B)[0]
            weather_probs_dict = {
                self.class_names_B[i]: float(b_probs[i]) for i in range(len(self.class_names_B))
            }
        else:
            weather_probs_dict = {cls: (1.0 if cls == weather_risk_class else 0.0) for cls in self.class_names_B}

        # --------------------------------------------------
        # 3. 2D Risk Matrix Evaluation
        # --------------------------------------------------
        final_risk_level = RISK_MATRIX.get(instability_class, {}).get(weather_risk_class, 'MODERATE')
        
        # Rule Enforcement: High instability (P >= 0.85) can never be LOW or MODERATE final risk
        if p_instability >= 0.85 and final_risk_level in ['LOW', 'MODERATE']:
            final_risk_level = 'HIGH'

        # --------------------------------------------------
        # 4. Transparent Hazard Index Calculation (0 - 100)
        # --------------------------------------------------
        w_score = WEATHER_CLASS_SCORES.get(weather_risk_class, 0.45)
        raw_score = (WEIGHT_INSTABILITY * p_instability + WEIGHT_WEATHER * w_score) * 100.0
        risk_score = float(np.clip(round(raw_score, 1), 0.0, 100.0))

        # --------------------------------------------------
        # 5. Advisory Message & Top Contributing Factors
        # --------------------------------------------------
        advisory = ADVISORIES.get(final_risk_level, ADVISORIES['MODERATE'])
        
        dict_A = df_A.iloc[0].to_dict()
        dict_B = df_B.iloc[0].to_dict()
        
        top_A_factors = get_sample_top_risk_factors(dict_A, self.model_A, self.features_A, top_n=2)
        top_B_factors = get_sample_top_risk_factors(dict_B, self.model_B, self.features_B, top_n=2)
        top_factors = top_A_factors + top_B_factors

        return {
            "instability_probability": round(p_instability, 4),
            "instability_class": instability_class,
            "weather_risk": weather_risk_class,
            "weather_probabilities": {k: round(v, 4) for k, v in weather_probs_dict.items()},
            "final_risk_level": final_risk_level,
            "risk_score": risk_score,
            "advisory": advisory,
            "top_risk_factors": top_factors
        }
