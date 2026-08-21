import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AppLayout } from './components/layout/AppLayout';

import { CommandCenter } from './pages/CommandCenter';
import { RiskMap } from './pages/RiskMap';
import { LandslideDetection } from './pages/LandslideDetection';
import { TerrainSusceptibility } from './pages/TerrainSusceptibility';
import { WeatherRisk } from './pages/WeatherRisk';
import { LSTMTemporalRisk } from './pages/LSTMTemporalRisk';
import { MultimodalRisk } from './pages/MultimodalRisk';
import { EarlyWarning } from './pages/EarlyWarning';
import { LandslideInventory } from './pages/LandslideInventory';
import { FieldObservations } from './pages/FieldObservations';
import { AlertManagement } from './pages/AlertManagement';
import { ModelStatus } from './pages/ModelStatus';
import { DataHealth } from './pages/DataHealth';
import { JhariaMining } from './pages/JhariaMining';
import { FutureIntegrations } from './pages/FutureIntegrations';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppLayout />}>
          <Route index element={<CommandCenter />} />
          <Route path="risk-map" element={<RiskMap />} />
          <Route path="detection" element={<LandslideDetection />} />
          <Route path="terrain" element={<TerrainSusceptibility />} />
          <Route path="weather" element={<WeatherRisk />} />
          <Route path="temporal-risk" element={<LSTMTemporalRisk />} />
          <Route path="multimodal-risk" element={<MultimodalRisk />} />
          <Route path="early-warning" element={<EarlyWarning />} />
          <Route path="inventory" element={<LandslideInventory />} />
          <Route path="field-reports" element={<FieldObservations />} />
          <Route path="alerts" element={<AlertManagement />} />
          <Route path="models" element={<ModelStatus />} />
          <Route path="data-health" element={<DataHealth />} />
          <Route path="jharia" element={<JhariaMining />} />
          <Route path="integrations" element={<FutureIntegrations />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};


export default App;
