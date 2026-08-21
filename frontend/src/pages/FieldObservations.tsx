import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchFieldObservations, submitFieldReport, verifyFieldReport } from '@/services/api';
import { RiskBadge } from '@/components/common/RiskBadge';
import { StatusBadge } from '@/components/common/StatusBadge';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorState } from '@/components/common/EmptyState';
import {
  Camera,
  FileCheck,
  Send,
} from 'lucide-react';

export const FieldObservations: React.FC = () => {
  const queryClient = useQueryClient();

  // Form State
  const [locationName, setLocationName] = useState('');
  const [state, setState] = useState('Meghalaya');
  const [district, setDistrict] = useState('East Khasi Hills');
  const [latitude, setLatitude] = useState(25.5788);
  const [longitude, setLongitude] = useState(91.8933);
  const [hazardType, setHazardType] = useState('LANDSLIDE');
  const [severity, setSeverity] = useState('HIGH');
  const [roadBlocked, setRoadBlocked] = useState(true);
  const [infrastructure, setInfrastructure] = useState('NH-6 Arterial Corridor');
  const [reporterName, setReporterName] = useState('Field Geotechnical Officer');
  const [description, setDescription] = useState('Active slope shear failure observed following 48h persistent rainfall.');
  const [submitSuccess, setSubmitSuccess] = useState(false);

  // Queries
  const reportsQ = useQuery({ queryKey: ['fieldObservations'], queryFn: fetchFieldObservations });

  // Mutations
  const submitMut = useMutation({
    mutationFn: submitFieldReport,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['fieldObservations'] });
      setSubmitSuccess(true);
      setTimeout(() => setSubmitSuccess(false), 4000);
      setLocationName('');
    },
  });

  const verifyMut = useMutation({
    mutationFn: verifyFieldReport,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['fieldObservations'] });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    submitMut.mutate({
      latitude: Number(latitude),
      longitude: Number(longitude),
      incident_type: hazardType,
      severity,
      description: `${locationName || 'Mountain Corridor'} (${district}, ${state}): ${description}`,
      reporter_name: reporterName,
      infrastructure_affected: infrastructure,
      road_blocked: roadBlocked,
    });
  };


  const handlePreset = (name: string, st: string, dt: string, lat: number, lng: number) => {
    setLocationName(name);
    setState(st);
    setDistrict(dt);
    setLatitude(lat);
    setLongitude(lng);
  };

  if (reportsQ.isLoading) {
    return (
      <div className="h-96 flex items-center justify-center">
        <LoadingSpinner label="Loading Field Observation Records & Geotechnical Queue..." size="lg" />
      </div>
    );
  }

  if (reportsQ.isError) {
    return (
      <ErrorState
        title="Field Service Error"
        message="Failed to load field observation database from the FastAPI backend."
        onRetry={() => reportsQ.refetch()}
      />
    );
  }

  const reports = reportsQ.data?.reports || [];

  return (
    <div className="space-y-4">
      {/* 1. Institutional Ops Sub-Header Bar */}
      <div className="p-3.5 bg-slate-900 border border-slate-800 rounded flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-3">
          <Camera className="w-4 h-4 text-blue-400" />
          <div>
            <strong className="font-mono tracking-wide text-slate-200 uppercase">
              FIELD OBSERVATIONS & GEOTECHNICAL VERIFICATION QUEUE
            </strong>
            <span className="text-slate-500 mx-2">•</span>
            <span className="text-slate-400 font-mono text-[11px]">
              Ground-Truth Ingestion & Civil Defense Incident Logging
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3 font-mono text-[11px]">
          <span className="text-slate-400">
            TOTAL RECORDS: <strong className="text-slate-200">{reports.length} Reports</strong>
          </span>
          <span className="text-slate-700">|</span>
          <span className="px-2 py-0.5 rounded bg-slate-950 text-blue-400 border border-blue-900 font-semibold">
            LOCAL REPOSITORY
          </span>
        </div>
      </div>

      {/* 2. Main Grid: Engineering Entry Form & Review Queue */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Field Entry Form (5 Cols) */}
        <div className="lg:col-span-5 bg-slate-900 border border-slate-800 rounded p-4 space-y-3">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <span className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wide">
              Field Incident Entry Form
            </span>
            <span className="text-[10px] font-mono text-slate-500">ISO Field Standard</span>
          </div>

          {/* Quick Presets */}
          <div className="space-y-1">
            <span className="text-[10px] font-mono uppercase text-slate-500 block">Quick Coordinate Presets:</span>
            <div className="flex flex-wrap gap-1 font-mono text-[10px]">
              <button
                type="button"
                onClick={() => handlePreset('Shillong Pass (NH-6)', 'Meghalaya', 'East Khasi Hills', 25.5788, 91.8933)}
                className="px-2 py-0.5 rounded bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800 transition-colors"
              >
                Shillong NH-6
              </button>
              <button
                type="button"
                onClick={() => handlePreset('Guwahati Hill Slope', 'Assam', 'Kamrup Metro', 26.1445, 91.7362)}
                className="px-2 py-0.5 rounded bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800 transition-colors"
              >
                Guwahati Slopes
              </button>
              <button
                type="button"
                onClick={() => handlePreset('Gangtok Bypass', 'Sikkim', 'East Sikkim', 27.3389, 88.6138)}
                className="px-2 py-0.5 rounded bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800 transition-colors"
              >
                Gangtok NH-10
              </button>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-2.5 text-xs font-mono">
            <div>
              <label className="block text-[10px] text-slate-500 uppercase mb-0.5">Location Name</label>
              <input
                type="text"
                required
                value={locationName}
                onChange={(e) => setLocationName(e.target.value)}
                placeholder="e.g. NH-6 KM 42 Slope Failure"
                className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-slate-200 text-xs focus:border-blue-600 focus:outline-none"
              />
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-[10px] text-slate-500 uppercase mb-0.5">Latitude (°N)</label>
                <input
                  type="number"
                  step="0.0001"
                  required
                  value={latitude}
                  onChange={(e) => setLatitude(parseFloat(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-slate-200 text-xs focus:border-blue-600 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-[10px] text-slate-500 uppercase mb-0.5">Longitude (°E)</label>
                <input
                  type="number"
                  step="0.0001"
                  required
                  value={longitude}
                  onChange={(e) => setLongitude(parseFloat(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-slate-200 text-xs focus:border-blue-600 focus:outline-none"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-[10px] text-slate-500 uppercase mb-0.5">State</label>
                <select
                  value={state}
                  onChange={(e) => setState(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded px-2 py-1.5 text-slate-200 text-xs focus:border-blue-600 focus:outline-none font-sans"
                >
                  <option value="Meghalaya">Meghalaya</option>
                  <option value="Assam">Assam</option>
                  <option value="Sikkim">Sikkim</option>
                  <option value="Manipur">Manipur</option>
                  <option value="Mizoram">Mizoram</option>
                  <option value="Nagaland">Nagaland</option>
                  <option value="Arunachal Pradesh">Arunachal Pradesh</option>
                  <option value="Tripura">Tripura</option>
                </select>
              </div>
              <div>
                <label className="block text-[10px] text-slate-500 uppercase mb-0.5">Incident Type</label>
                <select
                  value={hazardType}
                  onChange={(e) => setHazardType(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded px-2 py-1.5 text-slate-200 text-xs focus:border-blue-600 focus:outline-none"
                >
                  <option value="LANDSLIDE">LANDSLIDE</option>
                  <option value="SLOPE_FAILURE">SLOPE_FAILURE</option>
                  <option value="TENSION_CRACK">TENSION_CRACK</option>
                  <option value="ROCKFALL">ROCKFALL</option>
                  <option value="DEBRIS_FLOW">DEBRIS_FLOW</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-[10px] text-slate-500 uppercase mb-0.5">Severity</label>
                <select
                  value={severity}
                  onChange={(e) => setSeverity(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded px-2 py-1.5 text-slate-200 text-xs focus:border-blue-600 focus:outline-none"
                >
                  <option value="LOW">LOW</option>
                  <option value="MODERATE">MODERATE</option>
                  <option value="HIGH">HIGH</option>
                  <option value="CRITICAL">CRITICAL</option>
                </select>
              </div>
              <div>
                <label className="block text-[10px] text-slate-500 uppercase mb-0.5">Road Blocked?</label>
                <select
                  value={roadBlocked ? 'YES' : 'NO'}
                  onChange={(e) => setRoadBlocked(e.target.value === 'YES')}
                  className="w-full bg-slate-950 border border-slate-800 rounded px-2 py-1.5 text-slate-200 text-xs focus:border-blue-600 focus:outline-none"
                >
                  <option value="YES">YES (BLOCKED)</option>
                  <option value="NO">NO (CLEAR)</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-[10px] text-slate-500 uppercase mb-0.5">Reporter Name</label>
                <input
                  type="text"
                  value={reporterName}
                  onChange={(e) => setReporterName(e.target.value)}
                  placeholder="Officer Name"
                  className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-slate-200 text-xs focus:border-blue-600 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-[10px] text-slate-500 uppercase mb-0.5">Infrastructure Affected</label>
                <input
                  type="text"
                  value={infrastructure}
                  onChange={(e) => setInfrastructure(e.target.value)}
                  placeholder="e.g. Highway Culvert"
                  className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-slate-200 text-xs focus:border-blue-600 focus:outline-none"
                />
              </div>
            </div>

            <div>
              <label className="block text-[10px] text-slate-500 uppercase mb-0.5">Observations / Geological Notes</label>
              <textarea
                rows={2}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-slate-200 text-xs focus:border-blue-600 focus:outline-none font-sans"
              />
            </div>

            <button
              type="submit"
              disabled={submitMut.isPending}
              className="w-full py-2 rounded bg-blue-600 hover:bg-blue-500 text-white font-bold transition-colors flex items-center justify-center gap-2 text-xs"
            >
              <Send className="w-3.5 h-3.5" />
              <span>{submitMut.isPending ? 'Logging to Database...' : 'Submit Incident Report'}</span>
            </button>

            {submitSuccess && (
              <div className="p-2 rounded bg-emerald-950 border border-emerald-800 text-emerald-300 text-center font-sans text-xs">
                Observation successfully recorded in local verification database.
              </div>
            )}
          </form>
        </div>

        {/* Administrative Review & Verification Queue (7 Cols) */}
        <div className="lg:col-span-7 bg-slate-900 border border-slate-800 rounded overflow-hidden flex flex-col">
          <div className="px-3.5 py-2.5 border-b border-slate-800 bg-slate-950 flex items-center justify-between text-xs">
            <strong className="text-slate-200 font-medium flex items-center gap-2">
              <FileCheck className="w-4 h-4 text-emerald-400" />
              Administrative Verification Queue & Field History
            </strong>
            <span className="text-[10px] font-mono text-slate-500">
              {reports.length} Total Logs
            </span>
          </div>

          <div className="overflow-x-auto flex-1 max-h-[560px] overflow-y-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-slate-950 text-slate-500 uppercase text-[10px] border-b border-slate-800 sticky top-0">
                <tr>
                  <th className="py-2.5 px-3">Report ID / Time</th>
                  <th className="py-2.5 px-3">Location</th>
                  <th className="py-2.5 px-3">Type</th>
                  <th className="py-2.5 px-3">Severity</th>
                  <th className="py-2.5 px-3 text-center">Status</th>
                  <th className="py-2.5 px-3 text-right">Reviewer Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300 text-[11px]">
                {reports.map((rep) => (
                  <tr key={rep.report_id} className="hover:bg-slate-800/30">
                    <td className="py-2.5 px-3">
                      <strong className="text-slate-200 block">{rep.report_id}</strong>
                      <span className="text-[10px] text-slate-500">{(rep.timestamp || rep.reported_at || '').slice(0, 10)}</span>
                    </td>
                    <td className="py-2.5 px-3 font-sans text-slate-200">
                      <span className="block font-medium truncate max-w-[140px]">{rep.description?.slice(0, 30) || 'Mountain Slope'}</span>
                      <span className="text-[10px] text-slate-500 font-mono">
                        {rep.latitude?.toFixed(3)}°N, {rep.longitude?.toFixed(3)}°E
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-slate-300">{rep.incident_type || rep.hazard_type || 'SLOPE'}</td>
                    <td className="py-2.5 px-3">
                      <RiskBadge level={rep.severity as any} size="sm" />
                    </td>
                    <td className="py-2.5 px-3 text-center">
                      <StatusBadge status={rep.status || 'UNVERIFIED'} size="sm" />
                    </td>
                    <td className="py-2.5 px-3 text-right">
                      <div className="flex items-center justify-end gap-1 font-mono text-[10px]">
                        <button
                          onClick={() => verifyMut.mutate({ report_id: rep.report_id, new_status: 'VERIFIED' })}
                          className="px-2 py-0.5 rounded bg-emerald-950 hover:bg-emerald-900 text-emerald-300 border border-emerald-800 transition-colors"
                          title="Verify as ground-truth record"
                        >
                          Verify
                        </button>
                        <button
                          onClick={() => verifyMut.mutate({ report_id: rep.report_id, new_status: 'REJECTED' })}
                          className="px-2 py-0.5 rounded bg-red-950 hover:bg-red-900 text-red-300 border border-red-800 transition-colors"
                          title="Reject report"
                        >
                          Reject
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
