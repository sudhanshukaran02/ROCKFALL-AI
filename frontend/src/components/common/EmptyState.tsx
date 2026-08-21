import React from 'react';
import { Database, AlertCircle } from 'lucide-react';
import { cn } from '@/utils/cn';

interface EmptyStateProps {
  title?: string;
  description?: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title = 'No Data Available',
  description = 'No records matched the selected filters or the data source is currently unconnected.',
  icon,
  action,
  className,
}) => {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center p-8 text-center rounded-lg border border-dashed border-slate-800 bg-slate-900/40',
        className
      )}
    >
      <div className="p-3 rounded-full bg-slate-800 text-slate-400 mb-3">
        {icon || <Database className="w-6 h-6" />}
      </div>
      <h4 className="text-sm font-semibold text-slate-200 mb-1">{title}</h4>
      <p className="text-xs text-slate-400 max-w-md mb-4">{description}</p>
      {action}
    </div>
  );
};

interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
  className?: string;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Data Loading Error',
  message = 'Failed to fetch data from the integration layer.',
  onRetry,
  className,
}) => {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center p-6 text-center rounded-lg border border-red-900/50 bg-red-950/20 text-red-300',
        className
      )}
    >
      <AlertCircle className="w-8 h-8 text-red-400 mb-2" />
      <h4 className="text-sm font-semibold text-red-200 mb-1">{title}</h4>
      <p className="text-xs text-red-300/80 max-w-md mb-3">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-3 py-1 bg-red-900/80 hover:bg-red-800 text-red-100 text-xs rounded border border-red-700 transition-colors"
        >
          Retry Request
        </button>
      )}
    </div>
  );
};
