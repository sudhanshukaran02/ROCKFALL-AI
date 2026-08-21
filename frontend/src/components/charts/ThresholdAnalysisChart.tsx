import React from 'react';
import ReactECharts from 'echarts-for-react';

interface ThresholdPoint {
  threshold: number;
  precision: number;
  recall: number;
  f1: number;
  specificity: number;
}

interface ThresholdAnalysisChartProps {
  points: ThresholdPoint[];
  height?: string | number;
}

export const ThresholdAnalysisChart: React.FC<ThresholdAnalysisChartProps> = ({
  points,
  height = 340,
}) => {
  const thresholds = points.map((p) => p.threshold.toFixed(2));
  const precision = points.map((p) => p.precision * 100);
  const recall = points.map((p) => p.recall * 100);
  const f1 = points.map((p) => p.f1);
  const specificity = points.map((p) => p.specificity * 100);

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#0f172a',
      borderColor: '#334155',
      textStyle: { color: '#f8fafc', fontSize: 12 },
      formatter: (params: any) => {
        if (!params || !params.length) return '';
        const th = params[0].axisValue;
        let html = `<div style="font-weight: 600; margin-bottom: 4px; border-bottom: 1px solid #334155; padding-bottom: 2px;">Decision Threshold: ${th}</div>`;
        params.forEach((item: any) => {
          const valStr = item.seriesName.includes('F1')
            ? Number(item.value).toFixed(4)
            : `${Number(item.value).toFixed(1)}%`;
          html += `<div style="display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-top: 2px;">
            <span style="color: ${item.color}">${item.seriesName}:</span>
            <span style="font-family: monospace; font-weight: 600;">${valStr}</span>
          </div>`;
        });
        return html;
      },
    },
    legend: {
      data: ['Recall (%)', 'Precision (%)', 'Specificity (%)', 'F1 Score'],
      textStyle: { color: '#94a3b8', fontSize: 11 },
      top: 0,
      right: 10,
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      top: '16%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      name: 'Threshold (r_th)',
      nameLocation: 'middle',
      nameGap: 24,
      nameTextStyle: { color: '#64748b', fontSize: 10 },
      data: thresholds,
      axisLine: { lineStyle: { color: '#334155' } },
      axisLabel: { color: '#94a3b8', fontSize: 10 },
      splitLine: { show: false },
    },
    yAxis: [
      {
        type: 'value',
        name: 'Percentage (%)',
        min: 0,
        max: 100,
        axisLine: { lineStyle: { color: '#334155' } },
        splitLine: { lineStyle: { color: '#1e293b' } },
        axisLabel: { color: '#94a3b8', fontSize: 10, formatter: '{value}%' },
      },
      {
        type: 'value',
        name: 'F1 Score',
        min: 0,
        max: 0.5,
        position: 'right',
        axisLine: { lineStyle: { color: '#334155' } },
        splitLine: { show: false },
        axisLabel: { color: '#94a3b8', fontSize: 10 },
      },
    ],
    series: [
      {
        name: 'Recall (%)',
        type: 'line',
        data: recall,
        smooth: true,
        showSymbol: false,
        lineStyle: { width: 2, color: '#38bdf8' },
        markLine: {
          silent: true,
          symbol: 'none',
          data: [
            {
              xAxis: '0.65',
              lineStyle: { color: '#f59e0b', type: 'dashed', width: 2 },
              label: { formatter: 'Balanced (0.65)', color: '#f59e0b', fontSize: 10, position: 'insideEndTop' },
            },
            {
              xAxis: '0.48',
              lineStyle: { color: '#ef4444', type: 'dotted', width: 1.5 },
              label: { formatter: 'High-Sens (0.48)', color: '#ef4444', fontSize: 9, position: 'insideEndTop' },
            },
          ],
        },
      },
      {
        name: 'Precision (%)',
        type: 'line',
        data: precision,
        smooth: true,
        showSymbol: false,
        lineStyle: { width: 2, color: '#10b981' },
      },
      {
        name: 'Specificity (%)',
        type: 'line',
        data: specificity,
        smooth: true,
        showSymbol: false,
        lineStyle: { width: 1.5, color: '#a855f7', type: 'dashed' },
      },
      {
        name: 'F1 Score',
        type: 'line',
        yAxisIndex: 1,
        data: f1,
        smooth: true,
        showSymbol: false,
        lineStyle: { width: 2.5, color: '#f59e0b' },
      },
    ],
  };

  return <ReactECharts option={option} style={{ height, width: '100%' }} />;
};
