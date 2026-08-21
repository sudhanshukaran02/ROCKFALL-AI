import React from 'react';
import { AlertTriangle, CheckCircle, Info, ShieldAlert, AlertCircle } from 'lucide-react';
import { RiskLevel } from '@/types';
import { cn } from '@/utils/cn';

interface RiskBadgeProps {
  level: RiskLevel;
  showIcon?: boolean;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({
  level,
  showIcon = true,
  className,
  size = 'md',
}) => {
  const getBadgeConfig = () => {
    switch (level) {
      case 'LOW':
        return {
          bg: 'bg-emerald-950/80 border-emerald-600 text-emerald-300',
          icon: <CheckCircle className="w-3.5 h-3.5" />,
          label: 'LOW RISK',
        };
      case 'WATCH':
      case 'MODERATE':
        return {
          bg: 'bg-amber-950/80 border-amber-500 text-amber-300',
          icon: <Info className="w-3.5 h-3.5" />,
          label: level === 'WATCH' ? 'WATCH / ELEVATED' : 'MODERATE RISK',
        };
      case 'WARNING':
      case 'HIGH':
        return {
          bg: 'bg-orange-950/80 border-orange-500 text-orange-300',
          icon: <AlertTriangle className="w-3.5 h-3.5" />,
          label: level === 'WARNING' ? 'WARNING LEVEL' : 'HIGH RISK',
        };
      case 'CRITICAL':
        return {
          bg: 'bg-red-950/90 border-red-500 text-red-200 animate-pulse',
          icon: <ShieldAlert className="w-3.5 h-3.5" />,
          label: 'CRITICAL RISK',
        };
      default:
        return {
          bg: 'bg-slate-800 border-slate-600 text-slate-300',
          icon: <AlertCircle className="w-3.5 h-3.5" />,
          label: String(level),
        };
    }
  };

  const { bg, icon, label } = getBadgeConfig();

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs gap-1',
    md: 'px-2.5 py-1 text-xs gap-1.5 font-semibold',
    lg: 'px-3.5 py-1.5 text-sm gap-2 font-bold',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-md border tracking-wide uppercase',
        bg,
        sizeClasses[size],
        className
      )}
    >
      {showIcon && icon}
      <span>{label}</span>
    </span>
  );
};
