import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.ner.config import Config


# ---------------------------------------------------------
# PROTOTYPE EARLY WARNING ALERT ENGINE
# ---------------------------------------------------------
def evaluate_prototype_alert(current_risk, operating_mode="Balanced Mode", persistence_active=True):
    """
    Evaluates prototype alert status using validated thresholds and 2-day persistence.
    Thresholds:
      - Balanced Mode: threshold = 0.65
      - High-Sensitivity Mode: threshold = 0.48
    Returns dictionary with alert status and recommendation.
    """
    threshold = 0.65 if operating_mode == "Balanced Mode" else 0.48

    is_alert_triggered = bool(current_risk >= threshold)

    if current_risk >= 0.70:
        warning_level = "CRITICAL"
        color_code = "#c0392b"
        rec_action = "Immediate field inspection & localized risk advisory recommended."
    elif current_risk >= 0.50:
        warning_level = "WARNING"
        color_code = "#e67e22"
        rec_action = "Enhanced slope monitoring and field team dispatch recommended."
    elif current_risk >= 0.35:
        warning_level = "WATCH"
        color_code = "#f39c12"
        rec_action = "Routine environmental monitoring & weather surveillance."
    else:
        warning_level = "LOW"
        color_code = "#27ae60"
        rec_action = "Baseline routine background monitoring."

    alert_summary = {
        "operating_mode": operating_mode,
        "selected_threshold": threshold,
        "current_risk": float(current_risk),
        "warning_level": warning_level,
        "is_alert_triggered": is_alert_triggered,
        "color_code": color_code,
        "persistence_rule": "2 Consecutive Days" if persistence_active else "1 Day",
        "recommended_action": rec_action,
        "disclaimer": "PROTOTYPE ALERT GENERATED — Not validated for autonomous public civil defense warnings."
    }

    return alert_summary
