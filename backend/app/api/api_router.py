from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from backend.app.schemas.all_schemas import (
    SystemHealthResponse,
    ModelStatusItem,
    LandslideEventListResponse,
    CurrentRiskResponse,
    RiskTimelineResponse,
    TerrainSummaryResponse,
    WeatherHistoryResponse,
    LSTMPredictionsResponse,
    FusionPredictionsResponse,
    AlertsListResponse,
    AlertItem,
    AlertEvaluationRequest,
    AlertAuthorizationRequest,
    FieldReportsListResponse,
    FieldReportCreateRequest,
    FieldReportItem,
    FieldReportVerificationRequest,
    JhariaSummaryResponse,
    JhariaEventsResponse,
    JhariaTerrainResponse,
    JhariaSimulationRequest,
    JhariaSimulationResponse,
    DataHealthResponse,
    ModelHealthResponse,
    UNetInferenceResponse,
    EarlyWarningStrategyResponse,
    FutureIntegrationsStatusResponse,
    MultilingualAdvisoryTemplateRequest,
    MultilingualAdvisoryTemplateResponse,
)

from backend.app.adapters.all_adapters import (
    get_system_health,
    get_models_status,
    get_verified_landslides,
    get_current_risk,
    get_risk_timeline,
    get_terrain_summary,
    get_weather_history,
    get_lstm_predictions,
    get_fusion_predictions,
    get_active_alerts,
    get_alert_by_id_adapter,
    update_alert_authorization_adapter,
    evaluate_custom_alert,
    get_field_observations_adapter,
    get_field_report_by_id_adapter,
    update_field_report_verification_adapter,
    submit_field_observation_adapter,
    get_jharia_summary,
    get_jharia_events,
    get_jharia_terrain,
    simulate_jharia_risk_adapter,
    get_data_health,
    get_model_health_adapter,
    run_unet_inference_adapter,
    get_early_warning_strategy_adapter,
    get_future_integrations_adapter,
    generate_multilingual_advisory_adapter,
)


api_router = APIRouter()


# 1. System Health
@api_router.get("/system/health", response_model=SystemHealthResponse)
def api_system_health():
    return get_system_health()


# 2. Models Status
@api_router.get("/models/status", response_model=list[ModelStatusItem])
def api_models_status():
    return get_models_status()


# 3. Verified Landslide Events
@api_router.get("/landslides", response_model=LandslideEventListResponse)
def api_landslides():
    events = get_verified_landslides()
    return {"total_count": len(events), "data_status": "HISTORICAL / VERIFIED", "events": events}


# 4. Current Multimodal Risk
@api_router.get("/risk/current", response_model=CurrentRiskResponse)
def api_risk_current():
    return get_current_risk()


# 5. Risk Timeline
@api_router.get("/risk/timeline", response_model=RiskTimelineResponse)
def api_risk_timeline():
    return get_risk_timeline()


# 6. Terrain Susceptibility Summary
@api_router.get("/terrain", response_model=TerrainSummaryResponse)
def api_terrain():
    return get_terrain_summary()


# 7. Weather / Environmental History
@api_router.get("/weather/history", response_model=WeatherHistoryResponse)
def api_weather_history(limit: int = Query(default=100, ge=1, le=2557)):
    return get_weather_history(limit=limit)


# 8. LSTM Predictions
@api_router.get("/lstm/predictions", response_model=LSTMPredictionsResponse)
def api_lstm_predictions():
    return get_lstm_predictions()


# 9. Multimodal Fusion Predictions
@api_router.get("/fusion/predictions", response_model=FusionPredictionsResponse)
def api_fusion_predictions():
    return get_fusion_predictions()


# 10. Alerts Management & Human Authorization
@api_router.get("/alerts", response_model=AlertsListResponse)
def api_alerts():
    return get_active_alerts()


@api_router.get("/alerts/{alert_id}", response_model=AlertItem)
def api_alert_detail(alert_id: str):
    res = get_alert_by_id_adapter(alert_id)
    if not res:
        raise HTTPException(status_code=404, detail="Alert not found")
    return res


@api_router.patch("/alerts/{alert_id}/authorization", response_model=AlertItem)
def api_alert_authorize(alert_id: str, req: AlertAuthorizationRequest):
    res = update_alert_authorization_adapter(
        alert_id=alert_id,
        new_status=req.new_status,
        reviewer_notes=req.reviewer_notes or "",
        authorizer_name=req.authorizer_name or "District Disaster Officer",
    )
    if not res:
        raise HTTPException(status_code=404, detail="Alert not found")
    return res


@api_router.post("/alerts/evaluate", response_model=AlertItem)
def api_alerts_evaluate(req: AlertEvaluationRequest):
    return evaluate_custom_alert(
        current_risk=req.current_risk,
        operating_mode=req.operating_mode,
        persistence_active=req.persistence_active,
    )


# 11. Field Observations & Verification Workflow
@api_router.get("/field-observations", response_model=FieldReportsListResponse)
@api_router.get("/field-reports", response_model=FieldReportsListResponse)
def api_field_observations():
    return get_field_observations_adapter()


@api_router.get("/field-reports/{report_id}", response_model=FieldReportItem)
@api_router.get("/field-observations/{report_id}", response_model=FieldReportItem)
def api_field_report_detail(report_id: str):
    res = get_field_report_by_id_adapter(report_id)
    if not res:
        raise HTTPException(status_code=404, detail="Field report not found")
    return res


@api_router.patch("/field-reports/{report_id}/verification", response_model=FieldReportItem)
@api_router.patch("/field-observations/{report_id}/verification", response_model=FieldReportItem)
def api_field_report_verify(report_id: str, req: FieldReportVerificationRequest):
    res = update_field_report_verification_adapter(
        report_id=report_id,
        new_status=req.new_status,
        reviewer_notes=req.reviewer_notes or "",
    )
    if not res:
        raise HTTPException(status_code=404, detail="Field report not found")
    return res


@api_router.post("/field-observations", response_model=FieldReportItem)
@api_router.post("/field-reports", response_model=FieldReportItem)
def api_field_observations_create(req: FieldReportCreateRequest):
    return submit_field_observation_adapter(
        latitude=req.latitude,
        longitude=req.longitude,
        incident_type=req.incident_type,
        severity=req.severity,
        description=req.description,
        photo_path=req.photo_path or "None",
        reporter_name=req.reporter_name or "Citizen / Field Engineer",
        infrastructure_affected=req.infrastructure_affected or "Road / Slope Transit",
        road_blocked=req.road_blocked or False,
    )


# 12. Jharia Mining Application (Dedicated Namespace)
@api_router.get("/jharia/summary", response_model=JhariaSummaryResponse)
def api_jharia_summary():
    return get_jharia_summary()


@api_router.get("/jharia/events", response_model=JhariaEventsResponse)
def api_jharia_events():
    return get_jharia_events()


@api_router.get("/jharia/terrain", response_model=JhariaTerrainResponse)
def api_jharia_terrain():
    return get_jharia_terrain()


@api_router.post("/jharia/simulate", response_model=JhariaSimulationResponse)
def api_jharia_simulate(req: JhariaSimulationRequest):
    return simulate_jharia_risk_adapter(
        geotechnical_susceptibility=req.geotechnical_susceptibility,
        weather_trigger_index=req.weather_trigger_index,
    )



# 13. Data Health & Model Health Grids
@api_router.get("/data-health", response_model=DataHealthResponse)
def api_data_health():
    return get_data_health()


@api_router.get("/model-health", response_model=ModelHealthResponse)
def api_model_health():
    return get_model_health_adapter()



# 14. U-Net Landslide Segmentation Inference
@api_router.get("/unet/sample", response_model=UNetInferenceResponse)
def api_unet_sample():
    return run_unet_inference_adapter(image_bytes=None)


@api_router.post("/unet/predict", response_model=UNetInferenceResponse)
def api_unet_predict():
    return run_unet_inference_adapter(image_bytes=None)


# 15. Early Warning Strategy & Optimization
@api_router.get("/early-warning/strategy", response_model=EarlyWarningStrategyResponse)
def api_early_warning_strategy():
    return get_early_warning_strategy_adapter()


# 16. Future Integration Boundaries & Multilingual Templates
@api_router.get("/integrations/status", response_model=FutureIntegrationsStatusResponse)
def api_integrations_status():
    return get_future_integrations_adapter()


@api_router.post("/integrations/generate-multilingual-advisory", response_model=MultilingualAdvisoryTemplateResponse)
def api_generate_multilingual_advisory(req: MultilingualAdvisoryTemplateRequest):
    return generate_multilingual_advisory_adapter(req.model_dump())


