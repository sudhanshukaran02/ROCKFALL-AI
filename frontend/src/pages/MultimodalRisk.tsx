import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchCurrentRisk, fetchFusionPredictions } from '@/services/api';
import { RiskBadge } from '@/components/common/RiskBadge';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorState } from '@/components/common/EmptyState';
import {
  Network,
  Info,
  Sliders,
} from 'lucide-react';

export const MultimodalRisk: React.FC = () => {
  const currentRiskQ = useQuery({ queryKey: ['currentRisk'], queryFn: fetchCurrentRisk });
  const fusionQ = useQuery({ queryKey: ['fusionPredictions'], queryFn: fetchFusionPredictions });

  // Interactive Scenario Simulator
  const [simE, setSimE] = useState<number>(0.40);
  const [simS, setSimS] = useState<number>(0.52);
  const [simT, setSimT] = useState<number>(0.21);

  const isLoading = currentRiskQ.isLoading || fusionQ.isLoading;
  const isError = currentRiskQ.isError || fusionQ.isError;

  if (isLoading) {
    return (
      <div className="h-96 flex items-center justify-center">
        <LoadingSpinner label="Loading Multimodal Late-Fusion Architecture & Evaluation Records..." size="lg" />
      </div>
    );
  }

  if (isError) {
    return (
      <ErrorState
        title="Multimodal Fusion Service Error"
        message="Failed to load multimodal fusion outputs from the backend integration layer."
        onRetry={() => {
          currentRiskQ.refetch();
          fusionQ.refetch();
        }}
      />
    );
  }

  const currentRisk = currentRiskQ.data;
  const simComposite = 0.25 * simE + 0.25 * simS + 0.50 * simT;

  const getWarningTier = (r: number) => {
    if (r >= 0.65) return { tier: 'CRITICAL', label: 'CRITICAL HAZARD (r ≥ 0.65)' };
    if (r >= 0.48) return { tier: 'WARNING', label: 'WARNING LEVEL (r ≥ 0.48)' };
    if (r >= 0.35) return { tier: 'WATCH', label: 'WATCH / ELEVATED (r ≥ 0.35)' };
    return { tier: 'LOW', label: 'LOW BASELINE (r < 0.35)' };
  };

  const simTier = getWarningTier(simComposite);

  return (
    <div className="space-y-4">
      {/* 1. Header Information Bar */}
      <div className="p-3.5 bg-slate-900 border border-slate-800 rounded flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-3">
          <Network className="w-4 h-4 text-blue-400" />
          <div>
            <strong className="font-mono tracking-wide text-slate-200 uppercase">
              MULTIMODAL LATE-FUSION DECISION ENGINE
            </strong>
            <span className="text-slate-500 mx-2">•</span>
            <span className="text-slate-400 font-mono text-[11px]">
              Exp D: Temporal-Focused Late Fusion (Validated)
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3 font-mono text-[11px]">
          <span className="text-slate-400">
            FUSION FORMULA: <strong className="text-slate-200">0.25E + 0.25S + 0.50T</strong>
          </span>
          <span className="text-slate-700">|</span>
          <span className="px-2 py-0.5 rounded bg-slate-950 text-emerald-400 border border-emerald-800 font-semibold">
            EQUATION FROZEN
          </span>
        </div>
      </div>

      {/* 2. Central Mathematical Formulation Panel */}
      <div className="p-4 bg-slate-900 border border-slate-800 rounded space-y-3">
        <div className="flex items-center justify-between border-b border-slate-800 pb-2">
          <span className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wide">
            Multimodal Late-Fusion Formulation
          </span>
          <span className="text-[10px] font-mono text-emerald-400 font-bold">
            ROC-AUC: 0.8682 | PR-AUC: 0.1099
          </span>
        </div>

        <div className="p-3 bg-slate-950 border border-slate-800 rounded text-center space-y-1">
          <div className="text-sm sm:text-base font-mono font-bold text-slate-100 tracking-wide">
            <span className="text-amber-400">R_multimodal</span> = (
            <span className="text-purple-400">0.25</span> × <span className="text-purple-300">E_spatial</span>) + (
            <span className="text-emerald-400">0.25</span> × <span className="text-emerald-300">S_terrain</span>) + (
            <span className="text-blue-400">0.50</span> × <span className="text-blue-300">T_temporal</span>)
          </div>
          <p className="text-[11px] text-slate-400 font-sans">
            Linearly synthesizes spatial scar evidence, topographic susceptibility, and dynamic antecedent rainfall forcing.
          </p>
        </div>

        {/* 3 Component Breakdown Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 font-mono text-xs">
          {/* Spatial Stream */}
          <div className="p-3 bg-slate-950 border border-purple-900/40 rounded space-y-1.5">
            <div className="flex justify-between items-center text-[10px] text-slate-400 uppercase font-sans">
              <span>Spatial Stream</span>
              <span className="text-purple-400 font-bold">Weight: 25%</span>
            </div>
            <div className="text-base font-bold text-purple-300">
              E_spatial = {currentRisk?.spatial_evidence?.toFixed(4) || '0.4000'}
            </div>
            <div className="text-[11px] text-slate-400 font-sans">
              4-Channel U-Net CNN segmentation of scar density and multispectral anomalies.
            </div>
            <div className="text-[10px] text-slate-500 pt-1 border-t border-slate-900">
              Contribution: {(0.25 * (currentRisk?.spatial_evidence || 0.40)).toFixed(4)}
            </div>
          </div>

          {/* Terrain Stream */}
          <div className="p-3 bg-slate-950 border border-emerald-900/40 rounded space-y-1.5">
            <div className="flex justify-between items-center text-[10px] text-slate-400 uppercase font-sans">
              <span>Terrain Stream</span>
              <span className="text-emerald-400 font-bold">Weight: 25%</span>
            </div>
            <div className="text-base font-bold text-emerald-300">
              S_terrain = {currentRisk?.terrain_susceptibility?.toFixed(4) || '0.5200'}
            </div>
            <div className="text-[11px] text-slate-400 font-sans">
              SRTM 30m morphometric baseline (Slope, Aspect, Curvature, TWI).
            </div>
            <div className="text-[10px] text-slate-500 pt-1 border-t border-slate-900">
              Contribution: {(0.25 * (currentRisk?.terrain_susceptibility || 0.52)).toFixed(4)}
            </div>
          </div>

          {/* Temporal Stream */}
          <div className="p-3 bg-slate-950 border border-blue-900/40 rounded space-y-1.5">
            <div className="flex justify-between items-center text-[10px] text-slate-400 uppercase font-sans">
              <span>Temporal Stream</span>
              <span className="text-blue-400 font-bold">Weight: 50%</span>
            </div>
            <div className="text-base font-bold text-blue-300">
              T_temporal = {currentRisk?.temporal_risk?.toFixed(4) || '0.2100'}
            </div>
            <div className="text-[11px] text-slate-400 font-sans">
              2-Layer PyTorch LSTM 30-day antecedent meteorological sequence hazard.
            </div>
            <div className="text-[10px] text-slate-500 pt-1 border-t border-slate-900">
              Contribution: {(0.50 * (currentRisk?.temporal_risk || 0.21)).toFixed(4)}
            </div>
          </div>
        </div>
      </div>

      {/* 3. Interactive Factor Sensitivity Simulator */}
      <div className="p-4 bg-slate-900 border border-slate-800 rounded space-y-3">
        <div className="flex items-center justify-between border-b border-slate-800 pb-2">
          <span className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wide flex items-center gap-1.5">
            <Sliders className="w-3.5 h-3.5 text-blue-400" />
            Interactive Stream Sensitivity Simulator (Scenario Testing)
          </span>
          <span className="text-[10px] font-mono text-slate-500">Live Mathematical Evaluation</span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-center">
          {/* Controls (8 Cols) */}
          <div className="lg:col-span-8 space-y-3 text-xs font-mono">
            {/* Spatial Slider */}
            <div className="space-y-1">
              <div className="flex justify-between text-[11px]">
                <span className="text-purple-300">Spatial Evidence (E_spatial):</span>
                <strong className="text-slate-200">{simE.toFixed(2)}</strong>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={simE}
                onChange={(e) => setSimE(parseFloat(e.target.value))}
                className="w-full h-1.5 bg-slate-950 rounded-lg appearance-none cursor-pointer accent-purple-500"
              />
            </div>

            {/* Terrain Slider */}
            <div className="space-y-1">
              <div className="flex justify-between text-[11px]">
                <span className="text-emerald-300">Terrain Susceptibility (S_terrain):</span>
                <strong className="text-slate-200">{simS.toFixed(2)}</strong>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={simS}
                onChange={(e) => setSimS(parseFloat(e.target.value))}
                className="w-full h-1.5 bg-slate-950 rounded-lg appearance-none cursor-pointer accent-emerald-500"
              />
            </div>

            {/* Temporal Slider */}
            <div className="space-y-1">
              <div className="flex justify-between text-[11px]">
                <span className="text-blue-300">Temporal Weather Risk (T_temporal):</span>
                <strong className="text-slate-200">{simT.toFixed(2)}</strong>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={simT}
                onChange={(e) => setSimT(parseFloat(e.target.value))}
                className="w-full h-1.5 bg-slate-950 rounded-lg appearance-none cursor-pointer accent-blue-500"
              />
            </div>
          </div>

          {/* Simulated Result Dock (4 Cols) */}
          <div className="lg:col-span-4 p-3.5 bg-slate-950 border border-slate-800 rounded space-y-2 text-center font-mono">
            <span className="text-[10px] text-slate-500 uppercase block font-sans">Simulated Composite Index</span>
            <div className="text-2xl font-bold text-amber-400">
              {simComposite.toFixed(4)}
            </div>
            <div className="pt-1">
              <RiskBadge level={simTier.tier as any} size="md" />
            </div>
            <p className="text-[10px] text-slate-500 font-sans mt-1">
              {simTier.label}
            </p>
          </div>
        </div>
      </div>

      {/* 4. Verified Benchmark & Calibration Table */}
      <div className="bg-slate-900 border border-slate-800 rounded overflow-hidden">
        <div className="px-3.5 py-2.5 border-b border-slate-800 bg-slate-950 flex items-center justify-between text-xs">
          <strong className="text-slate-200 font-medium">
            Multimodal Fusion Evaluation Benchmark & Calibration Metrics
          </strong>
          <span className="text-[10px] font-mono text-emerald-400">
            Unseen Regional Test Split
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-950 text-slate-500 uppercase text-[10px] border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-4">Evaluation Metric</th>
                <th className="py-2.5 px-4">Observed Value</th>
                <th className="py-2.5 px-4">Engineering Interpretation & Action</th>
                <th className="py-2.5 px-4 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300 text-[11px]">
              <tr className="hover:bg-slate-800/30">
                <td className="py-2 px-4 font-bold text-slate-200">Combined ROC-AUC Score</td>
                <td className="py-2 px-4 text-emerald-400 font-bold">0.8682</td>
                <td className="py-2 px-4 font-sans text-slate-400">Excellent discrimination between landslide trigger days and quiescent days</td>
                <td className="py-2 px-4 text-right text-emerald-400">VERIFIED</td>
              </tr>
              <tr className="hover:bg-slate-800/30">
                <td className="py-2 px-4 font-bold text-slate-200">Precision-Recall AUC (PR-AUC)</td>
                <td className="py-2 px-4 text-blue-400 font-bold">0.1099</td>
                <td className="py-2 px-4 font-sans text-slate-400">Superior to static baseline under severe 1:40 class imbalance</td>
                <td className="py-2 px-4 text-right text-emerald-400">VERIFIED</td>
              </tr>
              <tr className="hover:bg-slate-800/30">
                <td className="py-2 px-4 font-bold text-slate-200">Brier Score (Probability Calibration)</td>
                <td className="py-2 px-4 text-amber-400 font-bold">0.1652</td>
                <td className="py-2 px-4 font-sans text-slate-400">POOR calibration: Raw probabilities overestimate frequency; tuned thresholds required</td>
                <td className="py-2 px-4 text-right text-amber-400">CALIBRATION REQD</td>
              </tr>
              <tr className="hover:bg-slate-800/30">
                <td className="py-2 px-4 font-bold text-slate-200">Balanced Operating Point</td>
                <td className="py-2 px-4 text-slate-200 font-bold">r_th = 0.65</td>
                <td className="py-2 px-4 font-sans text-slate-400">F1: 0.2500 | Precision: 28.57% | Recall: 22.22% | FPR: 1.52%</td>
                <td className="py-2 px-4 text-right text-emerald-400">OPERATIONAL</td>
              </tr>
              <tr className="hover:bg-slate-800/30">
                <td className="py-2 px-4 font-bold text-slate-200">High-Sensitivity Operating Point</td>
                <td className="py-2 px-4 text-slate-200 font-bold">r_th = 0.48</td>
                <td className="py-2 px-4 font-sans text-slate-400">Recall: 100.00% (Zero missed events) | Precision: 8.18% | FPR: 30.79%</td>
                <td className="py-2 px-4 text-right text-emerald-400">OPERATIONAL</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* 5. Interpretation & Decision-Support Role */}
      <div className="p-3.5 bg-slate-900 border border-slate-800 rounded space-y-1.5 text-xs">
        <div className="flex items-center gap-2 text-slate-200 font-semibold font-mono uppercase text-[11px]">
          <Info className="w-3.5 h-3.5 text-blue-400" />
          Late-Fusion Synthesis & Decision Role
        </div>
        <p className="text-slate-400 font-sans leading-relaxed text-[11px]">
          Multimodal late fusion answers: <strong>"HOW do spatial scar evidence, terrain slope, and dynamic rainfall combine to form an actionable institutional warning signal?"</strong>. By assigning 50% weight to dynamic temporal forcing and 25% each to spatial and terrain baselines, the platform achieves robust early warning while avoiding false triggers in flat or dry terrain.
        </p>
      </div>
    </div>
  );
};
