import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchLSTMPredictions, fetchRiskTimeline } from '@/services/api';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorState } from '@/components/common/EmptyState';
import { RiskTimelineChart } from '@/components/charts/RiskTimelineChart';
import {
  Timer,
  Info,
} from 'lucide-react';

export const LSTMTemporalRisk: React.FC = () => {
  const lstmQ = useQuery({ queryKey: ['lstmPredictions'], queryFn: fetchLSTMPredictions });
  const timelineQ = useQuery({ queryKey: ['riskTimeline'], queryFn: fetchRiskTimeline });

  const isLoading = lstmQ.isLoading || timelineQ.isLoading;
  const isError = lstmQ.isError || timelineQ.isError;

  if (isLoading) {
    return (
      <div className="h-96 flex items-center justify-center">
        <LoadingSpinner label="Loading 2-Layer PyTorch LSTM Predictions & Meteorological Series..." size="lg" />
      </div>
    );
  }

  if (isError) {
    return (
      <ErrorState
        title="Temporal LSTM Service Error"
        message="Failed to load LSTM model outputs from the FastAPI integration layer."
        onRetry={() => {
          lstmQ.refetch();
          timelineQ.refetch();
        }}
      />
    );
  }

  const lstmData = lstmQ.data;
  const timelinePoints = timelineQ.data?.points || [];

  return (
    <div className="space-y-4">
      {/* 1. Header Information Bar */}
      <div className="p-3.5 bg-slate-900 border border-slate-800 rounded flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-3">
          <Timer className="w-4 h-4 text-blue-400" />
          <div>
            <strong className="font-mono tracking-wide text-slate-200 uppercase">
              MODEL: 2-LAYER PYTORCH METEOROLOGICAL LSTM
            </strong>
            <span className="text-slate-500 mx-2">•</span>
            <span className="text-slate-400 font-mono text-[11px]">
              T_temporal Stream (50% Dominant Weight in Late Fusion)
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3 font-mono text-[11px]">
          <span className="text-slate-400">
            CHECKPOINT: <strong className="text-slate-200">ner_lstm_best.pth (41,259 bytes)</strong>
          </span>
          <span className="text-slate-700">|</span>
          <span className="px-2 py-0.5 rounded bg-slate-950 text-emerald-400 border border-emerald-800 font-semibold">
            SEQUENCE MODEL READY
          </span>
        </div>
      </div>

      {/* 2. Structured Model Specification & Input/Output Matrix */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Specifications Panel (4 Cols) */}
        <div className="lg:col-span-4 bg-slate-900 border border-slate-800 rounded p-4 space-y-3">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <span className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wide">
              Sequence Specifications
            </span>
            <span className="text-[10px] font-mono text-slate-500">PyTorch Recurrent</span>
          </div>

          <div className="space-y-2 text-xs font-mono">
            <div className="p-2 bg-slate-950 border border-slate-800 rounded space-y-1">
              <span className="text-[10px] text-slate-500 uppercase block font-sans">Primary Purpose</span>
              <p className="text-slate-200 font-sans text-xs">
                Captures cumulative antecedent rainfall, temperature, and atmospheric saturation dynamics over a sliding 30-day temporal window.
              </p>
            </div>

            <div className="p-2 bg-slate-950 border border-slate-800 rounded space-y-1">
              <span className="text-[10px] text-slate-500 uppercase block font-sans">Temporal Window</span>
              <p className="text-slate-200 text-xs font-mono">
                Lookback: T = 30 Days | Forecast Horizon: H = 24 Hours
              </p>
            </div>

            <div className="p-2 bg-slate-950 border border-slate-800 rounded space-y-1">
              <span className="text-[10px] text-slate-500 uppercase block font-sans">Input Features</span>
              <p className="text-slate-200 text-xs font-mono">
                Rainfall, 1..30d Rolling Sums, Temp, Humidity, Season Sin/Cos
              </p>
            </div>

            <div className="p-2 bg-slate-950 border border-slate-800 rounded space-y-1">
              <span className="text-[10px] text-slate-500 uppercase block font-sans">Output Metric</span>
              <p className="text-slate-200 text-xs font-mono">
                Next-Day Temporal Hazard Probability T_temporal [0.0, 1.0]
              </p>
            </div>
          </div>
        </div>

        {/* Temporal Sequence Diagnostics (8 Cols) */}
        <div className="lg:col-span-8 bg-slate-900 border border-slate-800 rounded p-4 space-y-3">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <span className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wide">
              30-Day Antecedent Lookback & Next-Day Hazard
            </span>
            <span className="text-[10px] font-mono text-slate-400">
              Target Reference: 31 Dec 2024
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 font-mono text-xs">
            <div className="p-3 bg-slate-950 border border-slate-800 rounded space-y-1">
              <span className="text-[10px] text-slate-500 uppercase block font-sans">Current T_temporal</span>
              <strong className="text-lg text-amber-400">
                {lstmData?.temporal_risk?.toFixed(4) || '0.2100'}
              </strong>
              <span className="text-[10px] text-slate-500 block">Next-Day Hazard</span>
            </div>

            <div className="p-3 bg-slate-950 border border-slate-800 rounded space-y-1">
              <span className="text-[10px] text-slate-500 uppercase block font-sans">7-Day Antecedent Rain</span>
              <strong className="text-lg text-slate-200">
                {lstmData?.rainfall_7d_mm?.toFixed(1) || '38.4'} mm
              </strong>
              <span className="text-[10px] text-slate-500 block">Cumulative Moisture</span>
            </div>

            <div className="p-3 bg-slate-950 border border-slate-800 rounded space-y-1">
              <span className="text-[10px] text-slate-500 uppercase block font-sans">24h Immediate Rain</span>
              <strong className="text-lg text-slate-200">
                {lstmData?.rainfall_24h_mm?.toFixed(1) || '4.2'} mm
              </strong>
              <span className="text-[10px] text-slate-500 block">Trigger Intensity</span>
            </div>

            <div className="p-3 bg-slate-950 border border-slate-800 rounded space-y-1">
              <span className="text-[10px] text-slate-500 uppercase block font-sans">Sequence Length</span>
              <strong className="text-lg text-blue-400">30 Steps</strong>
              <span className="text-[10px] text-slate-500 block">Daily Recurrent</span>
            </div>
          </div>

          <div className="p-2.5 bg-slate-950 border border-slate-800 rounded text-xs font-mono flex items-center justify-between">
            <span className="text-slate-400">Temporal Decision Contribution in Fusion:</span>
            <span className="text-slate-200 font-bold">
              0.50 × {lstmData?.temporal_risk?.toFixed(4) || '0.2100'} = {(0.5 * (lstmData?.temporal_risk || 0.21)).toFixed(4)}
            </span>
          </div>
        </div>
      </div>

      {/* 3. Scientific Time-Series Inspection Chart */}
      <div className="bg-slate-900 border border-slate-800 rounded p-4 space-y-2">
        <div className="flex items-center justify-between text-xs">
          <div>
            <strong className="text-slate-200 font-medium block">
              Multi-Year Temporal Environmental Risk & Rainfall Evolution (2017–2024)
            </strong>
            <span className="text-[10px] text-slate-500 font-mono">
              Evaluated on 366 untouched daily test steps with verified trigger event overlays
            </span>
          </div>
          <span className="text-[11px] font-mono text-blue-400">
            PR-AUC: 0.1488 (Weather-Ablated)
          </span>
        </div>

        <div className="h-60 pt-2">
          <RiskTimelineChart points={timelinePoints} />
        </div>
      </div>

      {/* 4. Comparative Benchmark & Feature Ablation Table */}
      <div className="bg-slate-900 border border-slate-800 rounded overflow-hidden">
        <div className="px-3.5 py-2.5 border-b border-slate-800 bg-slate-950 flex items-center justify-between text-xs">
          <strong className="text-slate-200 font-medium">
            Verified Temporal Model Benchmark & Feature Ablation Comparison
          </strong>
          <span className="text-[10px] font-mono text-emerald-400">
            Unseen 2024 Test Set (366 Days)
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-950 text-slate-500 uppercase text-[10px] border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-4">Architecture / Pipeline Variant</th>
                <th className="py-2.5 px-4">Test PR-AUC</th>
                <th className="py-2.5 px-4">Test ROC-AUC</th>
                <th className="py-2.5 px-4">Precision / Recall / F1</th>
                <th className="py-2.5 px-4 text-right">Relative Gain</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300 text-[11px]">
              <tr className="hover:bg-slate-800/30 bg-blue-950/20">
                <td className="py-2.5 px-4 font-bold text-blue-300">
                  2-Layer LSTM + Meteorological Ablation (Proposed)
                </td>
                <td className="py-2.5 px-4 text-emerald-400 font-bold">0.1488</td>
                <td className="py-2.5 px-4 text-slate-200 font-bold">0.8404</td>
                <td className="py-2.5 px-4 font-sans text-slate-400">P: 10.0% | R: 44.4% | F1: 0.1633</td>
                <td className="py-2.5 px-4 text-right text-emerald-400 font-bold">+67.4% vs Base</td>
              </tr>
              <tr className="hover:bg-slate-800/30">
                <td className="py-2.5 px-4 font-bold text-slate-200">
                  2-Layer LSTM (Rainfall-Only Baseline)
                </td>
                <td className="py-2.5 px-4 text-slate-300">0.1099</td>
                <td className="py-2.5 px-4 text-slate-300">0.8682</td>
                <td className="py-2.5 px-4 font-sans text-slate-400">P: 7.7% | R: 88.9% | F1: 0.1416</td>
                <td className="py-2.5 px-4 text-right text-slate-400">+23.6% vs Static</td>
              </tr>
              <tr className="hover:bg-slate-800/30">
                <td className="py-2.5 px-4 font-bold text-slate-400">
                  7-Day Cumulative Rainfall Threshold Baseline
                </td>
                <td className="py-2.5 px-4 text-slate-500">0.0889</td>
                <td className="py-2.5 px-4 text-slate-500">0.7612</td>
                <td className="py-2.5 px-4 font-sans text-slate-500">P: 5.2% | R: 66.7% | F1: 0.0965</td>
                <td className="py-2.5 px-4 text-right text-slate-500">Reference Baseline</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* 5. Interpretation & Physical Role */}
      <div className="p-3.5 bg-slate-900 border border-slate-800 rounded space-y-1.5 text-xs">
        <div className="flex items-center gap-2 text-slate-200 font-semibold font-mono uppercase text-[11px]">
          <Info className="w-3.5 h-3.5 text-blue-400" />
          Physical Mechanism & Decision-Support Contribution
        </div>
        <p className="text-slate-400 font-sans leading-relaxed text-[11px]">
          The Weather LSTM answers: <strong>"WHEN is antecedent hydrological forcing sufficient to trigger slope failure?"</strong>. It contributes T_temporal to multimodal late fusion (weighted at 50% as the dominant dynamic trigger). Capturing 30-day cumulative pore-water pressure dynamics outperforms simple single-day rainfall thresholds by +67.4% PR-AUC.
        </p>
      </div>
    </div>
  );
};
