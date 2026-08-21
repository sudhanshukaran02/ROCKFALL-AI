import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import {
  fetchJhariaSummary,
  fetchJhariaEvents,
  fetchJhariaTerrain,
  simulateJhariaRisk,
} from '@/services/api';
import { RiskBadge } from '@/components/common/RiskBadge';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorState } from '@/components/common/EmptyState';
import {
  Pickaxe,
  Sliders,
} from 'lucide-react';

export const JhariaMining: React.FC = () => {
  const [modelAInput, setModelAInput] = useState<number>(0.75);
  const [modelBInput, setModelBInput] = useState<number>(0.70);

  const summaryQ = useQuery({ queryKey: ['jhariaSummary'], queryFn: fetchJhariaSummary });
  const eventsQ = useQuery({ queryKey: ['jhariaEvents'], queryFn: fetchJhariaEvents });
  const terrainQ = useQuery({ queryKey: ['jhariaTerrain'], queryFn: fetchJhariaTerrain });

  const simMutation = useMutation({
    mutationFn: simulateJhariaRisk,
  });

  const isLoading = summaryQ.isLoading || eventsQ.isLoading || terrainQ.isLoading;
  const isError = summaryQ.isError || eventsQ.isError || terrainQ.isError;

  if (isLoading) {
    return (
      <div className="h-96 flex items-center justify-center">
        <LoadingSpinner label="Loading Jharia / Rajapur Open-Cast Mine Susceptibility Models..." size="lg" />
      </div>
    );
  }

  if (isError) {
    return (
      <ErrorState
        title="Jharia Mining Data Error"
        message="Failed to load Rajapur mine terrain and model outputs from FastAPI backend."
        onRetry={() => {
          summaryQ.refetch();
          eventsQ.refetch();
          terrainQ.refetch();
        }}
      />
    );
  }

  const events = eventsQ.data?.events || [];
  const terrain = terrainQ.data;
  const topPoints = terrain?.top_points || [];

  const simResult = simMutation.data || {
    composite_mining_risk_index: 0.50 * modelAInput + 0.50 * modelBInput,
    mining_risk_class:
      0.50 * modelAInput + 0.50 * modelBInput >= 0.70
        ? 'CRITICAL'
        : 0.50 * modelAInput + 0.50 * modelBInput >= 0.50
        ? 'HIGH'
        : 0.50 * modelAInput + 0.50 * modelBInput >= 0.35
        ? 'MODERATE'
        : 'LOW',
    recommended_mine_action:
      0.50 * modelAInput + 0.50 * modelBInput >= 0.70
        ? 'Immediate pit bench evacuation and crack meter telemetry dispatch required.'
        : 0.50 * modelAInput + 0.50 * modelBInput >= 0.50
        ? 'Restricted haul road transit. Geotechnical radar inspection mandated.'
        : 'Standard open-cast mining pit operations.',
    disclaimer: 'Scenario simulation only. Not a certified operational mine-safety broadcast.',
  };

  return (
    <div className="space-y-4">
      {/* 1. Institutional Secondary Sector Banner */}
      <div className="p-3.5 bg-slate-900 border border-amber-800/80 rounded flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-3">
          <Pickaxe className="w-4 h-4 text-amber-400" />
          <div>
            <strong className="font-mono tracking-wide text-amber-300 uppercase">
              JHARIA / RAJAPUR — SECONDARY MINING-SECTOR APPLICATION
            </strong>
            <span className="text-slate-500 mx-2">•</span>
            <span className="text-slate-400 font-mono text-[11px]">
              Open-Cast Coal Pit Bench Instability Assessment (Isolated from NER Training Data)
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3 font-mono text-[11px]">
          <span className="text-slate-400">
            PIT AREA: <strong className="text-slate-200">1.4503 km² (1,665 Grid Nodes)</strong>
          </span>
          <span className="text-slate-700">|</span>
          <span className="px-2 py-0.5 rounded bg-amber-950/80 text-amber-300 border border-amber-800 font-semibold">
            RESEARCH PROTOTYPE
          </span>
        </div>
      </div>

      {/* 2. Key Pit Morphometric & Benchmark Statistics */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 font-mono text-xs">
        <div className="p-3 bg-slate-900 border border-slate-800 rounded space-y-1">
          <span className="text-[10px] text-slate-500 uppercase block font-sans">Mean Susceptibility</span>
          <strong className="text-lg text-slate-200">0.3161</strong>
          <span className="text-[10px] text-slate-500 block">Pit Median: 0.2738</span>
        </div>

        <div className="p-3 bg-slate-900 border border-slate-800 rounded space-y-1">
          <span className="text-[10px] text-slate-500 uppercase block font-sans">Peak Susceptibility</span>
          <strong className="text-lg text-amber-400">0.7632</strong>
          <span className="text-[10px] text-slate-500 block">High-Wall Bench Zone</span>
        </div>

        <div className="p-3 bg-slate-900 border border-slate-800 rounded space-y-1">
          <span className="text-[10px] text-slate-500 uppercase block font-sans">High-Risk Area (≥0.60)</span>
          <strong className="text-lg text-red-400">6.01%</strong>
          <span className="text-[10px] text-slate-500 block">0.0871 km² Surface</span>
        </div>

        <div className="p-3 bg-slate-900 border border-slate-800 rounded space-y-1">
          <span className="text-[10px] text-slate-500 uppercase block font-sans">Confirmed Failure</span>
          <strong className="text-lg text-emerald-400">EVT_RAJ_007</strong>
          <span className="text-[10px] text-slate-500 block">April 2023 Rockfall</span>
        </div>
      </div>

      {/* 3. 2D Mining Risk Matrix Simulator (Model A + Model B) */}
      <div className="p-4 bg-slate-900 border border-slate-800 rounded space-y-3 font-mono text-xs">
        <div className="flex items-center justify-between border-b border-slate-800 pb-2">
          <span className="font-bold text-slate-200 flex items-center gap-2">
            <Sliders className="w-4 h-4 text-amber-400" />
            2D Mine Slope Risk Simulator (Model A Random Forest + Model B CatBoost)
          </span>
          <span className="text-[10px] px-2 py-0.5 rounded bg-slate-950 border border-slate-700 text-amber-400 font-bold">
            SCENARIO / SIMULATION
          </span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-center">
          {/* Sliders (8 Cols) */}
          <div className="lg:col-span-8 space-y-3">
            <div>
              <div className="flex justify-between text-[11px] mb-1">
                <span className="text-slate-300">Model A (Random Forest Geotechnical Terrain Index):</span>
                <strong className="text-amber-400">{modelAInput.toFixed(2)}</strong>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={modelAInput}
                onChange={(e) => {
                  const val = parseFloat(e.target.value);
                  setModelAInput(val);
                  simMutation.mutate({ geotechnical_susceptibility: val, weather_trigger_index: modelBInput });
                }}
                className="w-full h-1.5 bg-slate-950 rounded-lg appearance-none cursor-pointer accent-amber-500"
              />
            </div>

            <div>
              <div className="flex justify-between text-[11px] mb-1">
                <span className="text-slate-300">Model B (CatBoost Meteorological Operational Risk):</span>
                <strong className="text-blue-400">{modelBInput.toFixed(2)}</strong>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={modelBInput}
                onChange={(e) => {
                  const val = parseFloat(e.target.value);
                  setModelBInput(val);
                  simMutation.mutate({ geotechnical_susceptibility: modelAInput, weather_trigger_index: val });
                }}
                className="w-full h-1.5 bg-slate-950 rounded-lg appearance-none cursor-pointer accent-blue-500"
              />
            </div>
          </div>

          {/* Result Card (4 Cols) */}
          <div className="lg:col-span-4 p-3.5 bg-slate-950 border border-slate-800 rounded text-center space-y-2">
            <span className="text-[10px] text-slate-500 uppercase block font-sans">Simulated Composite Mine Index</span>
            <div className="text-2xl font-bold text-amber-400">
              {simResult.composite_mining_risk_index.toFixed(4)}
            </div>
            <div>
              <RiskBadge level={simResult.mining_risk_class as any} size="md" />
            </div>
            <p className="text-[10px] text-slate-400 font-sans mt-1">
              {simResult.recommended_mine_action}
            </p>
          </div>
        </div>
      </div>

      {/* 4. Top High-Susceptibility Pit Rankings & Historical Event Overlay Table */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Historical Events Table (6 Cols) */}
        <div className="lg:col-span-6 bg-slate-900 border border-slate-800 rounded overflow-hidden">
          <div className="px-3.5 py-2.5 border-b border-slate-800 bg-slate-950 flex items-center justify-between text-xs font-mono">
            <strong className="text-slate-200 font-medium">
              Documented Pit Instability Events Overlay
            </strong>
            <span className="text-[10px] text-slate-500">Rajapur Colliery</span>
          </div>

          <div className="overflow-x-auto max-h-56 overflow-y-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-slate-950 text-slate-500 uppercase text-[10px] border-b border-slate-800">
                <tr>
                  <th className="py-2 px-3">Event ID</th>
                  <th className="py-2 px-3">Date</th>
                  <th className="py-2 px-3">Type</th>
                  <th className="py-2 px-3 text-right">Slope</th>
                  <th className="py-2 px-3 text-right">Susceptibility</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300 text-[11px]">
                {events.map((evt: any) => (
                  <tr key={evt.event_id} className="hover:bg-slate-800/30">
                    <td className="py-2 px-3 font-bold text-slate-200">{evt.event_id}</td>
                    <td className="py-2 px-3 text-slate-400">{evt.date}</td>
                    <td className="py-2 px-3 text-slate-300">{evt.type}</td>
                    <td className="py-2 px-3 text-right text-slate-400">{evt.slope_deg?.toFixed(1)}°</td>
                    <td className="py-2 px-3 text-right text-amber-400 font-bold">
                      {evt.susceptibility_index?.toFixed(4)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Top 50 Pit Ranking Locations (6 Cols) */}
        <div className="lg:col-span-6 bg-slate-900 border border-slate-800 rounded overflow-hidden">
          <div className="px-3.5 py-2.5 border-b border-slate-800 bg-slate-950 flex items-center justify-between text-xs font-mono">
            <strong className="text-slate-200 font-medium">
              Top High-Susceptibility Pit Bench Coordinates
            </strong>
            <span className="text-[10px] text-slate-500">Model A Output</span>
          </div>

          <div className="overflow-x-auto max-h-56 overflow-y-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-slate-950 text-slate-500 uppercase text-[10px] border-b border-slate-800">
                <tr>
                  <th className="py-2 px-3">Rank</th>
                  <th className="py-2 px-3">Coordinates</th>
                  <th className="py-2 px-3 text-right">Slope Angle</th>
                  <th className="py-2 px-3 text-right">Susceptibility Index</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300 text-[11px]">
                {topPoints.slice(0, 10).map((pt: any, idx: number) => (
                  <tr key={idx} className="hover:bg-slate-800/30">
                    <td className="py-2 px-3 text-slate-500">#{idx + 1}</td>
                    <td className="py-2 px-3 text-slate-300 text-[10px]">
                      {pt.latitude?.toFixed(4)}°N, {pt.longitude?.toFixed(4)}°E
                    </td>
                    <td className="py-2 px-3 text-right text-slate-400">{pt.slope_deg?.toFixed(1)}°</td>
                    <td className="py-2 px-3 text-right text-amber-400 font-bold">
                      {pt.susceptibility_index?.toFixed(4)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
