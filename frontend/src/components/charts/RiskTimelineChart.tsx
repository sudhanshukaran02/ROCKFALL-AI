import React from 'react';
import ReactECharts from 'echarts-for-react';
import { RiskTimelinePoint } from '@/types';

interface RiskTimelineChartProps {
  points: RiskTimelinePoint[];
  height?: string | number;
}

export const RiskTimelineChart: React.FC<RiskTimelineChartProps> = ({
  points,
  height = 320,
}) => {
  const dates = points.map((p) => p.date);
  const multimodalRisks = points.map((p) => p.multimodal_risk);
  const temporalRisks = points.map((p) => p.temporal_risk);

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#0f172a',
      borderColor: '#334155',
      textStyle: { color: '#f8fafc', fontSize: 12 },
      formatter: (params: any) => {
        if (!params || !params.length) return '';
        const dateStr = params[0].axisValue;
        let html = `<div style="font-weight: 600; margin-bottom: 4px; border-bottom: 1px solid #334155; padding-bottom: 2px;">${dateStr}</div>`;
        params.forEach((item: any) => {
          html += `<div style="display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-top: 2px;">
            <span style="color: ${item.color}">${item.seriesName}:</span>
            <span style="font-family: monospace; font-weight: 600;">${Number(item.value).toFixed(4)}</span>
          </div>`;
        });
        return html;
      },
    },
    legend: {
      data: ['Multimodal Risk Index (R)', 'Temporal Weather Risk (T)'],
      textStyle: { color: '#94a3b8', fontSize: 11 },
      top: 0,
      right: 10,
    },
    grid: {
      left: '3%',
      right: '3%',
      bottom: '10%',
      top: '15%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLine: { lineStyle: { color: '#334155' } },
      axisLabel: { color: '#94a3b8', fontSize: 10 },
      splitLine: { show: false },
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 1.0,
      axisLine: { lineStyle: { color: '#334155' } },
      splitLine: { lineStyle: { color: '#1e293b' } },
      axisLabel: { color: '#94a3b8', fontSize: 10 },
    },
    series: [
      {
        name: 'Multimodal Risk Index (R)',
        type: 'line',
        data: multimodalRisks,
        smooth: true,
        showSymbol: false,
        lineStyle: { width: 2, color: '#f59e0b' },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(245, 158, 11, 0.25)' },
              { offset: 1, color: 'rgba(245, 158, 11, 0.0)' },
            ],
          },
        },
        markLine: {
          silent: true,
          symbol: 'none',
          data: [
            {
              yAxis: 0.65,
              lineStyle: { color: '#ea580c', type: 'dashed', width: 1.5 },
              label: { formatter: 'Balanced Threshold (0.65)', color: '#ea580c', fontSize: 10, position: 'insideEndTop' },
            },
            {
              yAxis: 0.48,
              lineStyle: { color: '#d97706', type: 'dotted', width: 1 },
              label: { formatter: 'High-Sensitivity (0.48)', color: '#d97706', fontSize: 9, position: 'insideEndTop' },
            },
          ],
        },
      },
      {
        name: 'Temporal Weather Risk (T)',
        type: 'line',
        data: temporalRisks,
        smooth: true,
        showSymbol: false,
        lineStyle: { width: 1.5, color: '#38bdf8', type: 'dashed' },
      },
    ],
  };

  return <ReactECharts option={option} style={{ height, width: '100%' }} />;
};
