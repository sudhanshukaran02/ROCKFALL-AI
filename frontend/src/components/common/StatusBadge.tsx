import React from 'react';
import { DataStatus } from '@/types';
import { cn } from '@/utils/cn';

interface StatusBadgeProps {
  status: DataStatus | string;
  className?: string;
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  className,
  size = 'md',
}) => {
  const getStyle = () => {
    switch (status) {
      case 'LIVE':
        return 'bg-emerald-950/70 border-emerald-500/60 text-emerald-300';
      case 'VERIFIED':
        return 'bg-blue-950/70 border-blue-500/60 text-blue-300';
      case 'HISTORICAL':
        return 'bg-slate-800/80 border-slate-600 text-slate-300';
      case 'MODEL OUTPUT':
        return 'bg-purple-950/70 border-purple-500/60 text-purple-300';
      case 'PROTOTYPE':
        return 'bg-amber-950/70 border-amber-500/60 text-amber-300';
      case 'DEMO DATA':
      case 'SIMULATED DATA':
        return 'bg-cyan-950/70 border-cyan-500/60 text-cyan-300';
      case 'NOT CONNECTED':
      case 'UNAVAILABLE':
      default:
        return 'bg-slate-800/60 border-slate-700 text-slate-400';
    }
  };

  const sizeClasses = {
    sm: 'px-1.5 py-0.5 text-[10px]',
    md: 'px-2 py-0.5 text-xs',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center font-mono font-medium rounded border uppercase tracking-wider',
        getStyle(),
        sizeClasses[size],
        className
      )}
    >
      {status}
    </span>
  );
};
