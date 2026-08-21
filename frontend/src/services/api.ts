import {
  SystemHealth,
  ModelStatusItem,
  CurrentRiskResponse,
  LandslideEventListResponse,
  RiskTimelineResponse,
  FusionPredictionsResponse,
  AlertsListResponse,
  DataHealthResponse,
  TerrainSummary,
} from '@/types';

const API_BASE = '/api';

export async function fetchSystemHealth(): Promise<SystemHealth> {
  const res = await fetch(`${API_BASE}/system/health`);
  if (!res.ok) throw new Error('Failed to fetch system health');
  return res.json();
}

export async function fetchModelsStatus(): Promise<ModelStatusItem[]> {
  const res = await fetch(`${API_BASE}/models/status`);
  if (!res.ok) throw new Error('Failed to fetch models status');
  return res.json();
}

export async function fetchCurrentRisk(): Promise<CurrentRiskResponse> {
  const res = await fetch(`${API_BASE}/risk/current`);
  if (!res.ok) throw new Error('Failed to fetch current risk');
  return res.json();
}

export async function fetchLandslides(): Promise<LandslideEventListResponse> {
  const res = await fetch(`${API_BASE}/landslides`);
  if (!res.ok) throw new Error('Failed to fetch verified landslide events');
  return res.json();
}

export async function fetchRiskTimeline(): Promise<RiskTimelineResponse> {
  const res = await fetch(`${API_BASE}/risk/timeline`);
  if (!res.ok) throw new Error('Failed to fetch risk timeline');
  return res.json();
}

export async function fetchFusionPredictions(): Promise<FusionPredictionsResponse> {
  const res = await fetch(`${API_BASE}/fusion/predictions`);
  if (!res.ok) throw new Error('Failed to fetch fusion predictions');
  return res.json();
}

export async function fetchLSTMPredictions(): Promise<any> {
  const res = await fetch(`${API_BASE}/lstm/predictions`);
  if (!res.ok) throw new Error('Failed to fetch LSTM predictions');
  return res.json();
}


export async function fetchAlerts(): Promise<AlertsListResponse> {
  const res = await fetch(`${API_BASE}/alerts`);
  if (!res.ok) throw new Error('Failed to fetch alerts');
  return res.json();
}

export async function fetchDataHealth(): Promise<DataHealthResponse> {
  const res = await fetch(`${API_BASE}/data-health`);
  if (!res.ok) throw new Error('Failed to fetch data health');
  return res.json();
}

export async function fetchModelHealth(): Promise<any> {
  const res = await fetch(`${API_BASE}/model-health`);
  if (!res.ok) throw new Error('Failed to fetch model health');
  return res.json();
}


export async function fetchTerrainSummary(): Promise<TerrainSummary> {
  const res = await fetch(`${API_BASE}/terrain`);
  if (!res.ok) throw new Error('Failed to fetch terrain summary');
  return res.json();
}

export async function fetchFieldObservations(): Promise<{ total_count: number; data_status: string; reports: any[] }> {
  const res = await fetch(`${API_BASE}/field-observations`);
  if (!res.ok) throw new Error('Failed to fetch field observations');
  return res.json();
}

export async function fetchUNetSample(): Promise<any> {
  const res = await fetch(`${API_BASE}/unet/sample`);
  if (!res.ok) throw new Error('Failed to fetch UNet sample inference');
  return res.json();
}

export async function fetchWeatherHistory(limit: number = 100): Promise<any> {
  const res = await fetch(`${API_BASE}/weather/history?limit=${limit}`);
  if (!res.ok) throw new Error('Failed to fetch weather history');
  return res.json();
}

export async function fetchEarlyWarningStrategy(): Promise<any> {
  const res = await fetch(`${API_BASE}/early-warning/strategy`);
  if (!res.ok) throw new Error('Failed to fetch early warning strategy');
  return res.json();
}

export async function evaluateCustomAlert(params: {
  current_risk: number;
  operating_mode: string;
  persistence_active?: boolean;
}): Promise<any> {
  const res = await fetch(`${API_BASE}/alerts/evaluate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  if (!res.ok) throw new Error('Failed to evaluate custom alert');
  return res.json();
}

export async function submitFieldReport(payload: {
  latitude: number;
  longitude: number;
  incident_type: string;
  severity: string;
  description: string;
  photo_path?: string;
  reporter_name?: string;
  infrastructure_affected?: string;
  road_blocked?: boolean;
}): Promise<any> {
  const res = await fetch(`${API_BASE}/field-reports`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Failed to submit field report');
  return res.json();
}

export async function verifyFieldReport(params: {
  report_id: string;
  new_status: string;
  reviewer_notes?: string;
}): Promise<any> {
  const res = await fetch(`${API_BASE}/field-reports/${params.report_id}/verification`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      new_status: params.new_status,
      reviewer_notes: params.reviewer_notes || '',
    }),
  });
  if (!res.ok) throw new Error('Failed to update field report verification status');
  return res.json();
}

export async function authorizeAlert(params: {
  alert_id: string;
  new_status: string;
  reviewer_notes?: string;
  authorizer_name?: string;
}): Promise<any> {
  const res = await fetch(`${API_BASE}/alerts/${params.alert_id}/authorization`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      new_status: params.new_status,
      reviewer_notes: params.reviewer_notes || '',
      authorizer_name: params.authorizer_name || 'District Disaster Officer',
    }),
  });
  if (!res.ok) throw new Error('Failed to authorize/reject alert');
  return res.json();
}

export async function fetchJhariaSummary(): Promise<any> {
  const res = await fetch(`${API_BASE}/jharia/summary`);
  if (!res.ok) throw new Error('Failed to fetch Jharia mining summary');
  return res.json();
}


export async function fetchJhariaEvents(): Promise<any> {
  const res = await fetch(`${API_BASE}/jharia/events`);
  if (!res.ok) throw new Error('Failed to fetch Jharia events');
  return res.json();
}

export async function fetchJhariaTerrain(): Promise<any> {
  const res = await fetch(`${API_BASE}/jharia/terrain`);
  if (!res.ok) throw new Error('Failed to fetch Jharia terrain points');
  return res.json();
}

export async function simulateJhariaRisk(params: {
  geotechnical_susceptibility: number;
  weather_trigger_index: number;
}): Promise<any> {
  const res = await fetch(`${API_BASE}/jharia/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  if (!res.ok) throw new Error('Failed to simulate Jharia mining risk');
  return res.json();
}

export async function fetchFutureIntegrations(): Promise<any> {
  const res = await fetch(`${API_BASE}/integrations/status`);
  if (!res.ok) throw new Error('Failed to fetch future integrations status');
  return res.json();
}

export async function generateMultilingualAdvisory(payload: {
  alert_id: string;
  risk_level: string;
  location_name: string;
  recommended_action: string;
}): Promise<any> {
  const res = await fetch(`${API_BASE}/integrations/generate-multilingual-advisory`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Failed to generate multilingual advisory');
  return res.json();
}




