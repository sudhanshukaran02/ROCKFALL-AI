import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchFutureIntegrations, generateMultilingualAdvisory } from '@/services/api';
import { StatusBadge } from '@/components/common/StatusBadge';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorState } from '@/components/common/EmptyState';
import {
  Activity,
  Globe,
  FileCode,
} from 'lucide-react';
import { IntegrationBoundaryItem } from '@/types';

export const FutureIntegrations: React.FC = () => {
  const [selectedLanguage, setSelectedLanguage] = useState<string>('en');
  const [activeTab, setActiveTab] = useState<string>('BOUND_IMD_WEATHER');

  const integrationsQ = useQuery({
    queryKey: ['futureIntegrations'],
    queryFn: fetchFutureIntegrations,
  });

  const multilingualQ = useQuery({
    queryKey: ['multilingualAdvisory'],
    queryFn: () =>
      generateMultilingualAdvisory({
        alert_id: 'ALT-CAP-2026-08',
        risk_level: 'HIGH',
        location_name: 'NH-6 Sonapur Tunnel Corridor, East Jaintia Hills, Meghalaya',
        recommended_action:
          'Suspend heavy commercial transit along NH-6. Deploy SDRF rapid response teams and activate local village disaster management committees.',
      }),
  });

  const isLoading = integrationsQ.isLoading || multilingualQ.isLoading;
  const isError = integrationsQ.isError || multilingualQ.isError;

  if (isLoading) {
    return (
      <div className="h-96 flex items-center justify-center">
        <LoadingSpinner label="Loading Future Integration Boundaries & Boundary Contracts..." size="lg" />
      </div>
    );
  }

  if (isError) {
    return (
      <ErrorState
        title="Integration Architecture Error"
        message="Failed to load future integration contracts and multilingual advisory schemas from FastAPI backend."
        onRetry={() => {
          integrationsQ.refetch();
          multilingualQ.refetch();
        }}
      />
    );
  }

  const data = integrationsQ.data;
  const boundaries: IntegrationBoundaryItem[] = data?.boundaries || [];
  const translations = multilingualQ.data?.languages || {};

  const currentBoundary = boundaries.find((b) => b.boundary_id === activeTab) || boundaries[0];
  const currentTranslation = translations[selectedLanguage] || translations['en'];

  return (
    <div className="space-y-4">
      {/* 1. Institutional Ops Sub-Header Bar */}
      <div className="p-3.5 bg-slate-900 border border-slate-800 rounded flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-3">
          <Activity className="w-4 h-4 text-blue-400" />
          <div>
            <strong className="font-mono tracking-wide text-slate-200 uppercase">
              FUTURE INTEGRATION BOUNDARIES & SYSTEM CONNECTIVITY MATRIX
            </strong>
            <span className="text-slate-500 mx-2">•</span>
            <span className="text-slate-400 font-mono text-[11px]">
              Decoupled Provider Contracts & Ingestion Pipelines
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3 font-mono text-[11px]">
          <span className="text-slate-400">
            CONTRACTS: <strong className="text-slate-200">6 Defined Interfaces</strong>
          </span>
          <span className="text-slate-700">|</span>
          <span className="px-2 py-0.5 rounded bg-slate-950 text-blue-400 border border-blue-900 font-semibold">
            ARCHITECTURE READY
          </span>
        </div>
      </div>

      {/* 2. Primary Integration Matrix Table */}
      <div className="bg-slate-900 border border-slate-800 rounded overflow-hidden">
        <div className="px-3.5 py-2.5 border-b border-slate-800 bg-slate-950 flex items-center justify-between text-xs font-mono">
          <strong className="text-slate-200 font-medium">
            1. External Source Ingestion & Boundary Matrix
          </strong>
          <span className="text-[10px] text-slate-500">6 Major Data Boundaries</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-950 text-slate-500 uppercase text-[10px] border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-4">Source System</th>
                <th className="py-2.5 px-4">Operational Purpose</th>
                <th className="py-2.5 px-4">Standard Interface Protocol</th>
                <th className="py-2.5 px-4">Current Connection Status</th>
                <th className="py-2.5 px-4">Fallback Mechanism</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300 text-[11px]">
              {boundaries.map((b) => (
                <tr
                  key={b.boundary_id}
                  onClick={() => setActiveTab(b.boundary_id)}
                  className={`hover:bg-slate-800/30 cursor-pointer ${
                    activeTab === b.boundary_id ? 'bg-blue-950/25' : ''
                  }`}
                >
                  <td className="py-2.5 px-4 font-bold text-slate-200 font-sans">
                    {b.provider_name}
                  </td>
                  <td className="py-2.5 px-4 text-slate-400 font-sans text-[11px]">
                    {b.purpose}
                  </td>
                  <td className="py-2.5 px-4 text-blue-300 font-mono text-[10px]">
                    {b.category} ({b.ingestion_protocol})
                  </td>
                  <td className="py-2.5 px-4">
                    <StatusBadge status={b.status} size="sm" />
                  </td>
                  <td className="py-2.5 px-4 text-slate-400 font-sans text-[10px]">
                    {b.status === 'NOT CONNECTED' ? 'NASA POWER Daily Climatology' : 'Local SQLite / Cache'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 3. Selected Boundary Technical Contract Specification */}
      {currentBoundary && (
        <div className="p-4 bg-slate-900 border border-slate-800 rounded space-y-3 font-mono text-xs">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <span className="font-bold text-slate-200 flex items-center gap-2">
              <FileCode className="w-4 h-4 text-blue-400" />
              Technical Interface Contract: {currentBoundary.provider_name}
            </span>
            <StatusBadge status={currentBoundary.status} size="sm" />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div className="p-2.5 bg-slate-950 border border-slate-800 rounded space-y-1">
              <span className="text-[10px] text-slate-500 uppercase block font-sans">Category / Boundary ID</span>
              <strong className="text-slate-200 text-xs block">{currentBoundary.category}</strong>
              <span className="text-[10px] text-slate-400">{currentBoundary.boundary_id}</span>
            </div>

            <div className="p-2.5 bg-slate-950 border border-slate-800 rounded space-y-1">
              <span className="text-[10px] text-slate-500 uppercase block font-sans">Protocol Specification</span>
              <strong className="text-slate-200 text-xs block">{currentBoundary.ingestion_protocol}</strong>
              <span className="text-[10px] text-slate-400">Strict Schema Validation</span>
            </div>

            <div className="p-2.5 bg-slate-950 border border-slate-800 rounded space-y-1">
              <span className="text-[10px] text-slate-500 uppercase block font-sans">Expected Schema Fields</span>
              <strong className="text-slate-200 text-xs block">{currentBoundary.expected_schema_fields?.length || 0} Fields Defined</strong>
              <span className="text-[10px] text-slate-400 truncate block">{currentBoundary.expected_schema_fields?.slice(0, 3).join(', ')}...</span>
            </div>
          </div>

          <div>
            <span className="text-[10px] text-slate-500 uppercase block mb-1">Operational Integration Notes:</span>
            <p className="p-3 bg-slate-950 border border-slate-800 rounded text-[11px] text-blue-300 overflow-x-auto leading-relaxed font-sans">
              {currentBoundary.operational_notes || 'Decoupled provider interface adapter contract.'}
            </p>
          </div>
        </div>
      )}

      {/* 4. Multilingual CAP 1.2 Emergency Advisory Generator */}
      <div className="p-4 bg-slate-900 border border-slate-800 rounded space-y-3 font-mono text-xs">
        <div className="flex items-center justify-between border-b border-slate-800 pb-2">
          <span className="font-bold text-slate-200 flex items-center gap-2">
            <Globe className="w-4 h-4 text-blue-400" />
            2. Multilingual Common Alerting Protocol (CAP 1.2) Generator
          </span>
          <span className="text-[10px] text-slate-400">8 North Eastern Regional Languages</span>
        </div>

        {/* Language Tabs */}
        <div className="flex flex-wrap gap-1">
          {[
            { code: 'en', name: 'English' },
            { code: 'as', name: 'অসমীয়া (Assamese)' },
            { code: 'bn', name: 'বাংলা (Bengali)' },
            { code: 'hi', name: 'हिन्दी (Hindi)' },
            { code: 'kha', name: 'Khasi (Meghalaya)' },
            { code: 'lus', name: 'Mizo (Mizoram)' },
            { code: 'mni', name: 'মৈতৈলোন্ (Manipuri)' },
            { code: 'ne', name: 'नेपाली (Nepali / Sikkim)' },
          ].map((lang) => (
            <button
              key={lang.code}
              onClick={() => setSelectedLanguage(lang.code)}
              className={`px-2.5 py-1 rounded border text-[11px] transition-colors ${
                selectedLanguage === lang.code
                  ? 'bg-blue-950 text-blue-300 border-blue-700 font-bold'
                  : 'bg-slate-950 text-slate-400 border-slate-800 hover:bg-slate-800'
              }`}
            >
              {lang.name}
            </button>
          ))}
        </div>

        {/* Translation Output Box */}
        {currentTranslation && (
          <div className="p-3 bg-slate-950 border border-slate-800 rounded space-y-2">
            <div className="flex items-center justify-between border-b border-slate-900 pb-1.5">
              <span className="font-bold text-slate-200">{currentTranslation.headline}</span>
              <span className="text-[10px] text-slate-500 uppercase">{currentTranslation.language_name}</span>
            </div>

            <div className="space-y-1 text-slate-300 font-sans text-xs">
              <div><strong>Description:</strong> {currentTranslation.description}</div>
              <div><strong>Instruction:</strong> {currentTranslation.instruction}</div>
            </div>

            <div className="pt-2 border-t border-slate-900 flex justify-between items-center text-[10px] text-slate-500 font-mono">
              <span>CAP Format: OASIS CAP-v1.2 XML / JSON</span>
              <span className="text-emerald-400 font-bold">TEMPLATE READY (OFFLINE)</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
