import pytest

def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "NER-LENS" in data["message"]


def test_system_health(client):
    response = client.get("/api/system/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ONLINE"
    assert data["system_name"] == "NER-LENS"
    assert data["live_feeds_connected"] is False
    assert data["total_monitored_events"] >= 40
    assert "RESEARCH PROTOTYPE" in data["disclaimer"]


def test_models_status(client):
    response = client.get("/api/models/status")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 4
    
    # Check U-Net
    unet = next((m for m in data if m["model_id"] == "unet_4ch_segmentation"), None)
    assert unet is not None
    assert unet["checkpoint_exists"] is True
    assert unet["primary_metric_value"] == 0.2595

    # Check LSTM
    lstm = next((m for m in data if m["model_id"] == "ner_weather_lstm"), None)
    assert lstm is not None
    assert lstm["checkpoint_exists"] is True
    assert lstm["primary_metric_value"] == 0.1488


def test_landslides_endpoint(client):
    response = client.get("/api/landslides")
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] >= 40
    assert len(data["events"]) >= 40
    assert data["data_status"] == "HISTORICAL / VERIFIED"
    
    # Check first event
    evt = data["events"][0]
    assert "latitude" in evt
    assert "longitude" in evt
    assert evt["verification_status"] == "VERIFIED"


def test_current_risk(client):
    response = client.get("/api/risk/current")
    assert response.status_code == 200
    data = response.json()
    assert 0.0 <= data["multimodal_risk"] <= 1.0
    assert data["warning_level"] in ["LOW", "WATCH", "MODERATE", "WARNING", "HIGH", "CRITICAL"]
    assert "spatial_contribution" in data["contributions"]
    assert "terrain_contribution" in data["contributions"]
    assert "temporal_contribution" in data["contributions"]


def test_risk_timeline(client):
    response = client.get("/api/risk/timeline")
    assert response.status_code == 200
    data = response.json()
    assert data["total_days"] > 0
    assert len(data["points"]) > 0


def test_terrain_summary(client):
    response = client.get("/api/terrain")
    assert response.status_code == 200
    data = response.json()
    assert data["s_terrain_index"] == 0.52
    assert "slope_deg" in data
    assert "elevation_m" in data
    assert "twi" in data


def test_weather_history(client):
    response = client.get("/api/weather/history?limit=50")
    assert response.status_code == 200
    data = response.json()
    assert len(data["records"]) == 50
    assert data["live_source_status"] == "NOT CONNECTED"


def test_lstm_predictions(client):
    response = client.get("/api/lstm/predictions")
    assert response.status_code == 200
    data = response.json()
    assert data["test_pr_auc"] == 0.1488
    assert len(data["predictions"]) > 0


def test_fusion_predictions(client):
    response = client.get("/api/fusion/predictions")
    assert response.status_code == 200
    data = response.json()
    assert data["test_roc_auc"] == 0.8682
    assert len(data["records"]) > 0


def test_alerts_endpoints(client):
    # GET alerts
    response = client.get("/api/alerts")
    assert response.status_code == 200
    data = response.json()
    assert len(data["alerts"]) > 0

    # POST alert evaluation
    eval_resp = client.post("/api/alerts/evaluate", json={"current_risk": 0.72, "operating_mode": "Balanced Mode"})
    assert eval_resp.status_code == 200
    eval_data = eval_resp.json()
    assert eval_data["is_alert_triggered"] is True
    assert eval_data["warning_level"] == "CRITICAL"


def test_field_observations_endpoints(client):
    # GET observations
    response = client.get("/api/field-observations")
    assert response.status_code == 200
    data = response.json()
    assert "reports" in data

    # POST new observation
    post_resp = client.post(
        "/api/field-observations",
        json={
            "latitude": 25.5788,
            "longitude": 91.8933,
            "incident_type": "Crack",
            "severity": "HIGH",
            "description": "Pytest verification observation report",
        }
    )
    assert post_resp.status_code == 200
    res = post_resp.json()
    assert res["report_id"].startswith("REP-")
    assert res["status"] in ["PENDING_VERIFICATION", "SUBMITTED_PROTOTYPE"]


def test_jharia_endpoints(client):
    # Summary
    summary_resp = client.get("/api/jharia/summary")
    assert summary_resp.status_code == 200
    summary = summary_resp.json()
    assert summary["domain"] == "SECONDARY_MINING_APPLICATION"
    assert summary["benchmark_metrics"]["mean_susceptibility_index"] == 0.3161

    # Events
    events_resp = client.get("/api/jharia/events")
    assert events_resp.status_code == 200
    events = events_resp.json()
    assert events["total_events"] >= 8

    # Terrain
    terrain_resp = client.get("/api/jharia/terrain")
    assert terrain_resp.status_code == 200
    terrain = terrain_resp.json()
    assert len(terrain["top_points"]) > 0
    assert terrain["zone_summary"]["mean_index"] == 0.3161

    # Simulate
    sim_resp = client.post("/api/jharia/simulate", json={"geotechnical_susceptibility": 0.75, "weather_trigger_index": 0.70})
    assert sim_resp.status_code == 200
    sim = sim_resp.json()
    assert sim["composite_mining_risk_index"] == 0.725
    assert sim["mining_risk_class"] == "CRITICAL"



def test_data_health(client):
    response = client.get("/api/data-health")
    assert response.status_code == 200
    data = response.json()
    assert data["total_layers"] >= 8

    # Check that live IMD and soil moisture are explicitly marked NOT CONNECTED
    imd = next((l for l in data["layers"] if "IMD" in l["layer_name"]), None)
    assert imd is not None
    assert imd["status"] == "NOT CONNECTED"


def test_model_health_endpoint(client):
    response = client.get("/api/model-health")
    assert response.status_code == 200
    data = response.json()
    assert data["system_status"] == "RESEARCH DECISION-SUPPORT READY"
    assert len(data["models"]) >= 5
    assert len(data["checkpoints"]) >= 4
    assert len(data["validation_matrix"]) >= 5
    assert len(data["connectivity_matrix"]) >= 6
    assert len(data["scientific_limitations"]) >= 8

    # Verify all 4 actual checkpoints are FOUND
    for cp in data["checkpoints"]:
        assert cp["exists"] is True
        assert cp["status"] == "FOUND"
        assert cp["size_bytes"] > 0



def test_unet_inference_endpoints(client):
    response = client.get("/api/unet/sample")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert "spatial_evidence" in data
    assert data["metrics"]["test_iou"] == 0.2595
    assert data["metrics"]["test_recall"] == 0.9141
    assert data["input_image_base64"].startswith("data:image/png;base64,")
    assert data["mask_image_base64"].startswith("data:image/png;base64,")
    assert data["heatmap_image_base64"].startswith("data:image/png;base64,")


def test_field_reports_and_verification_workflow(client):
    # 1. List field reports
    resp = client.get("/api/field-reports")
    assert resp.status_code == 200
    data = resp.json()
    assert "reports" in data

    # 2. Submit new report
    post_payload = {
        "latitude": 25.5788,
        "longitude": 91.8933,
        "incident_type": "SLOPE_FAILURE",
        "severity": "HIGH",
        "description": "Debris observed across road shoulder on Shillong bypass",
        "photo_path": "None",
        "reporter_name": "Field Officer K. Sharma",
        "infrastructure_affected": "NH-6 Bypass",
        "road_blocked": True,
    }
    create_resp = client.post("/api/field-reports", json=post_payload)
    assert create_resp.status_code == 200
    created = create_resp.json()
    report_id = created["report_id"]
    assert created["incident_type"] == "SLOPE_FAILURE"
    assert created["status"] == "PENDING_VERIFICATION"

    # 3. Retrieve detail
    detail_resp = client.get(f"/api/field-reports/{report_id}")
    assert detail_resp.status_code == 200
    assert detail_resp.json()["report_id"] == report_id

    # 4. Verify report
    verify_payload = {
        "new_status": "VERIFIED",
        "reviewer_notes": "Geotechnical team validated active slip plane."
    }
    patch_resp = client.patch(f"/api/field-reports/{report_id}/verification", json=verify_payload)
    assert patch_resp.status_code == 200
    updated = patch_resp.json()
    assert updated["status"] == "VERIFIED"
    assert updated["reviewer_notes"] == "Geotechnical team validated active slip plane."


def test_alerts_and_human_authorization_workflow(client):
    # 1. Get active alerts
    resp = client.get("/api/alerts")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_alerts"] >= 1
    alert_id = data["alerts"][0]["alert_id"]

    # 2. Get alert detail
    detail_resp = client.get(f"/api/alerts/{alert_id}")
    assert detail_resp.status_code == 200
    assert detail_resp.json()["alert_id"] == alert_id

    # 3. Authorize alert
    auth_payload = {
        "new_status": "AUTHORIZED",
        "reviewer_notes": "Rainfall threshold confirmed by local IMD AWS station.",
        "authorizer_name": "Senior Geotechnical Officer",
    }
    patch_resp = client.patch(f"/api/alerts/{alert_id}/authorization", json=auth_payload)
    assert patch_resp.status_code == 200
    updated = patch_resp.json()
    assert updated["status"] == "AUTHORIZED"
    assert updated["authorized_by"] == "Senior Geotechnical Officer"


def test_early_warning_strategy_endpoints(client):
    response = client.get("/api/early-warning/strategy")
    assert response.status_code == 200
    data = response.json()
    assert len(data["operating_points"]) >= 2
    assert len(data["persistence_rules"]) >= 3
    assert len(data["warning_frequencies"]) >= 2
    assert len(data["threshold_curve"]) > 10
    assert data["calibration"]["brier_score"] == 0.1652

    # Check balanced mode values
    balanced = next((op for op in data["operating_points"] if "Balanced" in op["operating_mode"]), None)
    assert balanced is not None
    assert balanced["selected_threshold"] == 0.65
    assert balanced["f1"] == 0.25


def test_future_integrations_endpoints(client):
    # 1. Status and Boundaries
    resp = client.get("/api/integrations/status")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["boundaries"]) >= 6
    assert data["multimodal_extension_blueprint"]["current_equation"] == "R = 0.25 * E_spatial + 0.25 * S_terrain + 0.50 * T_temporal"

    # Check that live IMD and IoT are NOT CONNECTED
    imd = next(b for b in data["boundaries"] if b["boundary_id"] == "BOUND_IMD_WEATHER")
    assert imd["status"] == "NOT CONNECTED"

    iot = next(b for b in data["boundaries"] if b["boundary_id"] == "BOUND_IOT_SOIL_SENSORS")
    assert iot["status"] == "NOT CONNECTED"

    insar = next(b for b in data["boundaries"] if b["boundary_id"] == "BOUND_SENTINEL1_INSAR")
    assert insar["status"] == "NOT CONNECTED"

    # 2. Multilingual Advisory Generator
    adv_payload = {
        "alert_id": "ALT-TEST-999",
        "risk_level": "CRITICAL",
        "location_name": "NH-6 Sonapur Tunnel, Meghalaya",
        "recommended_action": "Evacuate downhill settlements and suspend all vehicular movement.",
    }
    adv_resp = client.post("/api/integrations/generate-multilingual-advisory", json=adv_payload)
    assert adv_resp.status_code == 200
    adv = adv_resp.json()
    assert "en" in adv["languages"]
    assert "as" in adv["languages"]
    assert "bn" in adv["languages"]
    assert "hi" in adv["languages"]
    assert "kha" in adv["languages"]
    assert "mzo" in adv["languages"]
    assert "mni" in adv["languages"]
    assert "ne" in adv["languages"]




