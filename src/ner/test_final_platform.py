import os
import sys
import numpy as np
import pandas as pd
import torch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.ner.config import Config
from src.ner.dashboard_integration import (
    load_unet_model,
    predict_landslide_segmentation,
    get_terrain_susceptibility_summary,
    calculate_multimodal_risk
)
from src.ner.field_reporting import submit_field_report, get_all_field_reports
from src.ner.alert_engine import evaluate_prototype_alert
from src.ner.gis_layers import get_verified_landslide_events_df


def test_final_platform_integration():
    print("============================================================", flush=True)
    print("RUNNING FINAL MULTIMODAL LANDSLIDE PLATFORM INTEGRATION TESTS", flush=True)
    print("============================================================", flush=True)

    # 1. Verify U-Net Checkpoint
    unet_path = os.path.join(Config.BASE_DIR, "results", "ner", "segmentation", "best_unet.pth")
    assert os.path.exists(unet_path), f"U-Net checkpoint missing at {unet_path}"
    model, device = load_unet_model()
    assert model is not None, "Failed to load U-Net model"
    print("[TEST 1/10 PASSED] U-Net model checkpoint exists and loads cleanly.", flush=True)

    # 2. Verify LSTM Checkpoint
    lstm_path = os.path.join(Config.BASE_DIR, "models", "ner_lstm_best.pth")
    assert os.path.exists(lstm_path), f"LSTM checkpoint missing at {lstm_path}"
    print("[TEST 2/10 PASSED] LSTM model checkpoint exists.", flush=True)

    # 3. Verify Multimodal Fusion Outputs
    fusion_dir = os.path.join(Config.BASE_DIR, "results", "ner", "fusion")
    assert os.path.exists(os.path.join(fusion_dir, "multimodal_predictions.csv")), "multimodal_predictions.csv missing"
    assert os.path.exists(os.path.join(fusion_dir, "multimodal_fusion_report.md")), "multimodal_fusion_report.md missing"
    print("[TEST 3/10 PASSED] Multimodal fusion output CSV and report exist.", flush=True)

    # 4. Verify Terrain Outputs
    terrain_stats = get_terrain_susceptibility_summary()
    assert terrain_stats['s_terrain_index'] == 0.52, "Invalid terrain index"
    print("[TEST 4/10 PASSED] SRTM DEM terrain susceptibility summary operates.", flush=True)

    # 5. Verify Field Report Storage
    report = submit_field_report(25.5788, 91.8933, "Landslide", "HIGH", "Test verification report")
    assert report['report_id'].startswith("REP-"), "Field report submission failed"
    df_reports = get_all_field_reports()
    assert len(df_reports) > 0, "Field report database empty"
    print("[TEST 5/10 PASSED] Field report local CSV database read/write works.", flush=True)

    # 6. Verify Risk Calculation Bounds [0, 1]
    r_val, r_lvl, contribs = calculate_multimodal_risk(0.40, 0.52, 0.65)
    assert 0.0 <= r_val <= 1.0, f"Risk index {r_val} outside [0, 1]"
    assert r_lvl in ["LOW", "WATCH", "WARNING", "CRITICAL"], f"Invalid risk level {r_lvl}"
    print(f"[TEST 6/10 PASSED] Multimodal risk calculation returns valid score in [0,1]: {r_val:.4f} ({r_lvl})", flush=True)

    # 7. Verify Alert Engine Strategy
    alert = evaluate_prototype_alert(r_val, operating_mode="Balanced Mode")
    assert "selected_threshold" in alert, "Alert engine dictionary invalid"
    assert alert['selected_threshold'] == 0.65, "Invalid balanced threshold"
    print("[TEST 7/10 PASSED] Alert engine prototype decision support operates.", flush=True)

    # 8. Verify GIS Layer Data
    df_events = get_verified_landslide_events_df()
    assert len(df_events) >= 40, f"Verified event inventory count {len(df_events)} < 40"
    print(f"[TEST 8/10 PASSED] GIS layer verified event inventory loaded: {len(df_events)} events.", flush=True)

    # 9. Verify Jharia Application Assets
    model_a_path = os.path.join(Config.BASE_DIR, "models", "model_A_best.pkl")
    model_b_path = os.path.join(Config.BASE_DIR, "models", "model_B_best.pkl")
    assert os.path.exists(model_a_path), "Model A missing"
    assert os.path.exists(model_b_path), "Model B missing"
    print("[TEST 9/10 PASSED] Jharia mining Model A and Model B assets intact.", flush=True)

    # 10. Verify Streamlit Application Imports
    from app.app import load_jharia_fusion_engine
    j_engine = load_jharia_fusion_engine()
    assert j_engine is not None, "Jharia fusion engine failed to initialize"
    print("[TEST 10/10 PASSED] Streamlit application imports and loads successfully.", flush=True)

    print("\n============================================================", flush=True)
    print("ALL PLATFORM INTEGRATION TESTS PASSED CLEANLY!", flush=True)
    print("============================================================", flush=True)


if __name__ == "__main__":
    test_final_platform_integration()
