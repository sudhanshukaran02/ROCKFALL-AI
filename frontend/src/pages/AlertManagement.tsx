import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchAlerts, authorizeAlert } from '@/services/api';
import { StatusBadge } from '@/components/common/StatusBadge';
import { RiskBadge } from '@/components/common/RiskBadge';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorState } from '@/components/common/EmptyState';
import {
  BellRing,
  UserCheck,
  CheckCircle,
  XCircle,
  Radio,
  FileCheck,
} from 'lucide-react';
import { EarlyWarningAlert } from '@/types';

export const AlertManagement: React.FC = () => {
  const queryClient = useQueryClient();

  const [selectedAlertId, setSelectedAlertId] = useState<string | null>(null);
  const [authorizerName, setAuthorizerName] = useState<string>('District Geotechnical Officer');
  const [reviewerNotes, setReviewerNotes] = useState<string>('Ground inspection matches elevated rainfall hazard. Dispatched patrol unit.');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');

  const alertsQ = useQuery({
    queryKey: ['activeAlerts'],
    queryFn: fetchAlerts,
  });

  const authMutation = useMutation({
    mutationFn: authorizeAlert,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['activeAlerts'] });
      setSelectedAlertId(null);
    },
  });

  if (alertsQ.isLoading) {
    return (
      <div className="h-96 flex items-center justify-center">
        <LoadingSpinner label="Loading Early Warning Advisory Queue & Human Authorization Gateway..." size="lg" />
      </div>
    );
  }

  if (alertsQ.isError) {
    return (
      <ErrorState
        title="Alert Management Error"
        message="Failed to load active system alerts from FastAPI backend."
        onRetry={() => alertsQ.refetch()}
      />
    );
  }

  const alerts: EarlyWarningAlert[] = alertsQ.data?.alerts || [];
  const filteredAlerts = alerts.filter((a) => {
    if (statusFilter === 'ALL') return true;
    return a.status === statusFilter;
  });

  return (
    <div className="space-y-4">
      {/* 1. Institutional Ops Sub-Header Bar */}
      <div className="p-3.5 bg-slate-900 border border-slate-800 rounded flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-3">
          <BellRing className="w-4 h-4 text-blue-400" />
          <div>
            <strong className="font-mono tracking-wide text-slate-200 uppercase">
              ALERT MANAGEMENT & STATUTORY AUTHORIZATION WORKSPACE
            </strong>
            <span className="text-slate-500 mx-2">•</span>
            <span className="text-slate-400 font-mono text-[11px]">
              Human-in-the-Loop Dissemination Gateway
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3 font-mono text-[11px]">
          <span className="text-slate-400">
            TOTAL ADVISORIES: <strong className="text-slate-200">{alerts.length} In Queue</strong>
          </span>
          <span className="text-slate-700">|</span>
          <span className="px-2 py-0.5 rounded bg-slate-950 text-amber-400 border border-amber-800 font-semibold">
            HUMAN SIGN-OFF MANDATORY
          </span>
        </div>
      </div>

      {/* 2. Institutional Authorization Pipeline Bar */}
      <div className="p-3 bg-slate-900 border border-slate-800 rounded flex flex-wrap items-center justify-between gap-2 text-xs font-mono">
        <div className="flex items-center gap-2 text-slate-300">
          <Radio className="w-3.5 h-3.5 text-blue-400" />
          <strong className="uppercase">Operational State Machine:</strong>
          <span className="text-slate-400 text-[11px]">
            Model Signal → Recommendation → Human Review → Authorized Action
          </span>
        </div>

        <div className="flex items-center gap-1 text-[11px]">
          {['ALL', 'MODEL_RECOMMENDATION', 'HUMAN_REVIEW', 'AUTHORIZED', 'REJECTED'].map((filter) => (
            <button
              key={filter}
              onClick={() => setStatusFilter(filter)}
              className={`px-2 py-0.5 rounded border text-[10px] uppercase transition-colors ${
                statusFilter === filter
                  ? 'bg-blue-950 text-blue-300 border-blue-700 font-bold'
                  : 'bg-slate-950 text-slate-400 border-slate-800 hover:bg-slate-800'
              }`}
            >
              {filter.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {/* 3. Primary Authorization Workflow Table */}
      <div className="bg-slate-900 border border-slate-800 rounded overflow-hidden">
        <div className="px-3.5 py-2.5 border-b border-slate-800 bg-slate-950 flex items-center justify-between text-xs">
          <strong className="text-slate-200 font-medium flex items-center gap-2">
            <FileCheck className="w-4 h-4 text-emerald-400" />
            Active Warning Advisories & Authorization Table
          </strong>
          <span className="text-[10px] font-mono text-slate-500">
            {filteredAlerts.length} Matching Records
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-950 text-slate-500 uppercase text-[10px] border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-4">Alert ID</th>
                <th className="py-2.5 px-4">Date / Reference</th>
                <th className="py-2.5 px-4">Target Location</th>
                <th className="py-2.5 px-4">Assessed Risk</th>
                <th className="py-2.5 px-4">Evidence Source</th>
                <th className="py-2.5 px-4 text-center">Protocol Status</th>
                <th className="py-2.5 px-4">Assigned Officer</th>
                <th className="py-2.5 px-4 text-right">Statutory Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300 text-[11px]">
              {filteredAlerts.map((alt) => {
                const isSelected = selectedAlertId === alt.alert_id;
                return (
                  <tr key={alt.alert_id} className={`hover:bg-slate-800/30 ${isSelected ? 'bg-blue-950/20' : ''}`}>
                    <td className="py-2.5 px-4 font-bold text-slate-200">{alt.alert_id}</td>
                    <td className="py-2.5 px-4 text-slate-400">{alt.timestamp?.slice(0, 10)}</td>
                    <td className="py-2.5 px-4 font-sans text-slate-200">
                      <span className="font-semibold block">{alt.location || 'Regional Hazard Corridor'}</span>
                      <span className="text-[10px] text-slate-500 font-mono">
                        Threshold: {alt.selected_threshold?.toFixed(2) || '0.65'} | Risk: {alt.current_risk?.toFixed(4) || '0.7200'}
                      </span>
                    </td>
                    <td className="py-2.5 px-4">
                      <RiskBadge level={alt.warning_level} size="sm" />
                    </td>
                    <td className="py-2.5 px-4 text-slate-400 text-[10px]">
                      {alt.trigger_source || 'Late Fusion Exp D'}
                    </td>
                    <td className="py-2.5 px-4 text-center">
                      <StatusBadge status={alt.status} size="sm" />
                    </td>
                    <td className="py-2.5 px-4 text-slate-400 font-sans text-[11px]">
                      {alt.authorized_by || 'Awaiting Officer Review'}
                    </td>
                    <td className="py-2.5 px-4 text-right">
                      {alt.status === 'AUTHORIZED' ? (
                        <span className="text-emerald-400 font-bold text-[10px] flex items-center justify-end gap-1">
                          <CheckCircle className="w-3 h-3" /> AUTHORIZED
                        </span>
                      ) : alt.status === 'REJECTED' ? (
                        <span className="text-slate-500 font-bold text-[10px] flex items-center justify-end gap-1">
                          <XCircle className="w-3 h-3" /> REJECTED
                        </span>
                      ) : (
                        <div className="flex items-center justify-end gap-1">
                          <button
                            onClick={() => setSelectedAlertId(isSelected ? null : alt.alert_id)}
                            className="px-2 py-0.5 rounded bg-blue-950 hover:bg-blue-900 text-blue-300 border border-blue-800 text-[10px] transition-colors"
                          >
                            {isSelected ? 'Close' : 'Review'}
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* 4. Active Authorization Review Drawer (Appears when Review is clicked) */}
      {selectedAlertId && (
        <div className="p-4 bg-slate-900 border border-blue-800 rounded space-y-3 font-mono text-xs">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <span className="font-bold text-slate-200 flex items-center gap-2">
              <UserCheck className="w-4 h-4 text-blue-400" />
              Statutory Authorization Console — {selectedAlertId}
            </span>
            <span className="text-[10px] text-slate-400">Formal Verification Record</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div>
              <label className="block text-[10px] text-slate-500 uppercase mb-1">Authorizing Officer</label>
              <input
                type="text"
                value={authorizerName}
                onChange={(e) => setAuthorizerName(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-slate-200 text-xs focus:border-blue-600 focus:outline-none"
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-[10px] text-slate-500 uppercase mb-1">Reviewer Technical Notes</label>
              <input
                type="text"
                value={reviewerNotes}
                onChange={(e) => setReviewerNotes(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-slate-200 text-xs focus:border-blue-600 focus:outline-none font-sans"
              />
            </div>
          </div>

          <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-800">
            <button
              onClick={() => setSelectedAlertId(null)}
              className="px-3 py-1 rounded bg-slate-950 hover:bg-slate-800 text-slate-400 border border-slate-800 text-xs"
            >
              Cancel
            </button>
            <button
              onClick={() =>
                authMutation.mutate({
                  alert_id: selectedAlertId,
                  new_status: 'REJECTED',
                  authorizer_name: authorizerName,
                  reviewer_notes: reviewerNotes,
                })
              }
              disabled={authMutation.isPending}
              className="px-3 py-1 rounded bg-red-950 hover:bg-red-900 text-red-300 border border-red-800 text-xs font-bold"
            >
              Reject Advisory
            </button>
            <button
              onClick={() =>
                authMutation.mutate({
                  alert_id: selectedAlertId,
                  new_status: 'AUTHORIZED',
                  authorizer_name: authorizerName,
                  reviewer_notes: reviewerNotes,
                })
              }
              disabled={authMutation.isPending}
              className="px-3 py-1 rounded bg-emerald-950 hover:bg-emerald-900 text-emerald-300 border border-emerald-800 text-xs font-bold flex items-center gap-1.5"
            >
              <CheckCircle className="w-3.5 h-3.5" />
              <span>Authorize Official Civil Defense Action</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
