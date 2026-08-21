import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchFusionPredictions } from '@/services/api';
import { Card } from '@/components/common/Card';
import { MetricCard } from '@/components/common/MetricCard';
import { RiskBadge } from '@/components/common/RiskBadge';
import { StatusBadge } from '@/components/common/StatusBadge';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorState } from '@/components/common/EmptyState';
import { RiskLevel } from '@/types';
import {
  Layers,
  Activity,
  Cpu,
  ShieldAlert,
  Sliders,
  Sparkles,
} from 'lucide-react';

export const MultimodalFusion: React.FC = () => {
  // Interactive Simulator State (allowing officers to simulate scenarios)
  const [simSpatial, setSimSpatial] = useState<number>(0.40);
  const [simTerrain, setSimTerrain] = useState<number>(0.52);
  const [simTemporal, setSimTemporal] = useState<number>(0.452);

  // Multimodal late-fusion weights (0.25, 0.25, 0.50)
  const simR = 0.25 * simSpatial + 0.25 * simTerrain + 0.50 * simTemporal;
  const getSimLevel = (r: number): RiskLevel => {
    if (r >= 0.70) return 'CRITICAL';
    if (r >= 0.50) return 'WARNING';
    if (r >= 0.35) return 'WATCH';
    return 'LOW';
  };

  const fusionQ = useQuery({ queryKey: ['fusionPredictions'], queryFn: fetchFusionPredictions });

  const isLoading = fusionQ.isLoading;
  const isError = fusionQ.isError;

  if (isLoading) {
    return (
      <div className="h-96 flex items-center justify-center">
        <LoadingSpinner label="Loading Multimodal Late-Fusion Model Metrics..." size="lg" />
      </div>
    );
  }

  if (isError) {
    return (
      <ErrorState
        title="Fusion Engine Error"
        message="Failed to load multimodal fusion records from FastAPI adapter."
        onRetry={() => fusionQ.refetch()}
      />
    );
  }

  const fusionData = fusionQ.data;
  const records = fusionData?.records || [];

  return (
    <div className="space-y-6">
      {/* 1. Header Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-lg p-5 flex flex-wrap items-center justify-between gap-4 shadow-card">
        <div>
          <div className="flex flex-wrap items-center gap-3">
            <h2 className="text-xl font-bold text-slate-100 tracking-tight flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-amber-400" />
              Multimodal Late-Fusion Decision Engine
            </h2>
            <StatusBadge status="MODEL OUTPUT" size="sm" />
          </div>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            Validated Formula: <strong className="text-amber-300">R = 0.25·E_spatial + 0.25·S_terrain + 0.50·T_temporal</strong>
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs bg-blue-950/80 text-blue-300 border border-blue-800 px-3 py-1.5 rounded flex items-center gap-1.5 font-medium">
            <Activity className="w-3.5 h-3.5 text-blue-400" />
            Validation-Tuned Weights
          </span>
        </div>
      </div>

      {/* 2. Key Metrics Ribbon */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <MetricCard
          title="Multimodal Test ROC-AUC"
          value={fusionData?.test_roc_auc ? fusionData.test_roc_auc.toFixed(4) : '0.8682'}
          subtitle="Class Discrimination"
          status="VERIFIED"
          variant="accent"
          icon={<Activity className="w-5 h-5 text-emerald-400" />}
        />
        <MetricCard
          title="Multimodal Test PR-AUC"
          value={fusionData?.test_pr_auc ? fusionData.test_pr_auc.toFixed(4) : '0.1099'}
          subtitle="Precision-Recall Area"
          status="VERIFIED"
          icon={<Cpu className="w-5 h-5 text-blue-400" />}
        />
        <MetricCard
          title="Brier Score (Calibration)"
          value="0.1652"
          subtitle="Uncalibrated Probability"
          status="HISTORICAL"
          icon={<ShieldAlert className="w-5 h-5 text-amber-400" />}
        />
        <MetricCard
          title="Dynamic Weather Weight"
          value="50.0%"
          subtitle="Dominant Trigger Modality"
          status="VERIFIED"
          icon={<Layers className="w-5 h-5 text-purple-400" />}
        />
        <MetricCard
          title="Spatial / Terrain Weights"
          value="25% / 25%"
          subtitle="Equal Morphological Prior"
          status="VERIFIED"
          icon={<Layers className="w-5 h-5 text-slate-400" />}
        />
      </div>

      {/* 3. Main Grid: Interactive Scenario Simulator & Modality Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Interactive Scenario Simulator (7 Cols) */}
        <div className="lg:col-span-7">
          <Card
            title="Interactive Multimodal Scenario Simulator"
            subtitle="Test hypothetical spatial, terrain, and temporal risk combinations in real-time"
            badge={<Sliders className="w-4 h-4 text-amber-400" />}
          >
            <div className="space-y-5 text-xs">
              {/* Output Decision Card */}
              <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 flex flex-wrap items-center justify-between gap-4">
                <div>
                  <span className="text-[10px] uppercase font-semibold text-slate-400 block mb-1">
                    Simulated Multimodal Risk Index (R)
                  </span>
                  <div className="flex items-center gap-3">
                    <span className="text-2xl font-mono font-bold text-amber-400">
                      {simR.toFixed(4)}
                    </span>
                    <RiskBadge level={getSimLevel(simR)} size="md" />
                  </div>
                </div>
                <div className="text-right text-[11px] text-slate-400 font-mono">
                  <div>0.25 × {simSpatial.toFixed(2)} = {(0.25 * simSpatial).toFixed(3)} (E)</div>
                  <div>0.25 × {simTerrain.toFixed(2)} = {(0.25 * simTerrain).toFixed(3)} (S)</div>
                  <div>0.50 × {simTemporal.toFixed(2)} = {(0.50 * simTemporal).toFixed(3)} (T)</div>
                </div>
              </div>

              {/* Slider 1: Temporal Weather (T) */}
              <div className="p-3 rounded bg-slate-950/70 border border-slate-800 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-blue-300">
                    1. Temporal Weather Risk (T_temporal) — 50% Weight
                  </span>
                  <span className="font-mono text-sm text-blue-300 font-bold">{simTemporal.toFixed(3)}</span>
                </div>
                <input
                  type="range"
                  min="0.0"
                  max="1.0"
                  step="0.01"
                  value={simTemporal}
                  onChange={(e) => setSimTemporal(parseFloat(e.target.value))}
                  className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-[10px] text-slate-400">
                  <span>Dry Season (0.05)</span>
                  <span>Moderate Rainfall (0.45)</span>
                  <span>Acute Monsoon (0.90)</span>
                </div>
              </div>

              {/* Slider 2: Terrain Susceptibility (S) */}
              <div className="p-3 rounded bg-slate-950/70 border border-slate-800 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-emerald-300">
                    2. Terrain Susceptibility (S_terrain) — 25% Weight
                  </span>
                  <span className="font-mono text-sm text-emerald-300 font-bold">{simTerrain.toFixed(3)}</span>
                </div>
                <input
                  type="range"
                  min="0.0"
                  max="1.0"
                  step="0.01"
                  value={simTerrain}
                  onChange={(e) => setSimTerrain(parseFloat(e.target.value))}
                  className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-[10px] text-slate-400">
                  <span>Flat Valley (0.15)</span>
                  <span>NER Mean Slope (0.52)</span>
                  <span>Escarpment (0.85)</span>
                </div>
              </div>

              {/* Slider 3: Spatial Evidence (E) */}
              <div className="p-3 rounded bg-slate-950/70 border border-slate-800 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-purple-300">
                    3. Spatial Evidence (E_spatial) — 25% Weight
                  </span>
                  <span className="font-mono text-sm text-purple-300 font-bold">{simSpatial.toFixed(3)}</span>
                </div>
                <input
                  type="range"
                  min="0.0"
                  max="1.0"
                  step="0.01"
                  value={simSpatial}
                  onChange={(e) => setSimSpatial(parseFloat(e.target.value))}
                  className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-[10px] text-slate-400">
                  <span>Undisturbed Forest (0.05)</span>
                  <span>Sparse Scar (0.40)</span>
                  <span>Fresh Failure (0.90)</span>
                </div>
              </div>
            </div>
          </Card>
        </div>

        {/* Right: Validation Rationale & Historical Sample Table (5 Cols) */}
        <div className="lg:col-span-5 flex flex-col gap-6">
          <Card
            title="Weight Optimization Rationale"
            subtitle="Why dynamic weather dominates static/spatial factors"
            badge={<StatusBadge status="VERIFIED" size="sm" />}
          >
            <div className="space-y-3 text-xs text-slate-300 leading-relaxed">
              <div className="p-3 rounded bg-slate-950 border border-slate-800 space-y-1.5">
                <span className="font-semibold text-slate-200 block text-xs uppercase tracking-wider">
                  Empirical Validation Tuning
                </span>
                <p className="text-[11px] text-slate-400">
                  Validation grid search established that giving 50% weight to continuous weather sequences maximizes early-warning lead time while reducing false alarms from static slope features.
                </p>
              </div>

              <div className="p-3 rounded bg-amber-950/30 border border-amber-900/50 space-y-1.5">
                <span className="font-semibold text-amber-300 flex items-center gap-1.5 text-xs">
                  <ShieldAlert className="w-3.5 h-3.5 text-amber-400" /> Uncalibrated Probability Reminder
                </span>
                <p className="text-[11px] text-amber-200/90">
                  Brier score of <strong>0.1652</strong> indicates raw output probabilities tend to overestimate true event frequency. Therefore, decisions must rely on optimized threshold tiers rather than treating raw values as absolute odds.
                </p>
              </div>
            </div>
          </Card>

          {/* Historical Multimodal Predictions Table */}
          <Card
            title="2024 Historical Fusion Records"
            subtitle="Sample test days from multimodal test evaluation"
            badge={<StatusBadge status="MODEL OUTPUT" size="sm" />}
          >
            <div className="overflow-x-auto max-h-[220px] overflow-y-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-950/80 text-slate-400 border-b border-slate-800 uppercase text-[10px] sticky top-0">
                  <tr>
                    <th className="py-2 px-2.5">Date</th>
                    <th className="py-2 px-2.5 text-right">E (25%)</th>
                    <th className="py-2 px-2.5 text-right">S (25%)</th>
                    <th className="py-2 px-2.5 text-right">T (50%)</th>
                    <th className="py-2 px-2.5 text-right">R (Total)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-slate-300 font-mono text-[11px]">
                  {records.slice(0, 6).map((rec, idx) => (
                    <tr key={idx} className="hover:bg-slate-800/30">
                      <td className="py-2 px-2.5 text-slate-400">{rec.date}</td>
                      <td className="py-2 px-2.5 text-right text-purple-300">{rec.e_spatial.toFixed(2)}</td>
                      <td className="py-2 px-2.5 text-right text-emerald-300">{rec.s_terrain.toFixed(2)}</td>
                      <td className="py-2 px-2.5 text-right text-blue-300">{rec.t_temporal.toFixed(2)}</td>
                      <td className="py-2 px-2.5 text-right font-bold text-amber-400">
                        {rec.r_multimodal.toFixed(4)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};
