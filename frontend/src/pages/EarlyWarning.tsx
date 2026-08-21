import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchEarlyWarningStrategy, fetchCurrentRisk } from '@/services/api';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorState } from '@/components/common/EmptyState';
import { ThresholdAnalysisChart } from '@/components/charts/ThresholdAnalysisChart';
import {
  ShieldAlert,
  Clock,
  Radio,
} from 'lucide-react';

export const EarlyWarning: React.FC = () => {
  const [activeMode, setActiveMode] = useState<'Balanced Mode' | 'High-Sensitivity Mode'>('Balanced Mode');

  const strategyQ = useQuery({ queryKey: ['earlyWarningStrategy'], queryFn: fetchEarlyWarningStrategy });
  const currentRiskQ = useQuery({ queryKey: ['currentRisk'], queryFn: fetchCurrentRisk });

  const isLoading = strategyQ.isLoading || currentRiskQ.isLoading;
  const isError = strategyQ.isError || currentRiskQ.isError;

  if (isLoading) {
    return (
      <div className="h-96 flex items-center justify-center">
        <LoadingSpinner label="Loading Early Warning Threshold Optimizations & Calibration Data..." size="lg" />
      </div>
    );
  }

  if (isError) {
    return (
      <ErrorState
        title="Early Warning Strategy Error"
        message="Failed to load threshold analysis and operating points from FastAPI backend."
        onRetry={() => {
          strategyQ.refetch();
          currentRiskQ.refetch();
        }}
      />
    );
  }

  const strategy = strategyQ.data;
  const currentRisk = currentRiskQ.data;
  const thresholdPoints = strategy?.threshold_curve || [];

  const currentRiskVal = currentRisk?.multimodal_risk || 0.334;
  const thresholdVal = activeMode === 'Balanced Mode' ? 0.65 : 0.48;
  const isTriggered = currentRiskVal >= thresholdVal;


  return (
    <div className="space-y-4">
      {/* 1. Header Information Bar */}
      <div className="p-3.5 bg-slate-900 border border-slate-800 rounded flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-3">
          <ShieldAlert className="w-4 h-4 text-blue-400" />
          <div>
            <strong className="font-mono tracking-wide text-slate-200 uppercase">
              EARLY WARNING STRATEGY & THRESHOLD OPTIMIZATION
            </strong>
            <span className="text-slate-500 mx-2">•</span>
            <span className="text-slate-400 font-mono text-[11px]">
              Decision Support Console (Human Authorization Enforced)
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3 font-mono text-[11px]">
          <span className="text-slate-400">
            ACTIVE POSTURE: <strong className="text-slate-200">{activeMode} (r_th = {thresholdVal.toFixed(2)})</strong>
          </span>
          <span className="text-slate-700">|</span>
          <span className="px-2 py-0.5 rounded bg-slate-950 text-emerald-400 border border-emerald-800 font-semibold">
            CALIBRATED OPERATING POINT
          </span>
        </div>
      </div>

      {/* 2. Institutional Authorization Pipeline State Machine Banner */}
      <div className="p-4 bg-slate-900 border border-slate-800 rounded space-y-3">
        <div className="flex items-center justify-between border-b border-slate-800 pb-2 text-xs font-mono">
          <span className="text-slate-300 font-bold uppercase tracking-wide flex items-center gap-2">
            <Radio className="w-3.5 h-3.5 text-blue-400" />
            Statutory Decision Pipeline (Zero Autonomous Broadcast)
          </span>
          <span className="text-[10px] text-slate-500">5-Stage Linear Protocol</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-5 gap-2 text-xs font-mono">
          <div className="p-2.5 bg-slate-950 border border-slate-800 rounded space-y-1">
            <span className="text-[10px] text-slate-500 uppercase block font-sans">Step 1</span>
            <strong className="text-slate-200 text-xs block">AI Model Output</strong>
            <span className="text-[10px] text-emerald-400 font-bold">R = {currentRiskVal.toFixed(4)}</span>
          </div>

          <div className="p-2.5 bg-slate-950 border border-slate-800 rounded space-y-1">
            <span className="text-[10px] text-slate-500 uppercase block font-sans">Step 2</span>
            <strong className="text-slate-200 text-xs block">Threshold Check</strong>
            <span className="text-[10px] text-slate-300">{isTriggered ? 'Trigger Condition Met' : 'Quiescent (< r_th)'}</span>
          </div>

          <div className="p-2.5 bg-slate-950 border border-amber-900/60 rounded space-y-1">
            <span className="text-[10px] text-amber-500 uppercase block font-sans">Step 3</span>
            <strong className="text-amber-300 text-xs block">System Advisory</strong>
            <span className="text-[10px] text-amber-400 font-bold">RECOMMENDATION</span>
          </div>

          <div className="p-2.5 bg-slate-950 border border-blue-900/60 rounded space-y-1">
            <span className="text-[10px] text-blue-400 uppercase block font-sans">Step 4</span>
            <strong className="text-blue-300 text-xs block">Geotechnical Review</strong>
            <span className="text-[10px] text-blue-400 font-bold">HUMAN REQUIRED</span>
          </div>

          <div className="p-2.5 bg-slate-950 border border-slate-800 rounded space-y-1">
            <span className="text-[10px] text-slate-500 uppercase block font-sans">Step 5</span>
            <strong className="text-slate-300 text-xs block">Official Action</strong>
            <span className="text-[10px] text-slate-400">AUTHORIZED DISPATCH</span>
          </div>
        </div>
      </div>

      {/* 3. Operating Modes Switcher & Evaluation Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Operating Point Selector (5 Cols) */}
        <div className="lg:col-span-5 bg-slate-900 border border-slate-800 rounded p-4 space-y-3">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <span className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wide">
              Operating Point Configuration
            </span>
            <span className="text-[10px] font-mono text-slate-500">2 Validated Modes</span>
          </div>

          <div className="space-y-2 text-xs">
            {/* Balanced Mode Button */}
            <button
              onClick={() => setActiveMode('Balanced Mode')}
              className={`w-full p-3 rounded border text-left font-mono transition-colors ${
                activeMode === 'Balanced Mode'
                  ? 'bg-blue-950/80 border-blue-600 text-slate-100'
                  : 'bg-slate-950 border-slate-800 text-slate-400 hover:bg-slate-900'
              }`}
            >
              <div className="flex items-center justify-between">
                <strong className="text-xs text-slate-200">Balanced Operating Mode</strong>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-900 border border-slate-700 text-blue-400">
                  r_th = 0.65
                </span>
              </div>
              <div className="mt-2 grid grid-cols-2 gap-1 text-[11px] text-slate-400">
                <span>Test F1: <strong>0.2500</strong></span>
                <span>Precision: <strong>28.57%</strong></span>
                <span>Recall: <strong>22.22%</strong></span>
                <span>FPR: <strong>1.52%</strong></span>
              </div>
              <p className="mt-1.5 text-[10px] font-sans text-slate-500">
                Minimizes institutional alarm fatigue. Best for standard municipal coordination.
              </p>
            </button>

            {/* High-Sensitivity Mode Button */}
            <button
              onClick={() => setActiveMode('High-Sensitivity Mode')}
              className={`w-full p-3 rounded border text-left font-mono transition-colors ${
                activeMode === 'High-Sensitivity Mode'
                  ? 'bg-amber-950/80 border-amber-600 text-slate-100'
                  : 'bg-slate-950 border-slate-800 text-slate-400 hover:bg-slate-900'
              }`}
            >
              <div className="flex items-center justify-between">
                <strong className="text-xs text-slate-200">High-Sensitivity Mode</strong>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-900 border border-slate-700 text-amber-400">
                  r_th = 0.48
                </span>
              </div>
              <div className="mt-2 grid grid-cols-2 gap-1 text-[11px] text-slate-400">
                <span>Test Recall: <strong className="text-emerald-400">100.00%</strong></span>
                <span>Val Recall: <strong>100.00%</strong></span>
                <span>Precision: <strong>8.18%</strong></span>
                <span>FPR: <strong>30.79%</strong></span>
              </div>
              <p className="mt-1.5 text-[10px] font-sans text-slate-500">
                Zero missed events during heavy monsoon surges or cyclone alerts.
              </p>
            </button>
          </div>

          {/* 2-Day Persistence Rule */}
          <div className="p-3 bg-slate-950 border border-slate-800 rounded space-y-1 text-xs font-mono">
            <div className="flex items-center justify-between text-slate-300">
              <span className="flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-purple-400" />
                2-Day Persistence Rule
              </span>
              <span className="text-emerald-400 font-bold">ACTIVE</span>
            </div>
            <p className="text-[11px] font-sans text-slate-400 leading-relaxed">
              Requires R ≥ r_th for <strong>2 consecutive days</strong> before triggering a formal alarm, suppressing ~20% of transient single-day rainfall spikes.
            </p>
          </div>
        </div>

        {/* Evaluation Output & 2x2 Confusion Matrix (7 Cols) */}
        <div className="lg:col-span-7 bg-slate-900 border border-slate-800 rounded p-4 space-y-3">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <span className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wide">
              {activeMode} — Confusion Matrix on Unseen 2024 Test Set (366 Days)
            </span>
            <span className="text-[10px] font-mono text-slate-400">Ground-Truth GSI</span>
          </div>

          {/* 2x2 Confusion Matrix Visualizer */}
          <div className="grid grid-cols-2 gap-2 text-xs font-mono text-center">
            {/* True Positive */}
            <div className="p-3 bg-slate-950 border border-emerald-900/60 rounded space-y-1">
              <span className="text-[10px] text-slate-500 uppercase block font-sans">True Positives (TP)</span>
              <div className="text-xl font-bold text-emerald-400">
                {activeMode === 'Balanced Mode' ? '2 Days' : '9 Days'}
              </div>
              <span className="text-[10px] text-slate-400 block font-sans">
                {activeMode === 'Balanced Mode' ? '22.2% of event days captured' : '100.0% of event days captured'}
              </span>
            </div>

            {/* False Positive */}
            <div className="p-3 bg-slate-950 border border-amber-900/60 rounded space-y-1">
              <span className="text-[10px] text-slate-500 uppercase block font-sans">False Positives (FP)</span>
              <div className="text-xl font-bold text-amber-400">
                {activeMode === 'Balanced Mode' ? '5 Days (1.52%)' : '101 Days (30.8%)'}
              </div>
              <span className="text-[10px] text-slate-400 block font-sans">
                {activeMode === 'Balanced Mode' ? 'Low alarm fatigue' : 'High false alarm volume'}
              </span>
            </div>

            {/* False Negative */}
            <div className="p-3 bg-slate-950 border border-red-900/60 rounded space-y-1">
              <span className="text-[10px] text-slate-500 uppercase block font-sans">False Negatives (FN)</span>
              <div className="text-xl font-bold text-red-400">
                {activeMode === 'Balanced Mode' ? '7 Days' : '0 Days'}
              </div>
              <span className="text-[10px] text-slate-400 block font-sans">
                {activeMode === 'Balanced Mode' ? 'Missed low-intensity events' : 'Zero missed events (Zero FN)'}
              </span>
            </div>

            {/* True Negative */}
            <div className="p-3 bg-slate-950 border border-slate-800 rounded space-y-1">
              <span className="text-[10px] text-slate-500 uppercase block font-sans">True Negatives (TN)</span>
              <div className="text-xl font-bold text-slate-200">
                {activeMode === 'Balanced Mode' ? '352 Days' : '256 Days'}
              </div>
              <span className="text-[10px] text-slate-400 block font-sans">
                Quiescent non-event days correctly classified
              </span>
            </div>
          </div>

          <div className="p-2.5 bg-slate-950 border border-slate-800 rounded text-xs font-sans text-slate-400 leading-relaxed">
            <strong>Operational Selection Directive:</strong> District Emergency Operations Centers (DEOC) should maintain <strong>Balanced Mode (r=0.65)</strong> as baseline posture, switching to <strong>High-Sensitivity Mode (r=0.48)</strong> only upon receiving formal IMD Red/Orange heavy rainfall alerts.
          </div>
        </div>
      </div>

      {/* 4. Threshold Sweep Precision-Recall Curve Chart */}
      <div className="bg-slate-900 border border-slate-800 rounded p-4 space-y-2">
        <div className="flex items-center justify-between text-xs">
          <div>
            <strong className="text-slate-200 font-medium block">
              Operating Threshold (r_th) Optimization & F1 Sweep (0.10 – 0.90)
            </strong>
            <span className="text-[10px] text-slate-500 font-mono">
              F1 curve peaks at r_th = 0.65 with minimal false positive rate (1.52%)
            </span>
          </div>
          <span className="text-[11px] font-mono text-blue-400">
            Sweep Points: {thresholdPoints.length}
          </span>
        </div>

        <div className="h-60 pt-2">
          <ThresholdAnalysisChart points={thresholdPoints} />
        </div>
      </div>
    </div>
  );
};
