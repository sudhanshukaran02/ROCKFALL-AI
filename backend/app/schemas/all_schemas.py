from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class SystemHealthResponse(BaseModel):
    status: str = Field(default="ONLINE")
    system_name: str = Field(default="NER-LENS")
    system_title: str
    version: str
    operating_mode: str
    disclaimer: str
    latest_data_date: str
    live_feeds_connected: bool = False
    total_monitored_events: int
    models_ready_count: int
    active_operating_mode: str = "Balanced Mode (r_th = 0.65)"

class ModelStatusItem(BaseModel):
    model_id: str
    name: str
    domain: str
    modality: str
    status: str
    checkpoint_path: str
    checkpoint_exists: bool
    primary_metric_name: str
    primary_metric_value: float | str
    recall: Optional[float] = None
    precision: Optional[float] = None
    f1_score: Optional[float] = None
    roc_auc: Optional[float] = None
    pr_auc: Optional[float] = None
    limitations: str

class LandslideEventItem(BaseModel):
    event_id: str
    event_date: str
    latitude: float
    longitude: float
    state: str
    district: Optional[str] = None
    location_name: str
    source: str
    verification_status: str = "VERIFIED"
    fatalities: Optional[int] = None
    rainfall_7d_mm: Optional[float] = None

class LandslideEventListResponse(BaseModel):
    total_count: int
    data_status: str = "HISTORICAL / VERIFIED"
    events: List[LandslideEventItem]

class CurrentRiskResponse(BaseModel):
    date: str
    spatial_evidence: float
    terrain_susceptibility: float
    temporal_risk: float
    multimodal_risk: float
    warning_level: str
    contributions: Dict[str, float]
    explainability: str
    data_status: str = "MODEL OUTPUT"
    notice: str

class RiskTimelinePoint(BaseModel):
    date: str
    multimodal_risk: float
    temporal_risk: float
    warning_level: str
    is_event_day: bool = False

class RiskTimelineResponse(BaseModel):
    total_days: int
    start_date: str
    end_date: str
    data_status: str = "HISTORICAL / MODEL OUTPUT"
    points: List[RiskTimelinePoint]

class TerrainDerivativeStats(BaseModel):
    min: float
    mean: float
    max: float

class TerrainSummaryResponse(BaseModel):
    elevation_m: TerrainDerivativeStats
    slope_deg: TerrainDerivativeStats
    aspect_deg: TerrainDerivativeStats
    curvature: TerrainDerivativeStats
    roughness: TerrainDerivativeStats
    twi: TerrainDerivativeStats
    s_terrain_index: float
    resolution_m: int = 30
    source: str = "SRTM 30m Global DEM"
    data_status: str = "HISTORICAL"

class WeatherRecord(BaseModel):
    date: str
    precipitation_mm: float
    rolling_7d_rain_mm: float
    rolling_30d_rain_mm: float
    temp_mean_c: float
    humidity_pct: float

class WeatherHistoryResponse(BaseModel):
    total_records: int
    start_date: str
    end_date: str
    data_status: str = "HISTORICAL"
    live_source_status: str = "NOT CONNECTED"
    records: List[WeatherRecord]

class LSTMPredictionPoint(BaseModel):
    date: str
    lstm_probability: float
    warning_level: str
    is_event_day: bool = False

class LSTMPredictionsResponse(BaseModel):
    test_year: int = 2024
    total_test_days: int
    best_ablation: str = "Weather features"
    test_pr_auc: float = 0.1488
    test_roc_auc: float = 0.8404
    data_status: str = "HISTORICAL / MODEL OUTPUT"
    predictions: List[LSTMPredictionPoint]

class FusionPredictionRecord(BaseModel):
    date: str
    e_spatial: float
    s_terrain: float
    t_temporal: float
    r_multimodal: float
    warning_level: str

class FusionPredictionsResponse(BaseModel):
    formula: str = "R = 0.25 * E + 0.25 * S + 0.50 * T"
    test_roc_auc: float = 0.8682
    test_pr_auc: float = 0.1099
    data_status: str = "HISTORICAL / MODEL OUTPUT"
    records: List[FusionPredictionRecord]

class AlertEvaluationRequest(BaseModel):
    current_risk: float = Field(ge=0.0, le=1.0)
    operating_mode: str = "Balanced Mode"
    persistence_active: bool = True

class AlertItem(BaseModel):
    alert_id: str
    timestamp: str
    operating_mode: str
    selected_threshold: float
    current_risk: float
    warning_level: str
    is_alert_triggered: bool
    persistence_rule: str
    recommended_action: str
    disclaimer: str
    status: str = "MODEL_RECOMMENDATION"
    location: str = "Regional Sector (NER Corridor)"
    trigger_source: str = "Multimodal Risk Engine (0.25E+0.25S+0.50T)"
    reviewer_notes: Optional[str] = ""
    authorized_by: Optional[str] = None
    authorized_at: Optional[str] = None

class AlertAuthorizationRequest(BaseModel):
    new_status: str  # "AUTHORIZED" | "REJECTED" | "HUMAN_REVIEW"
    reviewer_notes: Optional[str] = ""
    authorizer_name: Optional[str] = "District Disaster Officer"

class AlertsListResponse(BaseModel):
    total_alerts: int
    operating_mode: str
    alerts: List[AlertItem]

class FieldReportCreateRequest(BaseModel):
    latitude: float
    longitude: float
    incident_type: str
    severity: str
    description: str
    photo_path: Optional[str] = "None"
    reporter_name: Optional[str] = "Citizen / Field Engineer"
    infrastructure_affected: Optional[str] = "Road / Slope Transit"
    road_blocked: Optional[bool] = False

class FieldReportVerificationRequest(BaseModel):
    new_status: str  # "VERIFIED" | "REJECTED" | "PENDING_VERIFICATION"
    reviewer_notes: Optional[str] = ""

class FieldReportItem(BaseModel):
    report_id: str
    timestamp: str
    latitude: float
    longitude: float
    incident_type: str
    severity: str
    description: str
    photo_path: str = "None"
    reporter_name: Optional[str] = "Citizen / Field Engineer"
    infrastructure_affected: Optional[str] = "Road / Slope Transit"
    road_blocked: Optional[bool] = False
    status: str = "PENDING_VERIFICATION"
    reviewer_notes: Optional[str] = ""
    verified_at: Optional[str] = ""

class FieldReportsListResponse(BaseModel):
    total_count: int
    data_status: str = "PROTOTYPE"
    reports: List[FieldReportItem]

class JhariaSummaryResponse(BaseModel):
    application_title: str
    subtitle: str
    domain: str = "SECONDARY_MINING_APPLICATION"
    aoi_name: str
    bounds: Dict[str, float]
    aoi_area_km2: Optional[float] = 1.4503
    spatial_points_count: Optional[int] = 1665
    model_a_status: str
    model_b_status: str
    benchmark_metrics: Dict[str, Any]
    disclaimer: str

class JhariaEventItem(BaseModel):
    event_id: str
    date: str
    event_type: Optional[str] = "SLOPE_FAILURE"
    latitude: float
    longitude: float
    slope: float
    terrain_susceptibility_index: float
    susceptibility_class: str

class JhariaEventsResponse(BaseModel):
    total_events: int
    events: List[JhariaEventItem]

class JhariaTop50Point(BaseModel):
    point_id: int
    latitude: float
    longitude: float
    slope: float
    terrain_susceptibility_index: float
    susceptibility_class: str

class JhariaTerrainResponse(BaseModel):
    aoi: str
    total_points: int
    top_points: List[JhariaTop50Point]
    terrain_statistics: Optional[Dict[str, Any]] = None
    zone_summary: Dict[str, Any]

class JhariaSimulationRequest(BaseModel):
    geotechnical_susceptibility: float = Field(ge=0.0, le=1.0)
    weather_trigger_index: float = Field(ge=0.0, le=1.0)

class JhariaSimulationResponse(BaseModel):
    scenario_type: str = "HYPOTHETICAL_MINING_SCENARIO_SIMULATION"
    model_a_geotechnical_input: float
    model_b_weather_trigger_input: float
    composite_mining_risk_index: float
    mining_risk_class: str
    recommended_mine_action: str
    disclaimer: str


class DataHealthItem(BaseModel):
    layer_name: str
    category: str
    status: str
    source_name: str
    update_frequency: str
    coverage_area: str
    notes: str

class DataHealthResponse(BaseModel):
    total_layers: int
    layers: List[Dict[str, Any]]

class UNetInferenceResponse(BaseModel):
    status: str
    spatial_evidence: float
    detected_pixels: int
    total_pixels: int
    coverage_percentage: float
    input_image_base64: str
    mask_image_base64: str
    heatmap_image_base64: str
    model_name: str = "4-Channel UNet Segmentation"
    metrics: Dict[str, float]
    data_status: str = "MODEL OUTPUT"
    notes: str

class OperatingPointItem(BaseModel):
    operating_mode: str
    selected_threshold: float
    precision: float
    recall: float
    f1: float
    specificity: float
    false_positive_rate: float
    balanced_accuracy: float

class PersistenceItem(BaseModel):
    persistence_rule: str
    selected_threshold: float
    test_precision: float
    test_recall: float
    test_f1: float
    total_warning_days: int
    false_warning_days_fp: int
    correct_warning_days_tp: int
    missed_event_days_fn: int

class WarningFrequencyItem(BaseModel):
    operating_mode: str
    threshold: float
    total_days: int
    total_warning_days: int
    warning_percentage: float
    correct_warning_days_tp: int
    false_warning_days_fp: int
    missed_event_days_fn: int

class ThresholdCurvePoint(BaseModel):
    threshold: float
    precision: float
    recall: float
    f1: float
    specificity: float

class EarlyWarningStrategyResponse(BaseModel):
    operating_points: List[OperatingPointItem]
    persistence_rules: List[PersistenceItem]
    warning_frequencies: List[WarningFrequencyItem]
    threshold_curve: List[ThresholdCurvePoint]
    calibration: Dict[str, Any]
    disclaimer: str
    data_status: str = "HISTORICAL BENCHMARKS"

class CheckpointHealthItem(BaseModel):
    name: str
    checkpoint_path: str
    exists: bool
    size_bytes: int
    status: str

class ModelHealthItem(BaseModel):
    model_name: str
    purpose: str
    checkpoint: str
    status: str
    operational_role: str
    key_metrics: Dict[str, Any]

class ValidationMatrixItem(BaseModel):
    component: str
    training_completed: str
    validation_completed: str
    test_evaluation: str
    operational_status: str

class ConnectivityMatrixItem(BaseModel):
    source: str
    connection_type: str
    status: str
    purpose: str

class ModelHealthResponse(BaseModel):
    system_status: str = "RESEARCH DECISION-SUPPORT READY"
    models: List[ModelHealthItem]
    checkpoints: List[CheckpointHealthItem]
    validation_matrix: List[ValidationMatrixItem]
    connectivity_matrix: List[ConnectivityMatrixItem]
    data_freshness: Dict[str, Any]
    scientific_limitations: List[str]
    quality_summary: Dict[str, Any]


# -------------------------------------------------------------------
# STAGE 11: FUTURE INTEGRATION BOUNDARIES & ADAPTER SCHEMAS
# -------------------------------------------------------------------
class IntegrationBoundaryItem(BaseModel):
    boundary_id: str
    provider_name: str
    category: str
    purpose: str
    status: str
    ingestion_protocol: str
    expected_schema_fields: List[str]
    provenance_rules: Dict[str, Any]
    operational_notes: str

class MultilingualAdvisoryTemplateRequest(BaseModel):
    alert_id: str
    risk_level: str
    location_name: str
    recommended_action: str

class MultilingualAdvisoryTemplateResponse(BaseModel):
    alert_id: str
    risk_level: str
    location_name: str
    generated_at: str
    disclaimer: str
    languages: Dict[str, Dict[str, str]]

class FutureIntegrationsStatusResponse(BaseModel):
    architecture_version: str = "2.0-INTEGRATION-READINESS"
    overall_connectivity: str = "HISTORICAL BENCHMARKS ONLY (NO LIVE SENSORS)"
    disclaimer: str
    boundaries: List[IntegrationBoundaryItem]
    multimodal_extension_blueprint: Dict[str, Any]
    offline_sync_spec: Dict[str, Any]
    data_ingestion_pipeline_flow: List[Dict[str, str]]


