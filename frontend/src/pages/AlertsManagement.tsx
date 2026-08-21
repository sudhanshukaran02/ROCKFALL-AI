import React from 'react';
import { Card } from '@/components/common/Card';
import { StatusBadge } from '@/components/common/StatusBadge';
import { BellRing } from 'lucide-react';

export const AlertsManagement: React.FC = () => {
  return (
    <div className="space-y-6">
      <Card
        title="Decision-Support Alert Management"
        subtitle="Human authorization workflow: Model Recommendation → Analyst Review → Authorized Warning"
        action={<StatusBadge status="PROTOTYPE" size="sm" />}
      >
        <div className="p-6 rounded-lg bg-slate-950/60 border border-slate-800 text-center text-slate-400">
          <BellRing className="w-10 h-10 text-amber-400 mx-auto mb-2" />
          <h4 className="text-sm font-semibold text-slate-200">Alert Authorizing Workflow Ready</h4>
          <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
            Strict human-in-the-loop workflow prevents autonomous public dissemination.
          </p>
        </div>
      </Card>
    </div>
  );
};
