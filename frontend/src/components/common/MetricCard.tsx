import React from 'react';
import { cn } from '@/utils/cn';
import { StatusBadge } from './StatusBadge';
import { DataStatus } from '@/types';

interface MetricCardProps {
  title: string;
  value: string | number;
  unit?: string;
  subtitle?: string;
  status?: DataStatus | string;
  trend?: string;
  icon?: React.ReactNode;
  variant?: 'default' | 'accent' | 'warning' | 'danger';
  className?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  unit,
  subtitle,
  status,
  trend,
  icon,
  variant = 'default',
  className,
}) => {
  const getBorder = () => {
    switch (variant) {
      case 'accent':
        return 'border-blue-700/50 bg-slate-900/90';
      case 'warning':
        return 'border-amber-700/50 bg-slate-900/90';
      case 'danger':
        return 'border-red-700/50 bg-slate-900/90';
      default:
        return 'border-slate-800 bg-slate-900/80';
    }
  };

  return (
    <div
      className={cn(
        'p-4 rounded-lg border backdrop-blur-sm shadow-card flex flex-col justify-between transition-all hover:border-slate-700',
        getBorder(),
        className
      )}
    >
      <div className="flex items-start justify-between gap-2 mb-2">
        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
          {title}
        </span>
        {icon && <div className="text-slate-400 shrink-0">{icon}</div>}
      </div>

      <div className="flex items-baseline gap-1.5 my-1">
        <span className="text-2xl lg:text-3xl font-bold font-mono text-slate-100 tracking-tight">
          {value}
        </span>
        {unit && <span className="text-sm font-medium text-slate-400">{unit}</span>}
      </div>

      <div className="flex items-center justify-between gap-2 mt-2 pt-2 border-t border-slate-800/80 text-xs text-slate-400">
        <span className="truncate">{subtitle || trend || 'Verified Benchmark'}</span>
        {status && <StatusBadge status={status} size="sm" />}
      </div>
    </div>
  );
};
