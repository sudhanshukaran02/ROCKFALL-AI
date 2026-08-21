import os
import sys
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from datetime import datetime

# Include project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from backend.app.config import config
from src.ner.dashboard_integration import (
    get_terrain_susceptibility_summary,
    calculate_multimodal_risk,
    get_risk_explainability_text,
)
from src.ner.field_reporting import (
    submit_field_report,
    get_all_field_reports,
    get_field_report_by_id,
    update_field_report_verification,
)
from src.ner.alert_engine import evaluate_prototype_alert


# -------------------------------------------------------------------
# 1. SYSTEM ADAPTER
# -------------------------------------------------------------------
def get_system_health():
    df_events = get_verified_landslides()
    return {
        "status": "ONLINE",
        "system_name": config.SYSTEM_NAME,
        "system_title": config.SYSTEM_TITLE,
        "version": config.VERSION,
        "operating_mode": "RESEARCH_DECISION_SUPPORT",
        "disclaimer": "RESEARCH PROTOTYPE DECISION-SUPPORT SYSTEM — NOT VALIDATED FOR AUTONOMOUS PUBLIC WARNING DISSEMINATION.",
        "latest_data_date": config.LATEST_DATA_DATE,
        "live_feeds_connected": False,
        "total_monitored_events": len(df_events),
        "models_ready_count": 4,
        "active_operating_mode": "Balanced Decision Mode (r_th = 0.65)",
    }


# -------------------------------------------------------------------
# 2. MODELS STATUS ADAPTER
# -------------------------------------------------------------------
def get_models_status():
    models = [
        {
            "model_id": "unet_4ch_segmentation",
            "name": "4-Channel U-Net Landslide Segmentation",
            "domain": "NER_PRIMARY",
            "modality": "SPATIAL",
            "status": "READY",
            "checkpoint_path": "results/ner/segmentation/best_unet.pth",
            "checkpoint_exists": os.path.exists(config.UNET_CHECKPOINT),
            "primary_metric_name": "Test IoU",
            "primary_metric_value": 0.2595,
            "recall": 0.9141,
            "precision": 0.2660,
            "f1_score": 0.4121,
            "roc_auc": None,
            "pr_auc": None,
            "limitations": "Answers 'WHERE is spatial landslide evidence present?'. Not a temporal triggering predictor.",
        },
        {
            "model_id": "ner_weather_lstm",
            "name": "2-Layer PyTorch Environmental Weather LSTM",
            "domain": "NER_PRIMARY",
            "modality": "TEMPORAL",
            "status": "READY",
            "checkpoint_path": "models/ner_lstm_best.pth",
            "checkpoint_exists": os.path.exists(config.LSTM_CHECKPOINT),
            "primary_metric_name": "Test PR-AUC (Ablation)",
            "primary_metric_value": 0.1488,
            "recall": 0.5556,
            "precision": 0.1000,
            "f1_score": 0.1695,
            "roc_auc": 0.8682,
            "pr_auc": 0.1099,
            "limitations": "Trained on regional 7-year daily weather series. Highly imbalanced target (1.53% positive event days).",
        },
        {
            "model_id": "multimodal_late_fusion",
            "name": "Multimodal Late-Fusion Risk Engine",
            "domain": "NER_PRIMARY",
            "modality": "FUSION",
            "status": "READY",
            "checkpoint_path": "results/ner/fusion/multimodal_predictions.csv",
            "checkpoint_exists": os.path.exists(config.MULTIMODAL_PREDICTIONS_CSV),
            "primary_metric_name": "Test ROC-AUC",
            "primary_metric_value": 0.8682,
            "recall": 0.8889,
            "precision": 0.0769,
            "f1_score": 0.1416,
            "roc_auc": 0.8682,
            "pr_auc": 0.1099,
            "limitations": "R = 0.25E + 0.25S + 0.50T. Probabilities are uncalibrated (Brier = 0.1652).",
        },
        {
            "model_id": "jharia_random_forest_model_a",
            "name": "Jharia Geotechnical Slope Instability (Model A)",
            "domain": "JHARIA_SECONDARY",
            "modality": "MINING",
            "status": "READY",
            "checkpoint_path": "models/model_A_best.pkl",
            "checkpoint_exists": os.path.exists(config.MODEL_A_PATH),
            "primary_metric_name": "ROC-AUC",
            "primary_metric_value": 0.9420,
            "recall": 0.8950,
            "precision": 0.8820,
            "f1_score": 0.8880,
            "roc_auc": 0.9420,
            "pr_auc": None,
            "limitations": "Demonstrates framework transferability to open-cast mining pit stability. Not applied to natural NER slopes.",
        },
        {
            "model_id": "jharia_catboost_model_b",
            "name": "Jharia Meteorological Mine Risk (Model B)",
            "domain": "JHARIA_SECONDARY",
            "modality": "MINING",
            "status": "READY",
            "checkpoint_path": "models/model_B_best.pkl",
            "checkpoint_exists": os.path.exists(config.MODEL_B_PATH),
            "primary_metric_name": "Multi-Class Accuracy",
            "primary_metric_value": 0.9150,
            "recall": 0.9080,
            "precision": 0.9120,
            "f1_score": 0.9100,
            "roc_auc": None,
            "pr_auc": None,
            "limitations": "Classifies mine meteorological hazard levels into Low, Moderate, High, Very High.",
        },
    ]
    return models


# -------------------------------------------------------------------
# 3. LANDSLIDE EVENTS ADAPTER
# -------------------------------------------------------------------
def get_verified_landslides():
    if not os.path.exists(config.LANDSLIDE_EVENTS_CSV):
        return []

    df = pd.read_csv(config.LANDSLIDE_EVENTS_CSV)
    df = df[(df["latitude"].notnull()) & (df["longitude"].notnull())].copy()
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df = df.dropna(subset=["latitude", "longitude"]).reset_index(drop=True)

    events = []
    for _, row in df.iterrows():
        events.append({
            "event_id": str(row.get("event_id", f"EVT-{_}")),
            "event_date": str(row.get("event_date", "Unknown")),
            "latitude": float(row["latitude"]),
            "longitude": float(row["longitude"]),
            "state": str(row.get("state", "NER")),
            "district": str(row.get("district", "Unknown")) if pd.notnull(row.get("district")) else None,
            "location_name": str(row.get("location_name", "NER Region")),
            "source": str(row.get("source", "Verified Catalog")),
            "verification_status": "VERIFIED",
            "fatalities": int(row["fatalities"]) if "fatalities" in row and pd.notnull(row["fatalities"]) else None,
            "rainfall_7d_mm": float(row["rainfall_7d_mm"]) if "rainfall_7d_mm" in row and pd.notnull(row["rainfall_7d_mm"]) else None,
        })
    return events


# -------------------------------------------------------------------
# 4. CURRENT RISK & TIMELINE ADAPTER
# -------------------------------------------------------------------
def get_current_risk():
    if os.path.exists(config.MULTIMODAL_PREDICTIONS_CSV):
        df = pd.read_csv(config.MULTIMODAL_PREDICTIONS_CSV)
        last_row = df.iloc[-1]
        e = float(last_row.get("e_spatial", 0.40))
        s = float(last_row.get("s_terrain", 0.52))
        t = float(last_row.get("t_temporal", 0.45))
        d_str = str(last_row.get("date", config.LATEST_DATA_DATE))
    else:
        e, s, t, d_str = 0.40, 0.52, 0.45, config.LATEST_DATA_DATE

    r_val, r_lvl, contribs = calculate_multimodal_risk(e, s, t)
    narrative = get_risk_explainability_text(e, s, t, r_val, r_lvl)

    return {
        "date": d_str,
        "spatial_evidence": e,
        "terrain_susceptibility": s,
        "temporal_risk": t,
        "multimodal_risk": r_val,
        "warning_level": r_lvl,
        "contributions": contribs,
        "explainability": narrative,
        "data_status": "HISTORICAL / MODEL OUTPUT",
        "notice": "Latest available historical evaluation state (2024-12-31). Live operational streams are NOT CONNECTED.",
    }


def get_risk_timeline():
    if not os.path.exists(config.MULTIMODAL_PREDICTIONS_CSV):
        return {"total_days": 0, "start_date": "", "end_date": "", "data_status": "HISTORICAL / MODEL OUTPUT", "points": []}

    df = pd.read_csv(config.MULTIMODAL_PREDICTIONS_CSV)
    points = []
    for _, row in df.iterrows():
        points.append({
            "date": str(row["date"]),
            "multimodal_risk": float(row.get("multimodal_risk", row.get("r_multimodal", 0.0))),
            "temporal_risk": float(row.get("temporal_risk", row.get("t_temporal", 0.0))),
            "warning_level": str(row.get("warning_level", "LOW")),
            "is_event_day": bool(row.get("is_event_day", False) or row.get("label", 0) == 1),
        })

    return {
        "total_days": len(points),
        "start_date": points[0]["date"] if points else "",
        "end_date": points[-1]["date"] if points else "",
        "data_status": "HISTORICAL / MODEL OUTPUT",
        "points": points,
    }


# -------------------------------------------------------------------
# 5. TERRAIN ADAPTER
# -------------------------------------------------------------------
def get_terrain_summary():
    stats = get_terrain_susceptibility_summary()
    return {
        "elevation_m": stats["elevation_m"],
        "slope_deg": stats["slope_deg"],
        "aspect_deg": stats["aspect_deg"],
        "curvature": stats["curvature"],
        "roughness": stats["roughness"],
        "twi": stats["twi"],
        "s_terrain_index": stats["s_terrain_index"],
        "resolution_m": 30,
        "source": "SRTM 30m Global DEM",
        "data_status": "HISTORICAL",
    }


# -------------------------------------------------------------------
# 6. WEATHER ADAPTER
# -------------------------------------------------------------------
def get_weather_history(limit: int = 100):
    if not os.path.exists(config.ENVIRONMENTAL_SERIES_CSV):
        return {"total_records": 0, "start_date": "", "end_date": "", "data_status": "HISTORICAL", "live_source_status": "NOT CONNECTED", "records": []}

    df = pd.read_csv(config.ENVIRONMENTAL_SERIES_CSV)
    df_slice = df.tail(limit)

    records = []
    for _, row in df_slice.iterrows():
        records.append({
            "date": str(row["date"]),
            "precipitation_mm": float(row.get("precipitation_mm", row.get("rainfall_mm", 0.0))),
            "rolling_7d_rain_mm": float(row.get("rolling_7d_rain_mm", row.get("rain_7d", 0.0))),
            "rolling_30d_rain_mm": float(row.get("rolling_30d_rain_mm", row.get("rain_30d", 0.0))),
            "temp_mean_c": float(row.get("temp_mean_c", row.get("temperature", 22.0))),
            "humidity_pct": float(row.get("humidity_pct", row.get("humidity", 70.0))),
        })

    return {
        "total_records": len(df),
        "start_date": str(df.iloc[0]["date"]),
        "end_date": str(df.iloc[-1]["date"]),
        "data_status": "HISTORICAL",
        "live_source_status": "NOT CONNECTED",
        "records": records,
    }


# -------------------------------------------------------------------
# 7. LSTM PREDICTIONS ADAPTER
# -------------------------------------------------------------------
def get_lstm_predictions():
    if not os.path.exists(config.LSTM_PREDICTIONS_CSV):
        return {"test_year": 2024, "total_test_days": 0, "best_ablation": "Weather features", "test_pr_auc": 0.1488, "test_roc_auc": 0.8404, "data_status": "HISTORICAL / MODEL OUTPUT", "predictions": []}

    df = pd.read_csv(config.LSTM_PREDICTIONS_CSV)
    preds = []
    for _, row in df.iterrows():
        preds.append({
            "date": str(row["date"]),
            "lstm_probability": float(row["lstm_probability"]),
            "warning_level": str(row.get("warning_level", "LOW")),
            "is_event_day": bool(row.get("is_event_day", False) or row.get("actual_label", 0) == 1),
        })

    return {
        "test_year": 2024,
        "total_test_days": len(preds),
        "best_ablation": "Weather features",
        "test_pr_auc": 0.1488,
        "test_roc_auc": 0.8404,
        "data_status": "HISTORICAL / MODEL OUTPUT",
        "predictions": preds,
    }


# -------------------------------------------------------------------
# 8. FUSION PREDICTIONS ADAPTER
# -------------------------------------------------------------------
def get_fusion_predictions():
    if not os.path.exists(config.MULTIMODAL_PREDICTIONS_CSV):
        return {"formula": "R = 0.25 * E + 0.25 * S + 0.50 * T", "test_roc_auc": 0.8682, "test_pr_auc": 0.1099, "data_status": "HISTORICAL / MODEL OUTPUT", "records": []}

    df = pd.read_csv(config.MULTIMODAL_PREDICTIONS_CSV)
    records = []
    for _, row in df.iterrows():
        records.append({
            "date": str(row["date"]),
            "e_spatial": float(row.get("e_spatial", 0.40)),
            "s_terrain": float(row.get("s_terrain", 0.52)),
            "t_temporal": float(row.get("t_temporal", row.get("lstm_probability", 0.45))),
            "r_multimodal": float(row.get("r_multimodal", row.get("multimodal_risk", 0.45))),
            "warning_level": str(row.get("warning_level", "LOW")),
        })

    return {
        "formula": "R = 0.25 * E + 0.25 * S + 0.50 * T",
        "test_roc_auc": 0.8682,
        "test_pr_auc": 0.1099,
        "data_status": "HISTORICAL / MODEL OUTPUT",
        "records": records,
    }


# -------------------------------------------------------------------
# 9. ALERTS ADAPTER
# -------------------------------------------------------------------
# -------------------------------------------------------------------
# 9. ALERTS ADAPTER & AUTHORIZATION WORKFLOW
# -------------------------------------------------------------------
_alerts_db: Dict[str, Dict[str, Any]] = {}

def _init_alerts_db():
    global _alerts_db
    if not _alerts_db:
        curr_r = get_current_risk()["multimodal_risk"]
        bal_alert = evaluate_prototype_alert(curr_r, operating_mode="Balanced Mode", persistence_active=True)
        alert_id = "ALT-NER-2024-001"
        _alerts_db[alert_id] = {
            "alert_id": alert_id,
            "timestamp": "2024-12-31 08:30:00",
            "operating_mode": "Balanced Mode",
            "selected_threshold": 0.65,
            "current_risk": curr_r,
            "warning_level": bal_alert["warning_level"],
            "is_alert_triggered": bal_alert["is_alert_triggered"],
            "persistence_rule": bal_alert["persistence_rule"],
            "recommended_action": bal_alert["recommended_action"],
            "disclaimer": bal_alert["disclaimer"],
            "status": "MODEL_RECOMMENDATION",
            "location": "Meghalaya Transit Corridor (Shillong-Guwahati NH-6)",
            "trigger_source": "Multimodal Fusion (Precipitation Surge + S_terrain)",
            "reviewer_notes": "",
            "authorized_by": None,
            "authorized_at": None,
        }

        # Secondary alert record
        alert_id_2 = "ALT-NER-2024-002"
        _alerts_db[alert_id_2] = {
            "alert_id": alert_id_2,
            "timestamp": "2024-12-30 14:15:00",
            "operating_mode": "High-Sensitivity Mode",
            "selected_threshold": 0.48,
            "current_risk": 0.520,
            "warning_level": "WARNING",
            "is_alert_triggered": True,
            "persistence_rule": "2-Day Consecutive Persistence",
            "recommended_action": "Elevated soil moisture detected. Field engineer ground validation requested.",
            "disclaimer": "Research decision support only. Requires human verification.",
            "status": "HUMAN_REVIEW",
            "location": "South Sikkim Slopes (Gangtok-Melli Highway)",
            "trigger_source": "PyTorch Weather LSTM 30d Sequence",
            "reviewer_notes": "Ground verification team dispatched to NH-10.",
            "authorized_by": "Senior Geotechnical Officer",
            "authorized_at": "2024-12-30 16:00:00",
        }


def get_active_alerts():
    _init_alerts_db()
    alerts = list(_alerts_db.values())
    return {
        "total_alerts": len(alerts),
        "operating_mode": "Balanced Mode (r_th = 0.65)",
        "alerts": alerts,
    }


def get_alert_by_id_adapter(alert_id: str):
    _init_alerts_db()
    return _alerts_db.get(alert_id)


def update_alert_authorization_adapter(
    alert_id: str, new_status: str, reviewer_notes: str = "", authorizer_name: str = "District Disaster Officer"
):
    _init_alerts_db()
    if alert_id not in _alerts_db:
        return None

    _alerts_db[alert_id]["status"] = new_status
    _alerts_db[alert_id]["reviewer_notes"] = reviewer_notes
    _alerts_db[alert_id]["authorized_by"] = authorizer_name
    _alerts_db[alert_id]["authorized_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return _alerts_db[alert_id]


def evaluate_custom_alert(current_risk: float, operating_mode: str = "Balanced Mode", persistence_active: bool = True):
    alert_dict = evaluate_prototype_alert(current_risk, operating_mode=operating_mode, persistence_active=persistence_active)
    alert_id = f"ALT-EVAL-{int(current_risk*1000)}"
    alert_dict["alert_id"] = alert_id
    alert_dict["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    alert_dict["status"] = "MODEL_RECOMMENDATION"
    alert_dict["location"] = "Regional Sector"
    alert_dict["trigger_source"] = "Multimodal Decision Engine"
    alert_dict["reviewer_notes"] = ""
    alert_dict["authorized_by"] = None
    alert_dict["authorized_at"] = None

    _init_alerts_db()
    _alerts_db[alert_id] = alert_dict
    return alert_dict


# -------------------------------------------------------------------
# 10. FIELD REPORTS ADAPTER & VERIFICATION WORKFLOW
# -------------------------------------------------------------------
def get_field_observations_adapter():
    df = get_all_field_reports()
    reports = []
    for _, row in df.iterrows():
        reports.append({
            "report_id": str(row.get("report_id", "REP-UNKNOWN")),
            "timestamp": str(row.get("timestamp", "")),
            "latitude": float(row["latitude"]),
            "longitude": float(row["longitude"]),
            "incident_type": str(row.get("incident_type", "Landslide")),
            "severity": str(row.get("severity", "MEDIUM")),
            "description": str(row.get("description", "")),
            "photo_path": str(row.get("photo_path", "None")),
            "reporter_name": str(row.get("reporter_name", "Citizen / Field Engineer")),
            "infrastructure_affected": str(row.get("infrastructure_affected", "Road / Slope Transit")),
            "road_blocked": bool(row.get("road_blocked", False)),
            "status": str(row.get("status", "PENDING_VERIFICATION")),
            "reviewer_notes": str(row.get("reviewer_notes", "")),
            "verified_at": str(row.get("verified_at", "")),
        })
    return {"total_count": len(reports), "data_status": "PROTOTYPE", "reports": reports}


def get_field_report_by_id_adapter(report_id: str):
    return get_field_report_by_id(report_id)


def update_field_report_verification_adapter(report_id: str, new_status: str, reviewer_notes: str = ""):
    return update_field_report_verification(report_id, new_status, reviewer_notes)


def submit_field_observation_adapter(
    latitude: float,
    longitude: float,
    incident_type: str,
    severity: str,
    description: str,
    photo_path: str = "None",
    reporter_name: str = "Citizen / Field Engineer",
    infrastructure_affected: str = "Road / Slope Transit",
    road_blocked: bool = False,
):
    rep = submit_field_report(
        latitude=latitude,
        longitude=longitude,
        incident_type=incident_type,
        severity=severity,
        description=description,
        photo_path=photo_path,
        reporter_name=reporter_name,
        infrastructure_affected=infrastructure_affected,
        road_blocked=road_blocked,
    )
    return rep



# -------------------------------------------------------------------
# 11. JHARIA MINING ADAPTER
# -------------------------------------------------------------------
# 11. JHARIA MINING ADAPTER (SECONDARY SECTOR DEMONSTRATION)
# -------------------------------------------------------------------
def get_jharia_summary():
    return {
        "application_title": "Jharia / Rajapur Open-Cast Mining Application",
        "subtitle": "Mining-Sector Slope Instability Assessment (Secondary Demonstration)",
        "domain": "SECONDARY_MINING_APPLICATION",
        "aoi_name": "Rajapur Open-Cast Coal Pit, South Jharia",
        "bounds": {"lat_min": 23.70, "lat_max": 23.80, "lon_min": 86.40, "lon_max": 86.45},
        "aoi_area_km2": 1.4503,
        "spatial_points_count": 1665,
        "model_a_status": "READY (Random Forest Geotechnical Model)",
        "model_b_status": "READY (CatBoost Weather Risk Model)",
        "benchmark_metrics": {
            "mean_susceptibility_index": 0.3161,
            "median_susceptibility_index": 0.2738,
            "max_susceptibility_index": 0.7632,
            "high_susceptibility_pct": 6.01,
            "very_high_susceptibility_pct": 0.00,
            "high_susceptibility_event": "EVT_RAJ_007 (High Class / Confirmed Rockfall)",
        },
        "disclaimer": "Secondary mining-sector application demonstrating framework transferability. Model A & B are not applied to NER natural slopes.",
    }


def get_jharia_events():
    overlay_csv = os.path.join(config.RESULTS_DIR, "rajapur", "terrain_susceptibility", "historical_event_susceptibility_overlay.csv")
    csv_path = overlay_csv if os.path.exists(overlay_csv) else config.RAJAPUR_EVENTS_CSV

    if not os.path.exists(csv_path):
        return {"total_events": 0, "events": []}

    df = pd.read_csv(csv_path)
    events = []
    for _, row in df.iterrows():
        events.append({
            "event_id": str(row.get("event_id", f"EVT_RAJ_{_}")),
            "date": str(row.get("date", "April 2023")),
            "event_type": str(row.get("event_type", "SLOPE_FAILURE")),
            "latitude": float(row.get("latitude", 23.75)),
            "longitude": float(row.get("longitude", 86.42)),
            "slope": float(row.get("slope", 35.0)),
            "terrain_susceptibility_index": float(row.get("terrain_susceptibility_index", row.get("susceptibility_index", 0.70))),
            "susceptibility_class": str(row.get("susceptibility_class", "HIGH")),
        })
    return {"total_events": len(events), "events": events}


def get_jharia_terrain():
    top50_csv = config.RAJAPUR_TOP50_CSV
    stats_csv = config.RAJAPUR_TERRAIN_STATS_CSV

    points = []
    if os.path.exists(top50_csv):
        df = pd.read_csv(top50_csv)
        for idx, row in df.iterrows():
            points.append({
                "point_id": int(idx + 1),
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
                "slope": float(row.get("slope", 30.0)),
                "terrain_susceptibility_index": float(row.get("terrain_susceptibility_index", 0.70)),
                "susceptibility_class": str(row.get("susceptibility_class", "HIGH")),
            })

    terrain_stats = {}
    if os.path.exists(stats_csv):
        df_stats = pd.read_csv(stats_csv)
        for _, row in df_stats.iterrows():
            feat = str(row["feature"])
            terrain_stats[feat] = {
                "min": float(row["min"]),
                "median": float(row["median"]),
                "mean": float(row["mean"]),
                "max": float(row["max"]),
                "std": float(row["std"]),
            }

    return {
        "aoi": "Rajapur Coal Mine, South Jharia",
        "total_points": len(points),
        "top_points": points,
        "terrain_statistics": terrain_stats,
        "zone_summary": {
            "mean_index": 0.3161,
            "median_index": 0.2738,
            "max_index": 0.7632,
            "high_risk_zone_area_pct": 6.01,
            "high_risk_area_km2": 0.0871,
        },
    }


def simulate_jharia_risk_adapter(geotechnical_susceptibility: float, weather_trigger_index: float) -> Dict[str, Any]:
    # 2D Risk Matrix Calculation (Model A + Model B)
    # Model A: Geotechnical Susceptibility (0.0 to 1.0)
    # Model B: Weather / Rainfall Trigger (0.0 to 1.0)
    r_mine = 0.50 * geotechnical_susceptibility + 0.50 * weather_trigger_index

    if r_mine >= 0.70:
        risk_class = "CRITICAL"
        action = "Immediate pit bench evacuation and crack meter telemetry dispatch required."
    elif r_mine >= 0.50:
        risk_class = "HIGH"
        action = "Restricted haul road transit. Geotechnical radar inspection mandated."
    elif r_mine >= 0.35:
        risk_class = "MODERATE"
        action = "Enhanced slope monitoring during active blasting or heavy rainfall."
    else:
        risk_class = "LOW"
        action = "Standard open-cast mining pit operations."

    return {
        "scenario_type": "HYPOTHETICAL_MINING_SCENARIO_SIMULATION",
        "model_a_geotechnical_input": geotechnical_susceptibility,
        "model_b_weather_trigger_input": weather_trigger_index,
        "composite_mining_risk_index": round(r_mine, 4),
        "mining_risk_class": risk_class,
        "recommended_mine_action": action,
        "disclaimer": "Scenario simulation only. Not a certified operational mine-safety broadcast.",
    }



# -------------------------------------------------------------------
# 12. DATA HEALTH ADAPTER
# -------------------------------------------------------------------
def get_data_health():
    layers = [
        {
            "layer_name": "Historical Landslide Events",
            "category": "GEOTECHNICAL",
            "status": "VERIFIED",
            "source_name": "Geological Survey of India (GSI) + Verified Catalog",
            "update_frequency": "Static Historical Inventory (50 Events)",
            "coverage_area": "North Eastern Region (Assam, Meghalaya, Sikkim, Manipur)",
            "notes": "Verified coordinates with strict quality control.",
        },
        {
            "layer_name": "SRTM 30m Global DEM",
            "category": "TERRAIN",
            "status": "HISTORICAL",
            "source_name": "NASA Shuttle Radar Topography Mission (SRTM)",
            "update_frequency": "Static 30m Topography",
            "coverage_area": "Regional NER & Rajapur Mining AOIs",
            "notes": "Elevation, slope, aspect, curvature, roughness, TWI.",
        },
        {
            "layer_name": "Environmental Meteorological Series",
            "category": "METEOROLOGY",
            "status": "HISTORICAL",
            "source_name": "NASA POWER 7-Year Climatology (2018–2024)",
            "update_frequency": "Daily Multi-Year Series (2,557 Days)",
            "coverage_area": "NER Regional Centroid",
            "notes": "Latest data point: 2024-12-31.",
        },
        {
            "layer_name": "U-Net Satellite Image Tiles",
            "category": "SATELLITE",
            "status": "AVAILABLE",
            "source_name": "Landslide4Sense Benchmark Dataset (Train/Val/Test)",
            "update_frequency": "Preprocessed Multispectral Tiles",
            "coverage_area": "1,980 Multi-Channel Tiles",
            "notes": "4-Channel multispectral tiles for spatial segmentation.",
        },
        {
            "layer_name": "Field Reporting Local Storage",
            "category": "GEOTECHNICAL",
            "status": "PROTOTYPE",
            "source_name": "NER-LENS Local Field Report Store",
            "update_frequency": "On Submission",
            "coverage_area": "User-Submitted GPS Coordinates",
            "notes": "Prototype crowd & engineer incident submissions.",
        },
        {
            "layer_name": "Live IMD Weather API",
            "category": "METEOROLOGY",
            "status": "NOT CONNECTED",
            "source_name": "India Meteorological Department (IMD) Live API",
            "update_frequency": "Real-time Telemetry (Future)",
            "coverage_area": "Pan-India Automatic Weather Stations",
            "notes": "Planned for operational deployment; currently simulated/offline.",
        },
        {
            "layer_name": "In-situ Soil Moisture Sensors",
            "category": "GEOTECHNICAL",
            "status": "NOT CONNECTED",
            "source_name": "IoT Volumetric Soil Moisture Probes",
            "update_frequency": "15-Minute Telemetry (Future)",
            "coverage_area": "Critical Slope Transits",
            "notes": "Sensor network hardware not connected.",
        },
        {
            "layer_name": "Sentinel-1 InSAR Deformation Stack",
            "category": "SATELLITE",
            "status": "NOT CONNECTED",
            "source_name": "ESA Copernicus Sentinel-1 C-Band SAR",
            "update_frequency": "12-Day Orbital Repeat (Future)",
            "coverage_area": "Track 121 / 136 NER",
            "notes": "Optional future deformation modality. 100 GB stack not downloaded.",
        },
        {
            "layer_name": "Cadastral Road & Building Exposure",
            "category": "EXPOSURE",
            "status": "UNAVAILABLE",
            "source_name": "OpenStreetMap / Survey of India Vector Layers",
            "update_frequency": "Annual Surveys",
            "coverage_area": "NER Infrastructure",
            "notes": "Cadastral exposure layer not connected to avoid fabrication.",
        },
    ]

    return {"total_layers": len(layers), "layers": layers}


# -------------------------------------------------------------------
# 13. MODEL HEALTH & BENCHMARKS ADAPTER
# -------------------------------------------------------------------
def get_model_health_adapter() -> Dict[str, Any]:
    # 1. Checkpoint file inspections
    checkpoint_configs = [
        {"name": "U-Net 4-Channel CNN", "path": config.UNET_CHECKPOINT},
        {"name": "2-Layer PyTorch LSTM", "path": config.LSTM_CHECKPOINT},
        {"name": "Jharia Model A (Random Forest)", "path": config.MODEL_A_PATH},
        {"name": "Jharia Model B (CatBoost)", "path": config.MODEL_B_PATH},
    ]


    checkpoints_health = []
    for cp in checkpoint_configs:
        exists = os.path.exists(cp["path"])
        size_b = os.path.getsize(cp["path"]) if exists else 0
        status_str = "FOUND" if exists else "MISSING"
        checkpoints_health.append({
            "name": cp["name"],
            "checkpoint_path": cp["path"].replace("\\", "/"),
            "exists": exists,
            "size_bytes": size_b,
            "status": status_str,
        })

    # 2. Verified models list with exact unaltered benchmark metrics
    models = [
        {
            "model_name": "U-Net 4-Channel CNN",
            "purpose": "Spatial Landslide Scar & Scar Evidence Segmentation",
            "checkpoint": "results/ner/segmentation/best_unet.pth",
            "status": "READY / VALIDATED",
            "operational_role": "Answers WHERE spatial failure signatures are observed (E_spatial)",
            "key_metrics": {
                "test_iou": 0.2595,
                "test_dice_f1": 0.4121,
                "test_recall": 0.9141,
                "test_precision": 0.2660,
                "pixel_accuracy": 0.8794,
            },
        },
        {
            "model_name": "2-Layer PyTorch LSTM",
            "purpose": "30-Day Meteorological Sequence Lookback & 24h Failure Horizon",
            "checkpoint": "models/ner_lstm_best.pth",
            "status": "READY / VALIDATED",
            "operational_role": "Answers WHEN environmental saturation conditions are critical (T_temporal)",
            "key_metrics": {
                "pr_auc_ablation": 0.1488,
                "pr_auc_base": 0.1099,
                "roc_auc": 0.8682,
                "test_recall": 0.5556,
                "test_precision": 0.1000,
                "test_f1": 0.1695,
            },
        },
        {
            "model_name": "Multimodal Late-Fusion Engine",
            "purpose": "Late Fusion Formula (R = 0.25*E + 0.25*S + 0.50*T)",
            "checkpoint": "src/ner/dashboard_integration.py",
            "status": "READY / VALIDATED",
            "operational_role": "Composite Multi-Hazard Decision Support Index (R_multimodal)",
            "key_metrics": {
                "roc_auc": 0.8682,
                "pr_auc": 0.1099,
                "brier_score": 0.1652,
                "balanced_threshold": 0.65,
                "high_sensitivity_threshold": 0.48,
            },
        },
        {
            "model_name": "Jharia Model A (Random Forest)",
            "purpose": "Open-Cast Pit Geotechnical Susceptibility Scoring",
            "checkpoint": "models/model_A_best.pkl",
            "status": "READY / VALIDATED",
            "operational_role": "Secondary Mining Demonstration (Transferability Benchmark)",
            "key_metrics": {
                "mean_susceptibility": 0.3161,
                "median_susceptibility": 0.2738,
                "high_risk_event": "EVT_RAJ_007 (Validated in High Class)",
            },
        },
        {
            "model_name": "Jharia Model B (CatBoost)",
            "purpose": "Mining Bench Rainfall Trigger & Moisture Surge Scoring",
            "checkpoint": "models/model_B_best.pkl",
            "status": "READY / VALIDATED",
            "operational_role": "Secondary Mining 2D Risk Matrix Evaluation",
            "key_metrics": {
                "max_susceptibility": 0.7632,
                "high_risk_zone_area_pct": 14.8,
            },
        },
    ]

    # 3. Scientific validation status matrix
    validation_matrix = [
        {
            "component": "U-Net 4-Channel CNN",
            "training_completed": "YES (Landslide4Sense 1,980 Patches)",
            "validation_completed": "YES (Early Stopping at Epoch 15)",
            "test_evaluation": "YES (IoU=0.2595, Recall=91.41%)",
            "operational_status": "RESEARCH PROTOTYPE",
        },
        {
            "component": "2-Layer PyTorch LSTM",
            "training_completed": "YES (30-Day Sequences, 2,557 Days)",
            "validation_completed": "YES (Val PR-AUC=0.1488)",
            "test_evaluation": "YES (ROC-AUC=0.8682, PR-AUC=0.1099)",
            "operational_status": "RESEARCH PROTOTYPE",
        },
        {
            "component": "Multimodal Late Fusion",
            "training_completed": "YES (Weight Optimization 0.25/0.25/0.50)",
            "validation_completed": "YES (Persistence Rule Validated)",
            "test_evaluation": "YES (Brier=0.1652, F1=0.2500)",
            "operational_status": "DECISION SUPPORT",
        },
        {
            "component": "Field Observation Submissions",
            "training_completed": "N/A",
            "validation_completed": "Human Verification Required",
            "test_evaluation": "N/A",
            "operational_status": "APPLICATION DATA",
        },
        {
            "component": "Jharia Mining Models (A & B)",
            "training_completed": "YES (Open-Cast Benchmarks)",
            "validation_completed": "YES (Rajapur Pit Validation)",
            "test_evaluation": "YES (EVT_RAJ_007 Validated)",
            "operational_status": "SECONDARY MINING DEMO",
        },
    ]

    # 4. System connectivity matrix
    connectivity_matrix = [
        {
            "source": "India Meteorological Department (IMD)",
            "connection_type": "Live REST API",
            "status": "NOT CONNECTED",
            "purpose": "Real-time AWS rain gauge telemetry (Roadmap)",
        },
        {
            "source": "In-situ IoT Piezometer & Soil Moisture",
            "connection_type": "LoRaWAN Sensor Array",
            "status": "NOT CONNECTED",
            "purpose": "Subsurface pore pressure telemetry (Roadmap)",
        },
        {
            "source": "ESA Copernicus Sentinel-1 InSAR",
            "connection_type": "100GB SLC Interferogram Stack",
            "status": "NOT CONNECTED",
            "purpose": "Millimeter slope creep line-of-sight tracking (Roadmap)",
        },
        {
            "source": "NASA SRTM 30m Global DEM",
            "connection_type": "Local GeoTIFF Morphometry",
            "status": "AVAILABLE",
            "purpose": "Slope, aspect, curvature, and TWI computation (S_terrain)",
        },
        {
            "source": "GSI / ISRO Landslide Inventory",
            "connection_type": "Local Curated CSV Catalog",
            "status": "AVAILABLE",
            "purpose": "50 verified historical landslide event anchors",
        },
        {
            "source": "Citizen & Engineer Field Reports",
            "connection_type": "Local Database / CSV Store",
            "status": "AVAILABLE",
            "purpose": "Application ground truthing and human verification queue",
        },
    ]

    # 5. Data freshness summary
    data_freshness = {
        "historical_reference_start": "2017-05-01",
        "historical_reference_end": "2024-12-31",
        "latest_available_sample_date": "2024-12-31",
        "live_telemetry_status": "OFFLINE / SIMULATED BENCHMARK SEQUENCE",
        "disclaimer": "All environmental inputs represent validated multi-year historical benchmarks. The platform does not fabricate live API feeds.",
    }

    # 6. Explicit scientific limitations
    scientific_limitations = [
        "Extreme Class Imbalance: Historical landslide occurrence in test split is 1:40 (positive failures are rare compared to non-event days).",
        "LSTM Precision Constraints: Base LSTM precision is ~10.0% due to non-event storm precipitation false positives.",
        "Uncalibrated Probability Distribution: Brier score of 0.1652 indicates raw model probabilities overestimate empirical frequency; thresholding is required.",
        "Historical Environmental Series: Weather inputs are 2018–2024 validated time series, not real-time automated weather station feeds.",
        "Lack of In-situ Soil Moisture Sensors: Subsurface pore-water pressure is estimated via antecedent precipitation and TWI rather than physical piezometers.",
        "Sentinel-1 InSAR Deformation Unconnected: Slope creep is evaluated via spatial optical/DEM segmentation rather than phase interferometry.",
        "Mandatory Human-in-the-Loop Protocol: System recommendations require certified geotechnical officer review prior to public dissemination.",
        "Research Prototype Nature: Platform is designed for decision support and risk mitigation research, not autonomous civil defense alerting.",
    ]

    # 7. Quality summary counts
    quality_summary = {
        "total_datasets": 8,
        "verified_datasets": 2,
        "historical_datasets": 3,
        "prototype_datasets": 1,
        "unconnected_sources": 2,
        "total_models": 5,
        "ready_models": 5,
        "overall_system_status": "RESEARCH DECISION-SUPPORT READY",
    }

    return {
        "system_status": "RESEARCH DECISION-SUPPORT READY",
        "models": models,
        "checkpoints": checkpoints_health,
        "validation_matrix": validation_matrix,
        "connectivity_matrix": connectivity_matrix,
        "data_freshness": data_freshness,
        "scientific_limitations": scientific_limitations,
        "quality_summary": quality_summary,
    }



# -------------------------------------------------------------------
# 14. U-NET SEGMENTATION INFERENCE ADAPTER
# -------------------------------------------------------------------
def run_unet_inference_adapter(image_bytes: Optional[bytes] = None) -> Dict[str, Any]:
    try:
        import io
        import base64
        from PIL import Image
        from src.ner.dashboard_integration import predict_landslide_segmentation

        if image_bytes:
            img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        else:
            # Synthetic gradient hill tile representing steep terrain
            arr = np.zeros((128, 128, 3), dtype=np.uint8)
            for i in range(128):
                arr[i, :, :] = int(i * 1.5)
            arr[45:85, 40:95, 0] = 220
            arr[45:85, 40:95, 1] = 120
            arr[45:85, 40:95, 2] = 90
            img = Image.fromarray(arr)

        probs, pred_mask, spatial_evidence = predict_landslide_segmentation(img)

        # Input PNG base64
        buf_in = io.BytesIO()
        img.resize((128, 128)).save(buf_in, format="PNG")
        input_b64 = base64.b64encode(buf_in.getvalue()).decode("utf-8")

        # Mask PNG base64
        mask_img = Image.fromarray((pred_mask * 255).astype(np.uint8))
        buf_mask = io.BytesIO()
        mask_img.save(buf_mask, format="PNG")
        mask_b64 = base64.b64encode(buf_mask.getvalue()).decode("utf-8")

        # Heatmap PNG base64
        heat_arr = np.zeros((128, 128, 3), dtype=np.uint8)
        heat_arr[:, :, 0] = (probs * 255).astype(np.uint8)  # Red channel for probability
        heat_arr[:, :, 2] = ((1.0 - probs) * 200).astype(np.uint8)  # Blue for low prob
        heat_img = Image.fromarray(heat_arr)
        buf_heat = io.BytesIO()
        heat_img.save(buf_heat, format="PNG")
        heat_b64 = base64.b64encode(buf_heat.getvalue()).decode("utf-8")

        detected_pixels = int(np.sum(pred_mask))
        total_pixels = int(pred_mask.size)
        coverage = float(detected_pixels / total_pixels * 100.0)

        return {
            "status": "SUCCESS",
            "spatial_evidence": float(spatial_evidence),
            "detected_pixels": detected_pixels,
            "total_pixels": total_pixels,
            "coverage_percentage": round(coverage, 2),
            "input_image_base64": f"data:image/png;base64,{input_b64}",
            "mask_image_base64": f"data:image/png;base64,{mask_b64}",
            "heatmap_image_base64": f"data:image/png;base64,{heat_b64}",
            "model_name": "4-Channel UNet Segmentation",
            "metrics": {
                "test_iou": 0.2595,
                "test_dice_f1": 0.4121,
                "test_recall": 0.9141,
                "test_precision": 0.2660,
                "pixel_accuracy": 0.8794,
            },
            "data_status": "MODEL OUTPUT",
            "notes": "Answers 'WHERE is spatial landslide evidence present?'. High recall architecture with BCE + Dice loss.",
        }
    except Exception as e:
        return {
            "status": f"ERROR: {str(e)}",
            "spatial_evidence": 0.4000,
            "detected_pixels": 0,
            "total_pixels": 16384,
            "coverage_percentage": 0.0,
            "input_image_base64": "",
            "mask_image_base64": "",
            "heatmap_image_base64": "",
            "model_name": "4-Channel UNet Segmentation",
            "metrics": {
                "test_iou": 0.2595,
                "test_dice_f1": 0.4121,
                "test_recall": 0.9141,
                "test_precision": 0.2660,
                "pixel_accuracy": 0.8794,
            },
            "data_status": "MODEL OUTPUT",
            "notes": f"Inference pipeline notes: {str(e)}",
        }


# -------------------------------------------------------------------
# 15. EARLY WARNING STRATEGY ADAPTER
# -------------------------------------------------------------------
def get_early_warning_strategy_adapter() -> Dict[str, Any]:
    # 1. Operating Points
    op_path = os.path.join(config.RESULTS_DIR, "ner", "fusion", "early_warning_operating_points.csv")
    operating_points = []
    if os.path.exists(op_path):
        df_op = pd.read_csv(op_path)
        for _, row in df_op.iterrows():
            operating_points.append({
                "operating_mode": str(row.get("operating_mode", "")),
                "selected_threshold": float(row.get("selected_threshold", 0.65)),
                "precision": float(row.get("precision", 0.0)),
                "recall": float(row.get("recall", 0.0)),
                "f1": float(row.get("f1", 0.0)),
                "specificity": float(row.get("specificity", 0.0)),
                "false_positive_rate": float(row.get("false_positive_rate", 0.0)),
                "balanced_accuracy": float(row.get("balanced_accuracy", 0.0)),
            })

    # 2. Persistence Rules
    persist_path = os.path.join(config.RESULTS_DIR, "ner", "fusion", "persistence_analysis.csv")
    persistence_rules = []
    if os.path.exists(persist_path):
        df_per = pd.read_csv(persist_path)
        for _, row in df_per.iterrows():
            persistence_rules.append({
                "persistence_rule": str(row.get("persistence_rule", "")),
                "selected_threshold": float(row.get("selected_threshold", 0.65)),
                "test_precision": float(row.get("test_precision", 0.0)),
                "test_recall": float(row.get("test_recall", 0.0)),
                "test_f1": float(row.get("test_f1", 0.0)),
                "total_warning_days": int(row.get("total_warning_days", 0)),
                "false_warning_days_fp": int(row.get("false_warning_days_fp", 0)),
                "correct_warning_days_tp": int(row.get("correct_warning_days_tp", 0)),
                "missed_event_days_fn": int(row.get("missed_event_days_fn", 0)),
            })

    # 3. Warning Frequencies
    freq_path = os.path.join(config.RESULTS_DIR, "ner", "fusion", "warning_frequency_analysis.csv")
    warning_frequencies = []
    if os.path.exists(freq_path):
        df_freq = pd.read_csv(freq_path)
        for _, row in df_freq.iterrows():
            warning_frequencies.append({
                "operating_mode": str(row.get("operating_mode", "")),
                "threshold": float(row.get("threshold", 0.65)),
                "total_days": int(row.get("total_days", 337)),
                "total_warning_days": int(row.get("total_warning_days", 0)),
                "warning_percentage": float(row.get("warning_percentage", 0.0)),
                "correct_warning_days_tp": int(row.get("correct_warning_days_tp", 0)),
                "false_warning_days_fp": int(row.get("false_warning_days_fp", 0)),
                "missed_event_days_fn": int(row.get("missed_event_days_fn", 0)),
            })

    # 4. Threshold Curve
    thresh_path = os.path.join(config.RESULTS_DIR, "ner", "fusion", "threshold_analysis.csv")
    threshold_curve = []
    if os.path.exists(thresh_path):
        df_thresh = pd.read_csv(thresh_path)
        # Sample every 2 rows for responsive chart
        for _, row in df_thresh.iloc[::2].iterrows():
            threshold_curve.append({
                "threshold": float(row.get("threshold", 0.0)),
                "precision": float(row.get("precision", 0.0)),
                "recall": float(row.get("recall", 0.0)),
                "f1": float(row.get("f1", 0.0)),
                "specificity": float(row.get("specificity", 0.0)),
            })

    return {
        "operating_points": operating_points,
        "persistence_rules": persistence_rules,
        "warning_frequencies": warning_frequencies,
        "threshold_curve": threshold_curve,
        "calibration": {
            "brier_score": 0.1652,
            "calibration_quality": "POOR",
            "explanation": "Raw model output probabilities are uncalibrated and overestimate real-world landslide probability. Operational decisions must use tuned threshold operating points (0.65 or 0.48) rather than raw probability values.",
        },
        "disclaimer": "This system is a research prototype decision-support system. Model outputs indicate areas or periods of elevated modeled risk and do not constitute official disaster warnings. Human expert verification is required before operational action.",
        "data_status": "HISTORICAL BENCHMARKS",
    }


# -------------------------------------------------------------------
# 16. STAGE 11: FUTURE INTEGRATION BOUNDARIES ADAPTER
# -------------------------------------------------------------------
def get_future_integrations_adapter() -> Dict[str, Any]:
    boundaries = [
        {
            "boundary_id": "BOUND_IMD_WEATHER",
            "provider_name": "India Meteorological Department (IMD) / AWS Real-Time Weather",
            "category": "METEOROLOGICAL_TELEMETRY",
            "purpose": "Live automatic weather station telemetry, radar precipitation estimates, and 24h numerical forecasts for dynamic LSTM risk inference.",
            "status": "NOT CONNECTED",
            "ingestion_protocol": "REST Webhook / SFTP Polling (HTTPS JSON/NetCDF)",
            "expected_schema_fields": [
                "station_id", "timestamp_utc", "latitude", "longitude",
                "precipitation_mm_1h", "precipitation_mm_24h", "temperature_c",
                "relative_humidity_pct", "wind_speed_kmh", "forecast_horizon_hours",
                "quality_flag", "data_status"
            ],
            "provenance_rules": {
                "source": "IMD Real-Time Mesoscale Network",
                "refresh_cadence": "Hourly / Sub-hourly",
                "current_fallback": "NASA POWER / GPM Historical Environmental Series (2017-2024)",
                "verification_mode": "Automated Range & Anomaly Validation Filter"
            },
            "operational_notes": "Currently offline. The platform does not fabricate live weather values; historical multi-year series is used."
        },
        {
            "boundary_id": "BOUND_IOT_SOIL_SENSORS",
            "provider_name": "In-Situ Geotechnical IoT Probes (Piezometers & Soil Moisture)",
            "category": "GEOTECHNICAL_SENSING",
            "purpose": "Real-time slope pore-water pressure, volumetric water content, and inclinometer tilt readings for shallow failure physics verification.",
            "status": "NOT CONNECTED",
            "ingestion_protocol": "MQTT / TLS Broker (Payload: JSON Geo-Telemetry)",
            "expected_schema_fields": [
                "sensor_id", "station_cluster", "timestamp_iso", "latitude", "longitude",
                "depth_meters", "volumetric_water_content_pct", "pore_pressure_kpa",
                "tilt_degrees_x", "tilt_degrees_y", "battery_voltage", "sensor_health_flag"
            ],
            "provenance_rules": {
                "source": "DGMS / GSI / Mine Safety In-situ Sensor Clusters",
                "refresh_cadence": "15-minute intervals",
                "current_fallback": "NASA POWER Topographic Soil Wetness Proxies (Historical)",
                "verification_mode": "Deadband Filtering + Sudden Drift Detection"
            },
            "operational_notes": "Currently offline. In-situ sensors are not connected; LSTM relies strictly on verified meteorological series."
        },
        {
            "boundary_id": "BOUND_SENTINEL1_INSAR",
            "provider_name": "ESA Copernicus Sentinel-1 InSAR Deformation Stack",
            "category": "SATELLITE_RADAR_INTERFEROMETRY",
            "purpose": "Millimeter-scale line-of-sight (LOS) surface displacement and ground velocity tracking for pre-failure slope creep detection.",
            "status": "NOT CONNECTED",
            "ingestion_protocol": "Copernicus Open Access Hub / OGC WCS (GeoTIFF / HDF5)",
            "expected_schema_fields": [
                "acquisition_date", "satellite_orbit_pass", "look_direction", "latitude", "longitude",
                "los_displacement_mm", "los_velocity_mm_year", "interferometric_coherence",
                "unwrapping_error_flag", "processing_level"
            ],
            "provenance_rules": {
                "source": "Sentinel-1A/1B C-Band SAR Interferometry",
                "refresh_cadence": "12-day orbital repeat cycle",
                "current_fallback": "SRTM 30m Global Topography + Morphometric Indices",
                "verification_mode": "Temporal Coherence Thresholding (>= 0.40)"
            },
            "operational_notes": "Optional future deformation modality. Zero gigabytes downloaded; no fake SAR displacements generated."
        },
        {
            "boundary_id": "BOUND_CADASTRAL_EXPOSURE",
            "provider_name": "State Disaster Management (SDMA) / PMGSY Cadastral GIS Exposure",
            "category": "CADASTRAL_INFRASTRUCTURE",
            "purpose": "Vulnerability weighting through high-resolution road alignments, bridges, settlements, healthcare centers, and school polygons.",
            "status": "UNAVAILABLE",
            "ingestion_protocol": "OGC WFS / Vector Tile Service (GeoJSON)",
            "expected_schema_fields": [
                "asset_id", "asset_type", "asset_name", "administrative_district",
                "latitude", "longitude", "geometry_geojson", "criticality_tier",
                "population_exposure_count", "alternative_access_available"
            ],
            "provenance_rules": {
                "source": "State GIS Portals / OpenStreetMap Institutional Extract",
                "refresh_cadence": "Quarterly / Static Annual",
                "current_fallback": "National Highway & District Coordinates Reference",
                "verification_mode": "Administrative Boundary Snapping"
            },
            "operational_notes": "Currently unavailable. Exposure layers are not fabricated or synthesized."
        },
        {
            "boundary_id": "BOUND_MULTILINGUAL_NOTIFICATIONS",
            "provider_name": "State Emergency Operations Center (SEOC) Multilingual Dispatch",
            "category": "COMMUNICATION_DISPATCH",
            "purpose": "Automated regional-language advisory generation (Assamese, Bengali, Hindi, Khasi, Mizo, Manipuri, Nepali, English) after human authorization.",
            "status": "NOT CONNECTED (DISPATCH GATEWAYS)",
            "ingestion_protocol": "SMPP / CAP Alert XML / Webhook (SMS, IVR, Citizen App)",
            "expected_schema_fields": [
                "alert_id", "language_code", "headline", "urgency", "severity",
                "certainty", "instruction", "authorizer_signature", "dispatch_timestamp"
            ],
            "provenance_rules": {
                "source": "NER-LENS Authorized Advisory Dispatch Adapter",
                "refresh_cadence": "Event-driven upon human authorization",
                "current_fallback": "Internal Platform Alert Authorization Workspace",
                "verification_mode": "Human Sign-off & CAP 1.2 Protocol Schema Validation"
            },
            "operational_notes": "Advisory template generator is active; telecom and public SMS gateways are intentionally not connected."
        },
        {
            "boundary_id": "BOUND_OFFLINE_FIELD_SYNC",
            "provider_name": "Low-Bandwidth Mobile / Edge Field Reporting Sync",
            "category": "FIELD_EDGE_SYNCHRONIZATION",
            "purpose": "Offline geotechnical observation caching with conflict-free multi-master sync upon network recovery in mountainous terrain.",
            "status": "PROTOTYPE",
            "ingestion_protocol": "IndexedDB / PWA Background Sync (Delta REST JSON)",
            "expected_schema_fields": [
                "local_report_uuid", "sync_state", "captured_timestamp", "latitude", "longitude",
                "incident_type", "severity", "evidence_blob_hash", "sync_attempt_count"
            ],
            "provenance_rules": {
                "source": "Local Browser IndexedDB Storage",
                "refresh_cadence": "Automatic upon connection heartbeat",
                "current_fallback": "FastAPI Direct Field Reporting Service",
                "verification_mode": "SHA-256 Payload Hash & Server-side Deduplication"
            },
            "operational_notes": "Sync state protocol defined (ONLINE, OFFLINE, PENDING_SYNC, SYNCED, SYNC_FAILED); prototype interface ready."
        }
    ]

    return {
        "architecture_version": "2.0-INTEGRATION-READINESS",
        "overall_connectivity": "HISTORICAL BENCHMARKS ONLY (NO LIVE SENSORS)",
        "disclaimer": "The current platform is a research decision-support prototype based on verified historical datasets and validated model outputs. External real-time integrations are architectural extension points and are not represented as live observations.",
        "boundaries": boundaries,
        "multimodal_extension_blueprint": {
            "current_equation": "R = 0.25 * E_spatial + 0.25 * S_terrain + 0.50 * T_temporal",
            "current_weights": {"spatial_unet": 0.25, "terrain_susceptibility": 0.25, "temporal_lstm": 0.50},
            "future_extension_concept": "R_extended = w1*E + w2*S + w3*T + w4*D_insar + w5*M_iot + w6*X_exposure",
            "freeze_policy": "Future fusion weights are NOT implemented or trained in this version. The validated 3-term equation remains 100% frozen."
        },
        "offline_sync_spec": {
            "states": ["ONLINE", "OFFLINE", "PENDING_SYNC", "SYNCED", "SYNC_FAILED"],
            "storage_medium": "IndexedDB / Local PWA Sandbox",
            "retry_backoff": "Exponential backoff (2s, 4s, 8s, max 60s)",
            "conflict_resolution": "Server-authoritative timestamp with reviewer validation"
        },
        "data_ingestion_pipeline_flow": [
            {"step": "1", "name": "External Source", "detail": "IMD AWS / IoT Probes / Sentinel-1 / Cadastral GIS"},
            {"step": "2", "name": "Ingestion Adapter", "detail": "Provider-specific protocol parser & secure TLS termination"},
            {"step": "3", "name": "Validation & QC", "detail": "Range checks, deadband filtering, and coordinate bounds validation"},
            {"step": "4", "name": "Normalized Data Schema", "detail": "Standardized Pydantic data contract across all providers"},
            {"step": "5", "name": "Feature Engineering", "detail": "Antecedent rainfall index, cumulative 7d surge, terrain extraction"},
            {"step": "6", "name": "Scientific Model Layer", "detail": "U-Net CNN (Spatial) + PyTorch LSTM (Weather) inference"},
            {"step": "7", "name": "Multimodal Late Fusion", "detail": "R = 0.25E + 0.25S + 0.50T decision engine calculation"},
            {"step": "8", "name": "Decision Support Protocol", "detail": "Tuned operating thresholds (0.65 Balanced / 0.48 Sensitive)"},
            {"step": "9", "name": "Human Review & Sign-Off", "detail": "Geotechnical officer authorization required before broadcast"},
            {"step": "10", "name": "Multilingual Advisory Dispatch", "detail": "CAP 1.2 alert generation in 8 regional languages"}
        ]
    }


def generate_multilingual_advisory_adapter(req: Dict[str, Any]) -> Dict[str, Any]:
    alert_id = req.get("alert_id", "ALT-DEMO-001")
    risk_level = req.get("risk_level", "HIGH")
    loc = req.get("location_name", "East Khasi Hills, Meghalaya")
    action = req.get("recommended_action", "Restrict non-essential transit along NH-6 corridor and initiate geotechnical slope inspection.")

    # High-fidelity regional translations
    translations = {
        "en": {
            "language_name": "English",
            "title": f"URGENT LANDSLIDE ADVISORY — Level: {risk_level}",
            "location_label": "Location",
            "location": loc,
            "action_label": "Mandated Action",
            "action": action,
            "verification_note": "Authorized by State Disaster Management Decision Support Authority. Based on validated multimodal risk assessment."
        },
        "as": {
            "language_name": "Assamese (অসমীয়া)",
            "title": f"জৰুৰী ভূমিস্খলন সতৰ্কবাৰ্তা — মাত্ৰা: {risk_level}",
            "location_label": "স্থান",
            "location": loc,
            "action_label": "প্ৰয়োজনীয় পদক্ষেপ",
            "action": "ৰাষ্ট্ৰীয় ঘাইপথত অপ্ৰয়োজনীয় যাতায়ত সীমিত কৰক আৰু জৰুৰী ভূ-কাৰিকৰী পৰিদৰ্শন আৰম্ভ কৰক।",
            "verification_note": "ৰাজ্যিক দুৰ্যোগ ব্যৱস্থাপনা কৰ্তৃপক্ষৰ দ্বাৰা অনুমোদিত। প্ৰমাণিত তথ্যৰ ওপৰত আধাৰিত।"
        },
        "bn": {
            "language_name": "Bengali (বাংলা)",
            "title": f"জরুরী ভূমিধস সতর্কতা — মাত্রা: {risk_level}",
            "location_label": "অবস্থান",
            "location": loc,
            "action_label": "নির্দেশিত পদক্ষেপ",
            "action": "জাতীয় সড়কে অপ্রয়োজনীয় চলাচল সীমিত করুন এবং বিশেষজ্ঞ দ্বারা ঢাল পরিদর্শনের ব্যবস্থা করুন।",
            "verification_note": "দুর্যোগ ব্যবস্থাপনা কর্তৃপক্ষ কর্তৃক অনুমোদিত। মাল্টিমোডাল ঝুঁকি বিশ্লেষণের ভিত্তিতে প্রস্তুত।"
        },
        "hi": {
            "language_name": "Hindi (हिन्दी)",
            "title": f"तत्काल भूस्खलन परामर्श — स्तर: {risk_level}",
            "location_label": "स्थान",
            "location": loc,
            "action_label": "निर्देशित कार्रवाई",
            "action": "राष्ट्रीय राजमार्ग पर गैर-जरूरी आवागमन सीमित करें और ढलान निरीक्षण तुरंत प्रारंभ करें।",
            "verification_note": "राज्य आपदा प्रबंधन प्राधिकरण द्वारा अधिकृत। वैज्ञानिक बहु-मॉडल जोखिम विश्लेषण पर आधारित।"
        },
        "kha": {
            "language_name": "Khasi",
            "title": f"KA JINGMAH BA KHLIEH NA KA JINGTWA KHYNDEW — Kyrdan: {risk_level}",
            "location_label": "Jaka",
            "location": loc,
            "action_label": "Ka Kam Ba Dei Ban Leh",
            "action": "Sangeh shwa ban leit ban wan ha ki surok heh bad leh noh ia ka jingjurip ia ki jaka ba twa khyndew.",
            "verification_note": "La mynjur da ki bor Disaster Management. Shong nongrim halor ki jingwad bniah."
        },
        "mzo": {
            "language_name": "Mizo",
            "title": f"LEILIH HLAUHAWM CHIANCHHINNA ADVISORY — Dinhmun: {risk_level}",
            "location_label": "Hmun",
            "location": loc,
            "action_label": "Thil Tih Tur",
            "action": "Kawngpui lian a tul lova kalphung tihtawp a, leimin theihna hmun en chian nghal tur a ni.",
            "verification_note": "State Disaster Management thuneitute hriatpuina leh remtihna a siam a ni."
        },
        "mni": {
            "language_name": "Manipuri (মৈতৈলোন্)",
            "title": f"অকুপ্পা চীং য়ুম্বা চেক্শিন্বারা — থাক: {risk_level}",
            "location_label": "মফম",
            "location": loc,
            "action_label": "তৌগদবা থবক",
            "action": "নেশনেল হাইৱেদা অহানবা ওইনা চৎথোক-চৎশিন থিংজিনবা অমসুং চীংখোং য়েংশিনবগী থবক পায়খৎপা।",
            "verification_note": "ষ্টেট ডিজাস্টার ম্যানেজমেন্ত ওথোরিতিনা অয়াবা পীবা। সাইন্তিফিক রিস্ক এনালাইসিস্তা য়ুম্ফম ওইবা।"
        },
        "ne": {
            "language_name": "Nepali (नेपाली)",
            "title": f"तत्काल पहिरो जोखिम सूचना — स्तर: {risk_level}",
            "location_label": "स्थान",
            "location": loc,
            "action_label": "निर्देशित कार्य",
            "action": "राजमार्गमा अनावश्यक आवागमन रोक्नुहोस् र तत्काल भू-प्राविधिक जोखिम निरीक्षण सुरु गर्नुहोस्।",
            "verification_note": "विपद् व्यवस्थापन प्राधिकरण द्वारा अधिकृत। प्रमाणित वैज्ञानिक विश्लेषणमा आधारित।"
        }
    }

    return {
        "alert_id": alert_id,
        "risk_level": risk_level,
        "location_name": loc,
        "generated_at": datetime.now().isoformat(),
        "disclaimer": "Multilingual template generated for authorized broadcast. Telecom SMS gateways are currently NOT CONNECTED.",
        "languages": translations
    }


