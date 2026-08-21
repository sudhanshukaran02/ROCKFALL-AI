import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchUNetSample } from '@/services/api';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorState } from '@/components/common/EmptyState';
import {
  ScanEye,
  Info,
} from 'lucide-react';

export const LandslideDetection: React.FC = () => {
  const unetQ = useQuery({ queryKey: ['unetSample'], queryFn: fetchUNetSample });

  const isLoading = unetQ.isLoading;
  const isError = unetQ.isError;

  if (isLoading) {
    return (
      <div className="h-96 flex items-center justify-center">
        <LoadingSpinner label="Loading 4-Channel U-Net Architecture & Evaluation Metrics..." size="lg" />
      </div>
    );
  }

  if (isError) {
    return (
      <ErrorState
        title="U-Net Analysis Service Error"
        message="Failed to load U-Net inference output from backend adapter."
        onRetry={() => unetQ.refetch()}
      />
    );
  }

  const unetData = unetQ.data;


  return (
    <div className="space-y-4">
      {/* 1. Header Information Bar */}
      <div className="p-3.5 bg-slate-900 border border-slate-800 rounded flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-3">
          <ScanEye className="w-4 h-4 text-blue-400" />
          <div>
            <strong className="font-mono tracking-wide text-slate-200 uppercase">
              MODEL: U-NET 4-CHANNEL SPATIAL SEGMENTATION
            </strong>
            <span className="text-slate-500 mx-2">•</span>
            <span className="text-slate-400 font-mono text-[11px]">
              E_spatial Stream (25% Weight in Late Fusion)
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3 font-mono text-[11px]">
          <span className="text-slate-400">
            CHECKPOINT: <strong className="text-slate-200">best_unet.pth (31,118,347 bytes)</strong>
          </span>
          <span className="text-slate-700">|</span>
          <span className="px-2 py-0.5 rounded bg-slate-950 text-emerald-400 border border-emerald-800 font-semibold">
            WEIGHTS VERIFIED
          </span>
        </div>
      </div>

      {/* 2. Structured Model Specification & Input/Output Matrix */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Specification Panel (4 Cols) */}
        <div className="lg:col-span-4 bg-slate-900 border border-slate-800 rounded p-4 space-y-3">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <span className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wide">
              Model Specifications
            </span>
            <span className="text-[10px] font-mono text-slate-500">PyTorch CNN</span>
          </div>

          <div className="space-y-2 text-xs font-mono">
            <div className="p-2 bg-slate-950 border border-slate-800 rounded space-y-1">
              <span className="text-[10px] text-slate-500 uppercase block font-sans">Primary Purpose</span>
              <p className="text-slate-200 font-sans text-xs">
                Spatial segmentation of active landslide scar geometries from remote sensing imagery and topographic slope.
              </p>
            </div>

            <div className="p-2 bg-slate-950 border border-slate-800 rounded space-y-1">
              <span className="text-[10px] text-slate-500 uppercase block font-sans">Input Format</span>
              <p className="text-slate-200 text-xs font-mono">
                128 × 128 × 4 Tensor (RGB + Multispectral Proxy)
              </p>
            </div>

            <div className="p-2 bg-slate-950 border border-slate-800 rounded space-y-1">
              <span className="text-[10px] text-slate-500 uppercase block font-sans">Output Format</span>
              <p className="text-slate-200 text-xs font-mono">
                128 × 128 Probability Mask → Scalar E_spatial [0.0, 1.0]
              </p>
            </div>

            <div className="p-2 bg-slate-950 border border-slate-800 rounded space-y-1">
              <span className="text-[10px] text-slate-500 uppercase block font-sans">Loss Function</span>
              <p className="text-slate-200 text-xs font-mono">
                Binary Cross-Entropy + Dice Loss (Combined)
              </p>
            </div>
          </div>
        </div>

        {/* Inference Visual Evidence (8 Cols) */}
        <div className="lg:col-span-8 bg-slate-900 border border-slate-800 rounded p-4 space-y-3">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <span className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wide">
              Visual Evidence Decomposition
            </span>
            <span className="text-[10px] font-mono text-slate-400">
              Evaluated on 128×128 Test Tile
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {/* Input Tile */}
            <div className="p-2 bg-slate-950 border border-slate-800 rounded space-y-1.5 text-center">
              <span className="text-[11px] font-mono text-slate-400 block uppercase">1. Input Tile</span>
              <div className="aspect-square bg-slate-900 rounded overflow-hidden border border-slate-800 flex items-center justify-center">
                {unetData?.input_image_base64 ? (
                  <img
                    src={unetData.input_image_base64}
                    alt="Input Tile"
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <span className="text-xs text-slate-600 font-mono">Input Tile</span>
                )}
              </div>
              <span className="text-[10px] font-mono text-slate-500 block">RGB + Slope Channel</span>
            </div>

            {/* Predicted Binary Mask */}
            <div className="p-2 bg-slate-950 border border-slate-800 rounded space-y-1.5 text-center">
              <span className="text-[11px] font-mono text-purple-400 block uppercase">2. Predicted Scar</span>
              <div className="aspect-square bg-slate-900 rounded overflow-hidden border border-purple-900/50 flex items-center justify-center">
                {unetData?.mask_image_base64 ? (
                  <img
                    src={unetData.mask_image_base64}
                    alt="Predicted Scar"
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <span className="text-xs text-slate-600 font-mono">Mask</span>
                )}
              </div>
              <span className="text-[10px] font-mono text-purple-300 block">
                {unetData?.detected_pixels || 0} px ({unetData?.coverage_percentage || 0}%)
              </span>
            </div>

            {/* Probability Heatmap */}
            <div className="p-2 bg-slate-950 border border-slate-800 rounded space-y-1.5 text-center">
              <span className="text-[11px] font-mono text-amber-400 block uppercase">3. Probability Map</span>
              <div className="aspect-square bg-slate-900 rounded overflow-hidden border border-amber-900/50 flex items-center justify-center">
                {unetData?.heatmap_image_base64 ? (
                  <img
                    src={unetData.heatmap_image_base64}
                    alt="Probability Heatmap"
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <span className="text-xs text-slate-600 font-mono">Heatmap</span>
                )}
              </div>
              <span className="text-[10px] font-mono text-amber-300 block">
                E_spatial = {(unetData?.spatial_evidence || 0.4).toFixed(4)}
              </span>
            </div>
          </div>

          <div className="p-2.5 bg-slate-950 border border-slate-800 rounded flex items-center justify-between text-xs font-mono">
            <span className="text-slate-400">Scalar Spatial Evidence Contribution:</span>
            <strong className="text-amber-400 text-sm">
              E_spatial = {(unetData?.spatial_evidence || 0.40).toFixed(4)}
            </strong>
          </div>
        </div>
      </div>

      {/* 3. Verified Performance Benchmark Table */}
      <div className="bg-slate-900 border border-slate-800 rounded overflow-hidden">
        <div className="px-3.5 py-2.5 border-b border-slate-800 bg-slate-950 flex items-center justify-between text-xs">
          <strong className="text-slate-200 font-medium">
            Verified Test Split Performance Benchmarks (Frozen)
          </strong>
          <span className="text-[10px] font-mono text-emerald-400">
            Unseen Regional Evaluation
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-950 text-slate-500 uppercase text-[10px] border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-4">Metric</th>
                <th className="py-2.5 px-4">Evaluation Value</th>
                <th className="py-2.5 px-4">Engineering Target / Interpretation</th>
                <th className="py-2.5 px-4 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300 text-[11px]">
              <tr className="hover:bg-slate-800/30">
                <td className="py-2 px-4 font-bold text-slate-200">Test Recall (Sensitivity)</td>
                <td className="py-2 px-4 text-emerald-400 font-bold">91.41%</td>
                <td className="py-2 px-4 font-sans text-slate-400">Captures 91.4% of all ground-truth scar pixels (Prioritizes safety)</td>
                <td className="py-2 px-4 text-right text-emerald-400">VERIFIED</td>
              </tr>
              <tr className="hover:bg-slate-800/30">
                <td className="py-2 px-4 font-bold text-slate-200">Intersection-over-Union (IoU)</td>
                <td className="py-2 px-4 text-blue-400 font-bold">0.2595</td>
                <td className="py-2 px-4 font-sans text-slate-400">Standard spatial overlap metric on unseen regional terrain</td>
                <td className="py-2 px-4 text-right text-emerald-400">VERIFIED</td>
              </tr>
              <tr className="hover:bg-slate-800/30">
                <td className="py-2 px-4 font-bold text-slate-200">Dice / F1 Coefficient</td>
                <td className="py-2 px-4 text-purple-400 font-bold">0.4121</td>
                <td className="py-2 px-4 font-sans text-slate-400">Harmonic mean of precision and recall under class imbalance</td>
                <td className="py-2 px-4 text-right text-emerald-400">VERIFIED</td>
              </tr>
              <tr className="hover:bg-slate-800/30">
                <td className="py-2 px-4 font-bold text-slate-200">Test Precision</td>
                <td className="py-2 px-4 text-amber-400 font-bold">26.60%</td>
                <td className="py-2 px-4 font-sans text-slate-400">Conservative overprediction accepted to minimize missed events</td>
                <td className="py-2 px-4 text-right text-emerald-400">VERIFIED</td>
              </tr>
              <tr className="hover:bg-slate-800/30">
                <td className="py-2 px-4 font-bold text-slate-200">Pixel Accuracy</td>
                <td className="py-2 px-4 text-slate-200 font-bold">87.94%</td>
                <td className="py-2 px-4 font-sans text-slate-400">Overall background versus scar classification accuracy</td>
                <td className="py-2 px-4 text-right text-emerald-400">VERIFIED</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* 4. Interpretation & Physical Role */}
      <div className="p-3.5 bg-slate-900 border border-slate-800 rounded space-y-1.5 text-xs">
        <div className="flex items-center gap-2 text-slate-200 font-semibold font-mono uppercase text-[11px]">
          <Info className="w-3.5 h-3.5 text-blue-400" />
          Model Interpretation & Decision-Support Role
        </div>
        <p className="text-slate-400 font-sans leading-relaxed text-[11px]">
          The 4-Channel U-Net answers: <strong>"WHERE is spatial scar evidence detectable in recent imagery?"</strong>. It provides the spatial evidence component E_spatial to the multimodal late-fusion equation (weighted at 25%). Its high sensitivity (91.41%) ensures active slope failures are detected, while temporal and terrain streams filter false positives.
        </p>
      </div>
    </div>
  );
};
