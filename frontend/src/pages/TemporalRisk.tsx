import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchRiskTimeline, fetchWeatherHistory } from '@/services/api';
import { Card } from '@/components/common/Card';
import { MetricCard } from '@/components/common/MetricCard';
import { StatusBadge } from '@/components/common/StatusBadge';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorState } from '@/components/common/EmptyState';
import { RiskTimelineChart } from '@/components/charts/RiskTimelineChart';
import {
  CloudRain,
  Activity,
  Cpu,
  Calendar,
  Info,
  CheckCircle,
} from 'lucide-react';

export const TemporalRisk: React.FC = () => {
  const timelineQ = useQuery({ queryKey: ['riskTimeline'], queryFn: fetchRiskTimeline });
  const weatherQ = useQuery({ queryKey: ['weatherHistory'], queryFn: () => fetchWeatherHistory(100) });

  const isLoading = timelineQ.isLoading || weatherQ.isLoading;
  const isError = timelineQ.isError || weatherQ.isError;

  if (isLoading) {
    return (
      <div className="h-96 flex items-center justify-center">
        <LoadingSpinner label="Loading PyTorch LSTM Temporal Weather Predictions..." size="lg" />
      </div>
    );
  }

  if (isError) {
    return (
      <ErrorState
        title="Temporal Risk Service Error"
        message="Failed to load 2024 temporal risk predictions from FastAPI adapter."
        onRetry={() => {
          timelineQ.refetch();
          weatherQ.refetch();
        }}
      />
    );
  }

  const timelinePoints = timelineQ.data?.points || [];
  const weatherRecords = weatherQ.data?.records || [];

  return (
    <div className="space-y-6">
      {/* 1. Header Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-lg p-5 flex flex-wrap items-center justify-between gap-4 shadow-card">
        <div>
          <div className="flex flex-wrap items-center gap-3">
            <h2 className="text-xl font-bold text-slate-100 tracking-tight flex items-center gap-2">
              <CloudRain className="w-5 h-5 text-blue-400" />
              Temporal Environmental Risk — 2-Layer PyTorch LSTM
            </h2>
            <StatusBadge status="MODEL OUTPUT" size="sm" />
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Modality: <strong>Dynamic Weather Triggering (T_temporal)</strong> | Checkpoint:{' '}
            <code className="font-mono text-blue-300">models/ner_lstm_best.pth</code> (41.3 KB)
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs bg-emerald-950/80 text-emerald-300 border border-emerald-800 px-3 py-1.5 rounded flex items-center gap-1.5 font-medium">
            <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
            PyTorch Sequence Model Loaded
          </span>
        </div>
      </div>

      {/* 2. Key Metrics Ribbon */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <MetricCard
          title="Test ROC-AUC"
          value="0.8682"
          subtitle="Strong Class Discrimination"
          status="VERIFIED"
          variant="accent"
          icon={<Activity className="w-5 h-5 text-emerald-400" />}
        />
        <MetricCard
          title="Weather PR-AUC (Ablation)"
          value="0.1488"
          subtitle="Top Performing Modality"
          status="VERIFIED"
          icon={<CloudRain className="w-5 h-5 text-blue-400" />}
        />
        <MetricCard
          title="Lookback Window (T)"
          value="30 Days"
          subtitle="Continuous Daily Sequence"
          status="HISTORICAL"
          icon={<Calendar className="w-5 h-5 text-purple-400" />}
        />
        <MetricCard
          title="Forecast Horizon (H)"
          value="24 Hours"
          subtitle="Next-Day Landslide Probability"
          status="MODEL OUTPUT"
          icon={<Cpu className="w-5 h-5 text-amber-400" />}
        />
        <MetricCard
          title="Test Recall / F1"
          value="55.6% / 0.17"
          subtitle="Extreme 1:40 Class Imbalance"
          status="VERIFIED"
          icon={<CheckCircle className="w-5 h-5 text-slate-400" />}
        />
      </div>

      {/* 3. 2024 Continuous Risk Timeline Chart */}
      <Card
        title="2024 Continuous Temporal Risk Evaluation Timeline"
        subtitle="366 continuous test sequence days evaluated on untouched 2024 test split"
        badge={<StatusBadge status="HISTORICAL / MODEL OUTPUT" size="sm" />}
      >
        <RiskTimelineChart points={timelinePoints} height={340} />

        <div className="mt-4 pt-3 border-t border-slate-800 flex flex-wrap items-center justify-between gap-3 text-xs text-slate-400">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1.5">
              <span className="w-3 h-0.5 bg-amber-500 inline-block"></span>
              Multimodal Risk (R)
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-3 h-0.5 border-b-2 border-dashed border-sky-400 inline-block"></span>
              Temporal Weather Risk (T)
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-3 h-0.5 border-b-2 border-dashed border-orange-500 inline-block"></span>
              Balanced Threshold (0.65)
            </span>
          </div>
          <span className="font-mono text-[11px]">366 Daily Sequence Points</span>
        </div>
      </Card>

      {/* 4. Sequence Lookback Mechanics & Weather Records Table */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Sequence Architecture Diagnostics (5 Cols) */}
        <div className="lg:col-span-5">
          <Card
            title="30-Day Lookback Sequence Mechanics"
            subtitle="Deep recurrent feature ingestion pipeline"
            badge={<StatusBadge status="VERIFIED" size="sm" />}
          >
            <div className="space-y-3 text-xs">
              <div className="p-3 rounded bg-slate-950 border border-slate-800 font-mono text-[11px] space-y-2">
                <div className="flex justify-between border-b border-slate-900 pb-1">
                  <span className="text-slate-400">Model Structure:</span>
                  <strong className="text-slate-200">2-Layer PyTorch LSTM</strong>
                </div>
                <div className="flex justify-between border-b border-slate-900 pb-1">
                  <span className="text-slate-400">Hidden Units:</span>
                  <strong className="text-slate-200">64 Per Layer</strong>
                </div>
                <div className="flex justify-between border-b border-slate-900 pb-1">
                  <span className="text-slate-400">Recurrent Dropout:</span>
                  <strong className="text-slate-200">0.30</strong>
                </div>
                <div className="flex justify-between border-b border-slate-900 pb-1">
                  <span className="text-slate-400">Input Channels:</span>
                  <strong className="text-slate-200">Precipitation, Soil Moisture, Temp</strong>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Target Horizon:</span>
                  <strong className="text-slate-200">24-Hour Landslide Event Occurred</strong>
                </div>
              </div>

              <div className="p-3 rounded bg-blue-950/30 border border-blue-900/50 text-slate-300 space-y-1.5 leading-relaxed">
                <span className="font-semibold text-blue-300 flex items-center gap-1.5 text-xs">
                  <Info className="w-3.5 h-3.5" /> Physical Hydrological Rationale
                </span>
                <p className="text-[11px]">
                  Landslides in steep North Eastern terrain rarely occur from isolated rainfall bursts; rather, multi-week antecedent saturation progressively weakens cohesive soil strength, until acute convective precipitation triggers shear failure. The 30-day LSTM lookback explicitly models this antecedent memory.
                </p>
              </div>
            </div>
          </Card>
        </div>

        {/* Recent Weather Records Sample (7 Cols) */}
        <div className="lg:col-span-7">
          <Card
            title="Precipitation & Soil Moisture Dynamics"
            subtitle="Historical meteorological inputs ingested into the LSTM lookback window"
            badge={<StatusBadge status="HISTORICAL" size="sm" />}
          >
            <div className="overflow-x-auto max-h-[300px] overflow-y-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-950/80 text-slate-400 border-b border-slate-800 uppercase text-[10px] sticky top-0">
                  <tr>
                    <th className="py-2 px-2.5">Date</th>
                    <th className="py-2 px-2.5 text-right">Rain (mm)</th>
                    <th className="py-2 px-2.5 text-right">Rain 7d (mm)</th>
                    <th className="py-2 px-2.5 text-right">Soil Moisture</th>
                    <th className="py-2 px-2.5 text-right">Temp (°C)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-slate-300 font-mono text-[11px]">
                  {weatherRecords.slice(0, 8).map((rec: any, idx: number) => (
                    <tr key={idx} className="hover:bg-slate-800/30">
                      <td className="py-2 px-2.5 text-slate-400">{rec.date}</td>
                      <td className="py-2 px-2.5 text-right text-blue-300 font-bold">
                        {Number(rec.rainfall_mm || 0).toFixed(1)}
                      </td>
                      <td className="py-2 px-2.5 text-right text-cyan-300 font-bold">
                        {Number(rec.rainfall_7d_mm || 0).toFixed(1)}
                      </td>
                      <td className="py-2 px-2.5 text-right text-purple-300">
                        {Number(rec.soil_moisture || 0).toFixed(3)}
                      </td>
                      <td className="py-2 px-2.5 text-right text-slate-300">
                        {Number(rec.temperature_c || 0).toFixed(1)}
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
