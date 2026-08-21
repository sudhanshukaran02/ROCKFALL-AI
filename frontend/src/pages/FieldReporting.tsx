import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchFieldObservations, submitFieldReport, verifyFieldReport } from '@/services/api';
import { Card } from '@/components/common/Card';
import { StatusBadge } from '@/components/common/StatusBadge';
import { RiskBadge } from '@/components/common/RiskBadge';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorState } from '@/components/common/EmptyState';
import {
  FileText,
  CheckCircle,
  XCircle,
  Send,
  Camera,
  Car,
  HardHat,
} from 'lucide-react';
import { IncidentType, ReportSeverity, ReportVerificationStatus } from '@/types';

const INCIDENT_TYPES: IncidentType[] = [
  'LANDSLIDE',
  'SLOPE_FAILURE',
  'CRACK',
  'ROCKFALL',
  'ROAD_BLOCKAGE',
  'FLOOD',
  'OTHER',
];

const SEVERITIES: ReportSeverity[] = ['LOW', 'MODERATE', 'HIGH', 'CRITICAL'];

const PRESET_LOCATIONS = [
  { name: 'Shillong Bypass (NH-6, Meghalaya)', lat: 25.5788, lon: 91.8933 },
  { name: 'Gangtok-Melli Highway (NH-10, Sikkim)', lat: 27.3389, lon: 88.6065 },
  { name: 'Kohima-Dimapur Road (NH-29, Nagaland)', lat: 25.6751, lon: 94.1086 },
  { name: 'Aizawl Sairang Road (Mizoram)', lat: 23.7271, lon: 92.7176 },
  { name: 'Guwahati-Dispur Foothills (Assam)', lat: 26.1445, lon: 91.7362 },
];

export const FieldReporting: React.FC = () => {
  const queryClient = useQueryClient();

  // Form State
  const [lat, setLat] = useState<number>(25.5788);
  const [lon, setLon] = useState<number>(91.8933);
  const [incidentType, setIncidentType] = useState<IncidentType>('LANDSLIDE');
  const [severity, setSeverity] = useState<ReportSeverity>('HIGH');
  const [description, setDescription] = useState<string>('');
  const [reporterName, setReporterName] = useState<string>('Site Engineer T. Sangma');
  const [infrastructure, setInfrastructure] = useState<string>('Road / Slope Transit (NH-6)');
  const [roadBlocked, setRoadBlocked] = useState<boolean>(true);
  const [photoFileName, setPhotoFileName] = useState<string>('field_slip_photo_01.jpg');
  const [formSuccess, setFormSuccess] = useState<string | null>(null);

  // Filter State
  const [statusFilter, setStatusFilter] = useState<'ALL' | ReportVerificationStatus>('ALL');

  // Verification Review State
  const [selectedReportId, setSelectedReportId] = useState<string | null>(null);
  const [reviewerNotes, setReviewerNotes] = useState<string>('');

  const reportsQ = useQuery({
    queryKey: ['fieldObservations'],
    queryFn: fetchFieldObservations,
  });

  const submitMutation = useMutation({
    mutationFn: submitFieldReport,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['fieldObservations'] });
      setFormSuccess(`Report ${data.report_id} successfully submitted for technical review.`);
      setDescription('');
      setTimeout(() => setFormSuccess(null), 5000);
    },
  });

  const verifyMutation = useMutation({
    mutationFn: verifyFieldReport,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['fieldObservations'] });
      setSelectedReportId(null);
      setReviewerNotes('');
    },
  });

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!description.trim()) return;

    submitMutation.mutate({
      latitude: Number(lat),
      longitude: Number(lon),
      incident_type: incidentType,
      severity: severity,
      description: description.trim(),
      reporter_name: reporterName,
      infrastructure_affected: infrastructure,
      road_blocked: roadBlocked,
      photo_path: photoFileName ? `data/field_reports/${photoFileName}` : 'None',
    });
  };

  if (reportsQ.isLoading) {
    return (
      <div className="h-96 flex items-center justify-center">
        <LoadingSpinner label="Loading Field Observation Reports & Verification Queue..." size="lg" />
      </div>
    );
  }

  if (reportsQ.isError) {
    return (
      <ErrorState
        title="Field Reporting Error"
        message="Failed to load field observation reports from backend."
        onRetry={() => reportsQ.refetch()}
      />
    );
  }

  const reports = reportsQ.data?.reports || [];
  const filteredReports = reports.filter((r: any) => {
    if (statusFilter === 'ALL') return true;
    return r.status === statusFilter;
  });

  return (
    <div className="space-y-6">
      {/* 1. Mandatory Scientific & Safety Notice */}
      <div className="p-4 rounded-lg bg-slate-900 border border-blue-800/60 text-slate-200 flex items-start justify-between gap-4 shadow-card">
        <div className="flex items-start gap-3">
          <HardHat className="w-5 h-5 text-blue-400 shrink-0 mt-0.5" />
          <div className="text-xs space-y-1">
            <strong className="text-blue-300 font-semibold uppercase tracking-wider block">
              FIELD GROUND TRUTHING & OBSERVATION SUBMISSION PROTOCOL
            </strong>
            <p className="text-slate-300/90 leading-relaxed">
              Field observations submitted by citizens and onsite geotechnical engineers are recorded as <strong>application ground-truth data</strong> and are labeled <span className="text-amber-400 font-semibold">NOT SCIENTIFICALLY VERIFIED</span> until an authorized geologist completes human verification.
            </p>
          </div>
        </div>
        <StatusBadge status="FIELD OBSERVATION" size="sm" />
      </div>

      {/* 2. Main Two-Column Layout: Submission Form + Verification Queue */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Field Report Submission Form (5 Cols) */}
        <div className="lg:col-span-5 space-y-4">
          <Card
            title="Submit Field Observation"
            subtitle="Geotagged incident report from mobile units or onsite engineers"
            badge={<FileText className="w-4 h-4 text-emerald-400" />}
          >
            <form onSubmit={handleFormSubmit} className="space-y-4 text-xs">
              {formSuccess && (
                <div className="p-3 rounded bg-emerald-950/60 border border-emerald-800 text-emerald-300 flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 shrink-0" />
                  <span>{formSuccess}</span>
                </div>
              )}

              {/* Location Preset Selector */}
              <div>
                <label className="block text-slate-400 mb-1 font-medium">Quick Preset Corridor (NER)</label>
                <select
                  className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-blue-500 font-mono"
                  onChange={(e) => {
                    const preset = PRESET_LOCATIONS[Number(e.target.value)];
                    if (preset) {
                      setLat(preset.lat);
                      setLon(preset.lon);
                    }
                  }}
                >
                  {PRESET_LOCATIONS.map((loc, idx) => (
                    <option key={idx} value={idx}>
                      {loc.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* GPS Coordinates */}
              <div className="grid grid-cols-2 gap-3 font-mono">
                <div>
                  <label className="block text-slate-400 mb-1 font-medium font-sans">GPS Latitude (°N)</label>
                  <input
                    type="number"
                    step="0.0001"
                    value={lat}
                    onChange={(e) => setLat(parseFloat(e.target.value) || 0)}
                    required
                    className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1 font-medium font-sans">GPS Longitude (°E)</label>
                  <input
                    type="number"
                    step="0.0001"
                    value={lon}
                    onChange={(e) => setLon(parseFloat(e.target.value) || 0)}
                    required
                    className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              {/* Incident Type & Severity */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1 font-medium">Incident Type</label>
                  <select
                    value={incidentType}
                    onChange={(e) => setIncidentType(e.target.value as IncidentType)}
                    className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-blue-500"
                  >
                    {INCIDENT_TYPES.map((type) => (
                      <option key={type} value={type}>
                        {type.replace('_', ' ')}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-slate-400 mb-1 font-medium">Estimated Severity</label>
                  <select
                    value={severity}
                    onChange={(e) => setSeverity(e.target.value as ReportSeverity)}
                    className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-blue-500"
                  >
                    {SEVERITIES.map((sev) => (
                      <option key={sev} value={sev}>
                        {sev}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Reporter Name & Infrastructure */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1 font-medium">Reporter / Unit</label>
                  <input
                    type="text"
                    value={reporterName}
                    onChange={(e) => setReporterName(e.target.value)}
                    placeholder="e.g. Field Engineer T. Sangma"
                    className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1 font-medium">Infrastructure Affected</label>
                  <input
                    type="text"
                    value={infrastructure}
                    onChange={(e) => setInfrastructure(e.target.value)}
                    placeholder="e.g. NH-6 Transit Corridor"
                    className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              {/* Road Blockage Toggle */}
              <div className="flex items-center justify-between p-2.5 rounded bg-slate-950 border border-slate-800">
                <div className="flex items-center gap-2">
                  <Car className="w-4 h-4 text-amber-400" />
                  <span className="text-slate-300 font-medium">Transit Route / Road Blockage</span>
                </div>
                <button
                  type="button"
                  onClick={() => setRoadBlocked(!roadBlocked)}
                  className={`px-3 py-1 rounded text-[11px] font-semibold transition-colors ${
                    roadBlocked
                      ? 'bg-red-500/20 text-red-300 border border-red-500/40'
                      : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                  }`}
                >
                  {roadBlocked ? 'ROAD BLOCKED' : 'PASSABLE'}
                </button>
              </div>

              {/* Photo Evidence Simulation */}
              <div>
                <label className="block text-slate-400 mb-1 font-medium flex items-center justify-between">
                  <span>Photo / Evidence Attachment</span>
                  <span className="text-[10px] text-slate-500">Stored in data/field_reports/</span>
                </label>
                <div className="flex items-center gap-2">
                  <div className="p-2 rounded bg-slate-950 border border-slate-800 text-slate-400">
                    <Camera className="w-4 h-4 text-slate-300" />
                  </div>
                  <input
                    type="text"
                    value={photoFileName}
                    onChange={(e) => setPhotoFileName(e.target.value)}
                    placeholder="e.g. slope_failure_nh6.jpg"
                    className="flex-1 bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-slate-200 font-mono text-[11px] focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              {/* Description */}
              <div>
                <label className="block text-slate-400 mb-1 font-medium">Incident Description & Visual Indicators</label>
                <textarea
                  rows={3}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  required
                  placeholder="Describe slope movement, crack tension width, mud accumulation, or culvert overflow..."
                  className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-blue-500 leading-relaxed"
                />
              </div>

              <button
                type="submit"
                disabled={submitMutation.isPending || !description.trim()}
                className="w-full py-2 px-4 rounded bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-semibold flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
              >
                {submitMutation.isPending ? (
                  <LoadingSpinner size="sm" />
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    <span>Submit Report for Technical Verification</span>
                  </>
                )}
              </button>
            </form>
          </Card>
        </div>

        {/* Right Column: Verification Queue & Review Workspace (7 Cols) */}
        <div className="lg:col-span-7 space-y-4">
          <Card
            title={`Field Verification Queue (${reports.length} Total Reports)`}
            subtitle="Authorized geotechnical verification workflow (Pending -> Verified / Rejected)"
            badge={
              <div className="flex items-center gap-1.5">
                {(['ALL', 'PENDING_VERIFICATION', 'VERIFIED', 'REJECTED'] as const).map((filter) => (
                  <button
                    key={filter}
                    onClick={() => setStatusFilter(filter)}
                    className={`px-2 py-0.5 rounded text-[10px] font-semibold transition-colors ${
                      statusFilter === filter
                        ? 'bg-blue-600 text-white'
                        : 'bg-slate-900 text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    {filter.replace('_VERIFICATION', '')}
                  </button>
                ))}
              </div>
            }
          >
            <div className="space-y-3 max-h-[600px] overflow-y-auto pr-1">
              {filteredReports.length === 0 ? (
                <div className="p-8 text-center text-slate-500 text-xs">
                  No observation reports match the selected verification filter.
                </div>
              ) : (
                filteredReports.map((rep: any) => {
                  const isSelected = rep.report_id === selectedReportId;
                  const isVerified = rep.status === 'VERIFIED';
                  const isPending = rep.status === 'PENDING_VERIFICATION' || rep.status === 'SUBMITTED_PROTOTYPE';
                  const isRejected = rep.status === 'REJECTED';

                  return (
                    <div
                      key={rep.report_id}
                      className={`p-4 rounded-lg border transition-all ${
                        isSelected
                          ? 'bg-slate-900 border-blue-500 ring-1 ring-blue-500/50'
                          : 'bg-slate-950/70 border-slate-800 hover:border-slate-700'
                      }`}
                    >
                      <div className="flex items-start justify-between gap-3 mb-2">
                        <div>
                          <div className="flex items-center gap-2">
                            <strong className="text-slate-100 font-mono text-xs">{rep.report_id}</strong>
                            <RiskBadge
                              level={
                                rep.severity === 'CRITICAL'
                                  ? 'CRITICAL'
                                  : rep.severity === 'HIGH'
                                  ? 'WARNING'
                                  : rep.severity === 'MODERATE'
                                  ? 'WATCH'
                                  : 'LOW'
                              }
                              size="sm"
                            />
                            <span className="text-[11px] font-medium text-slate-300">
                              {rep.incident_type?.replace('_', ' ')}
                            </span>
                          </div>
                          <span className="text-[10px] text-slate-500 font-mono block mt-0.5">
                            {rep.timestamp} • Reporter: {rep.reporter_name || 'Field Unit'}
                          </span>
                        </div>

                        {/* Status Label */}
                        <div>
                          {isVerified && (
                            <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-950 border border-emerald-800 text-emerald-400">
                              VERIFIED
                            </span>
                          )}
                          {isPending && (
                            <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-amber-950 border border-amber-800 text-amber-400">
                              PENDING REVIEW
                            </span>
                          )}
                          {isRejected && (
                            <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-red-950 border border-red-800 text-red-400">
                              REJECTED
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Description & Metadata */}
                      <p className="text-xs text-slate-300 leading-relaxed mb-3">
                        {rep.description}
                      </p>

                      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-[11px] font-mono text-slate-400 bg-slate-950 p-2 rounded border border-slate-800/80 mb-3">
                        <div>
                          <span className="text-[10px] text-slate-500 uppercase block font-sans">Coordinates</span>
                          <span className="text-slate-300">{rep.latitude.toFixed(4)}°N, {rep.longitude.toFixed(4)}°E</span>
                        </div>
                        <div>
                          <span className="text-[10px] text-slate-500 uppercase block font-sans">Infrastructure</span>
                          <span className="text-slate-300 truncate block">{rep.infrastructure_affected || 'General'}</span>
                        </div>
                        <div>
                          <span className="text-[10px] text-slate-500 uppercase block font-sans">Road Status</span>
                          <span className={rep.road_blocked ? 'text-red-400 font-semibold' : 'text-emerald-400'}>
                            {rep.road_blocked ? 'BLOCKED' : 'PASSABLE'}
                          </span>
                        </div>
                      </div>

                      {/* Reviewer Notes if present */}
                      {rep.reviewer_notes && (
                        <div className="p-2 rounded bg-blue-950/30 border border-blue-900/40 text-[11px] text-blue-200 mb-3">
                          <strong className="text-blue-300 font-sans block text-[10px] uppercase">Reviewer Audit Notes:</strong>
                          <span>{rep.reviewer_notes}</span>
                        </div>
                      )}

                      {/* Action Bar */}
                      <div className="flex items-center justify-between pt-2 border-t border-slate-800 text-xs">
                        <span className="text-[10px] text-slate-500">
                          {rep.photo_path && rep.photo_path !== 'None'
                            ? `Evidence: ${rep.photo_path}`
                            : 'No photo attached'}
                        </span>

                        <div className="flex items-center gap-2">
                          {isSelected ? (
                            <button
                              onClick={() => setSelectedReportId(null)}
                              className="px-2.5 py-1 rounded bg-slate-800 text-slate-300 text-[11px]"
                            >
                              Cancel
                            </button>
                          ) : (
                            <button
                              onClick={() => {
                                setSelectedReportId(rep.report_id);
                                setReviewerNotes(rep.reviewer_notes || '');
                              }}
                              className="px-2.5 py-1 rounded bg-blue-600/30 hover:bg-blue-600/50 text-blue-300 border border-blue-500/40 text-[11px] font-medium"
                            >
                              Review & Authorize
                            </button>
                          )}
                        </div>
                      </div>

                      {/* Interactive Verification Review Drawer */}
                      {isSelected && (
                        <div className="mt-3 p-3 rounded bg-slate-900 border border-blue-800/80 space-y-3 animate-fadeIn">
                          <div>
                            <label className="block text-slate-400 mb-1 text-[11px] font-medium">
                              Geotechnical Reviewer Notes:
                            </label>
                            <input
                              type="text"
                              value={reviewerNotes}
                              onChange={(e) => setReviewerNotes(e.target.value)}
                              placeholder="e.g. Field inspection confirmed active headscarp tension crack..."
                              className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-slate-200 text-xs focus:outline-none focus:border-blue-500"
                            />
                          </div>

                          <div className="flex items-center justify-end gap-2">
                            <button
                              onClick={() =>
                                verifyMutation.mutate({
                                  report_id: rep.report_id,
                                  new_status: 'REJECTED',
                                  reviewer_notes: reviewerNotes || 'Dismissed upon preliminary technical review.',
                                })
                              }
                              disabled={verifyMutation.isPending}
                              className="px-3 py-1.5 rounded bg-red-950 hover:bg-red-900 text-red-300 border border-red-800 font-semibold text-[11px] flex items-center gap-1.5"
                            >
                              <XCircle className="w-3.5 h-3.5" />
                              <span>Reject Report</span>
                            </button>

                            <button
                              onClick={() =>
                                verifyMutation.mutate({
                                  report_id: rep.report_id,
                                  new_status: 'VERIFIED',
                                  reviewer_notes: reviewerNotes || 'Ground truth validated by onsite geotechnical engineer.',
                                })
                              }
                              disabled={verifyMutation.isPending}
                              className="px-3 py-1.5 rounded bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-semibold text-[11px] flex items-center gap-1.5"
                            >
                              <CheckCircle className="w-3.5 h-3.5" />
                              <span>Verify as Ground Truth</span>
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })
              )}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};
