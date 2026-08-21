import React from 'react';
import { ShieldAlert, Info } from 'lucide-react';
import { cn } from '@/utils/cn';

interface NoticeBannerProps {
  type?: 'prototype' | 'safety' | 'info';
  title?: string;
  message?: string;
  className?: string;
}

export const NoticeBanner: React.FC<NoticeBannerProps> = ({
  type = 'prototype',
  title = 'RESEARCH DECISION-SUPPORT PROTOTYPE',
  message = 'This system provides multimodal AI-derived decision support signals for research investigation. It is NOT an autonomous public disaster warning system and requires human technical review prior to any operational advisory dissemination.',
  className,
}) => {
  const isSafety = type === 'safety' || type === 'prototype';

  return (
    <div
      className={cn(
        'w-full border-b px-4 py-2.5 flex items-start sm:items-center gap-3 text-xs md:text-sm font-medium',
        isSafety
          ? 'bg-amber-950/40 border-amber-800/60 text-amber-200'
          : 'bg-blue-950/40 border-blue-800/60 text-blue-200',
        className
      )}
      role="alert"
    >
      <div className="p-1 rounded bg-amber-900/50 text-amber-400 shrink-0">
        {isSafety ? <ShieldAlert className="w-4 h-4" /> : <Info className="w-4 h-4" />}
      </div>
      <div className="flex-1 leading-relaxed">
        <strong className="font-semibold uppercase tracking-wider text-amber-300 mr-2">
          {title}:
        </strong>
        <span className="text-amber-200/90">{message}</span>
      </div>
    </div>
  );
};
