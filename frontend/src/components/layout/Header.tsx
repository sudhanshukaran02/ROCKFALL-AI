import React from 'react';
import { Mountain, Clock, Activity, AlertCircle } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { fetchSystemHealth } from '@/services/api';
import { StatusBadge } from '../common/StatusBadge';

export const Header: React.FC = () => {
  const { data: health, isLoading } = useQuery({
    queryKey: ['systemHealth'],
    queryFn: fetchSystemHealth,
    refetchInterval: 30000,
  });

  return (
    <header className="h-16 bg-slate-950 border-b border-slate-800 px-4 lg:px-6 flex items-center justify-between z-30 sticky top-0">
      {/* Brand & System Title */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-blue-900/60 border border-blue-600/50 flex items-center justify-center text-blue-400 font-bold text-lg shadow-inner">
          <Mountain className="w-5 h-5" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="font-bold text-base md:text-lg tracking-tight text-white flex items-center gap-2">
              NER-LENS
              <span className="text-[11px] font-mono px-1.5 py-0.2 bg-blue-950 text-blue-300 rounded border border-blue-800">
                {health?.version || 'v1.0-PROTOTYPE'}
              </span>
            </h1>
          </div>
          <p className="text-[11px] text-slate-400 hidden sm:block">
            North Eastern Region Landslide Early Warning & Risk Monitoring System
          </p>
        </div>
      </div>

      {/* Institutional Metadata & System Health */}
      <div className="flex items-center gap-3">
        <div className="hidden lg:flex items-center gap-2 px-3 py-1 rounded bg-slate-900 border border-slate-800 text-xs text-slate-300">
          <Clock className="w-3.5 h-3.5 text-slate-400" />
          <span>Latest Historical Data: <strong>{health?.latest_data_date || '2024-12-31'}</strong></span>
        </div>

        <div className="hidden md:flex items-center gap-2 px-3 py-1 rounded bg-slate-900 border border-slate-800 text-xs">
          {isLoading ? (
            <Activity className="w-3.5 h-3.5 text-amber-400 animate-pulse" />
          ) : health?.status === 'ONLINE' ? (
            <Activity className="w-3.5 h-3.5 text-emerald-400" />
          ) : (
            <AlertCircle className="w-3.5 h-3.5 text-red-400" />
          )}
          <span className="text-slate-400">Decision Engine:</span>
          <span className="text-emerald-400 font-medium font-mono">
            {health?.status || 'ONLINE'}
          </span>
        </div>

        <div className="flex items-center gap-2">
          <StatusBadge status="PROTOTYPE" size="sm" />
          <div className="hidden sm:block">
            <StatusBadge status="HISTORICAL" size="sm" />
          </div>
        </div>
      </div>
    </header>
  );
};
