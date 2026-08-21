export type RiskLevel = 'LOW' | 'WATCH' | 'MODERATE' | 'WARNING' | 'HIGH' | 'CRITICAL';

export type DataStatus = 
  | 'LIVE'
  | 'RECENT'
  | 'HISTORICAL'
  | 'MODEL OUTPUT'
  | 'VERIFIED'
  | 'PROTOTYPE'
  | 'DEMO DATA'
  | 'SIMULATED DATA'
  | 'UNAVAILABLE'
  | 'NOT CONNECTED';

export interface SystemHealth {
  status: 'ONLINE' | 'DEGRADED' | 'OFFLINE';
  system_name: string;
  version: string;
  operating_mode: string;
  disclaimer: string;
  latest_data_date: string;
  live_feeds_connected: boolean;
  total_monitored_events: number;
  models_ready_count?: number;
  active_operating_mode?: string;
}

export interface ModelStatusItem {
  model_id: string;
  name: string;
  domain: 'NER_PRIMARY' | 'JHARIA_SECONDARY';
  modality: 'SPATIAL' | 'TERRAIN' | 'TEMPORAL' | 'FUSION' | 'MINING';
  status: 'READY' | 'PROTOTYPE' | 'EXPERIMENTAL' | 'NOT_CONNECTED';
  checkpoint_path: string;
  primary_metric_name: string;
  primary_metric_value: number | string;
  recall?: number;
  precision?: number;
  f1_score?: number;
  roc_auc?: number;
  pr_auc?: number;
  limitations: string;
}

export interface LandslideEvent {
  event_id: string;
  event_date: string;
  latitude: number;
  longitude: number;
  state: string;
  district?: string;
  location_name: string;
  source: string;
  verification_status: 'VERIFIED' | 'CANDIDATE' | 'UNVERIFIED';
  fatalities?: number;
  rainfall_7d_mm?: number;
}

export interface LandslideEventListResponse {
  total_count: number;
  data_status: string;
  events: LandslideEvent[];
}

export interface CurrentRiskResponse {
  date: string;
  spatial_evidence: number;
  terrain_susceptibility: number;
  temporal_risk: number;
  multimodal_risk: number;
  warning_level: RiskLevel;
  contributions: {
    spatial_contribution: number;
    terrain_contribution: number;
    temporal_contribution: number;
    spatial_pct: number;
    terrain_pct: number;
    temporal_pct: number;
  };
  explainability: string;
  data_status: DataStatus;
  notice: string;
}

export interface MultimodalRiskState extends CurrentRiskResponse {}

export interface TerrainSummary {
  elevation_m: { min: number; mean: number; max: number };
  slope_deg: { min: number; mean: number; max: number };
  aspect_deg: { min: number; mean: number; max: number };
  curvature: { min: number; mean: number; max: number };
  roughness: { min: number; mean: number; max: number };
  twi: { min: number; mean: number; max: number };
  s_terrain_index: number;
  resolution_m: number;
  source: string;
}

export interface EarlyWarningAlert {
  alert_id: string;
  timestamp: string;
  operating_mode: string;
  selected_threshold: number;
  current_risk: number;
  warning_level: RiskLevel;
  is_alert_triggered: boolean;
  persistence_rule: string;
  recommended_action: string;
  disclaimer: string;
  status: 'MODEL_RECOMMENDATION' | 'HUMAN_REVIEW' | 'AUTHORIZED' | 'REJECTED';
  location?: string;
  trigger_source?: string;
  reviewer_notes?: string;
  authorized_by?: string | null;
  authorized_at?: string | null;
}

export interface AlertsListResponse {
  total_alerts: number;
  operating_mode: string;
  alerts: EarlyWarningAlert[];
}

export type IncidentType =
  | 'LANDSLIDE'
  | 'SLOPE_FAILURE'
  | 'CRACK'
  | 'ROCKFALL'
  | 'ROAD_BLOCKAGE'
  | 'FLOOD'
  | 'OTHER';

export type ReportSeverity = 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';
export type ReportVerificationStatus = 'PENDING_VERIFICATION' | 'VERIFIED' | 'REJECTED' | 'SUBMITTED_PROTOTYPE';

export interface FieldObservation {
  report_id: string;
  timestamp: string;
  latitude: number;
  longitude: number;
  incident_type: string;
  severity: string;
  description: string;
  photo_path?: string;
  reporter_name?: string;
  infrastructure_affected?: string;
  road_blocked?: boolean;
  status: ReportVerificationStatus;
  reviewer_notes?: string;
  verified_at?: string;
}

export interface FieldReportsListResponse {
  total_count: number;
  data_status: string;
  reports: FieldObservation[];
}

export interface FieldReportCreatePayload {
  latitude: number;
  longitude: number;
  incident_type: string;
  severity: string;
  description: string;
  photo_path?: string;
  reporter_name?: string;
  infrastructure_affected?: string;
  road_blocked?: boolean;
}


export interface JhariaMineSummary {
  application_title: string;
  subtitle: string;
  aoi_name: string;
  bounds: { lat_min: number; lat_max: number; lon_min: number; lon_max: number };
  models: {
    model_a: { name: string; type: string; features: string[] };
    model_b: { name: string; type: string; features: string[] };
  };
  terrain_benchmark: {
    mean_index: number;
    median_index: number;
    max_index: number;
    high_susceptibility_event: string;
  };
}

export interface DataHealthItem {
  layer_name: string;
  category: 'SATELLITE' | 'TERRAIN' | 'METEOROLOGY' | 'GEOTECHNICAL' | 'EXPOSURE' | 'INFRASTRUCTURE';
  status: DataStatus;
  source_name: string;
  update_frequency: string;
  coverage_area: string;
  notes: string;
}

export interface RiskTimelinePoint {
  date: string;
  multimodal_risk: number;
  temporal_risk: number;
  warning_level: RiskLevel;
  is_event_day: boolean;
}

export interface RiskTimelineResponse {
  total_days: number;
  start_date: string;
  end_date: string;
  data_status: string;
  points: RiskTimelinePoint[];
}

export interface FusionPredictionRecord {
  date: string;
  e_spatial: number;
  s_terrain: number;
  t_temporal: number;
  r_multimodal: number;
  warning_level: string;
}

export interface FusionPredictionsResponse {
  formula: string;
  test_roc_auc: number;
  test_pr_auc: number;
  data_status: string;
  records: FusionPredictionRecord[];
}

export interface AlertsListResponse {
  total_alerts: number;
  operating_mode: string;
  alerts: EarlyWarningAlert[];
}

export interface DataHealthResponse {
  total_layers: number;
  layers: DataHealthItem[];
}

export interface CheckpointHealthItem {
  name: string;
  checkpoint_path: string;
  exists: boolean;
  size_bytes: number;
  status: string;
}

export interface ModelHealthItem {
  model_name: string;
  purpose: string;
  checkpoint: string;
  status: string;
  operational_role: string;
  key_metrics: Record<string, any>;
}

export interface ValidationMatrixItem {
  component: string;
  training_completed: string;
  validation_completed: string;
  test_evaluation: string;
  operational_status: string;
}

export interface ConnectivityMatrixItem {
  source: string;
  connection_type: string;
  status: string;
  purpose: string;
}

export interface ModelHealthResponse {
  system_status: string;
  models: ModelHealthItem[];
  checkpoints: CheckpointHealthItem[];
  validation_matrix: ValidationMatrixItem[];
  connectivity_matrix: ConnectivityMatrixItem[];
  data_freshness: Record<string, any>;
  scientific_limitations: string[];
  quality_summary: Record<string, any>;
}


export interface UNetInferenceResponse {
  status: string;
  spatial_evidence: number;
  detected_pixels: number;
  total_pixels: number;
  coverage_percentage: number;
  input_image_base64: string;
  mask_image_base64: string;
  heatmap_image_base64: string;
  model_name: string;
  metrics: {
    test_iou: number;
    test_dice_f1: number;
    test_recall: number;
    test_precision: number;
    pixel_accuracy: number;
  };
  data_status: string;
  notes: string;
}

export interface IntegrationBoundaryItem {
  boundary_id: string;
  provider_name: string;
  category: string;
  purpose: string;
  status: string;
  ingestion_protocol: string;
  expected_schema_fields: string[];
  provenance_rules: Record<string, any>;
  operational_notes: string;
}

export interface FutureIntegrationsStatusResponse {
  architecture_version: string;
  overall_connectivity: string;
  disclaimer: string;
  boundaries: IntegrationBoundaryItem[];
  multimodal_extension_blueprint: Record<string, any>;
  offline_sync_spec: Record<string, any>;
  data_ingestion_pipeline_flow: Array<{ step: string; name: string; detail: string }>;
}

export interface MultilingualAdvisoryResponse {
  alert_id: string;
  risk_level: string;
  location_name: string;
  generated_at: string;
  disclaimer: string;
  languages: Record<string, {
    language_name: string;
    title: string;
    location_label: string;
    location: string;
    action_label: string;
    action: string;
    verification_note: string;
  }>;
}

