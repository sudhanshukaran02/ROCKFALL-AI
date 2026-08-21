import React from 'react';
import { cn } from '@/utils/cn';

interface CardProps {
  title?: string;
  subtitle?: string;
  badge?: React.ReactNode;
  action?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  bodyClassName?: string;
}

export const Card: React.FC<CardProps> = ({
  title,
  subtitle,
  badge,
  action,
  children,
  className,
  bodyClassName,
}) => {
  return (
    <div
      className={cn(
        'bg-slate-900/90 border border-slate-800 rounded-lg shadow-card overflow-hidden',
        className
      )}
    >
      {(title || subtitle || badge || action) && (
        <div className="px-5 py-3.5 border-b border-slate-800 flex flex-wrap items-center justify-between gap-3 bg-slate-950/40">
          <div>
            {title && (
              <h3 className="text-sm md:text-base font-semibold text-slate-100 flex items-center gap-2">
                {title}
                {badge && <span className="ml-1">{badge}</span>}
              </h3>
            )}
            {subtitle && <p className="text-xs text-slate-400 mt-0.5">{subtitle}</p>}
          </div>
          {action && <div className="flex items-center gap-2">{action}</div>}
        </div>
      )}
      <div className={cn('p-5', bodyClassName)}>{children}</div>
    </div>
  );
};
