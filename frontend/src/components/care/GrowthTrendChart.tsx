import React from 'react';
import { GrowthRecord } from '../../types';
import { Card } from '../ui/Card';

interface GrowthTrendChartProps {
  records: GrowthRecord[];
}

export const GrowthTrendChart: React.FC<GrowthTrendChartProps> = ({ records }) => {
  if (!records || records.length === 0) return null;

  // Sort ascending by date for timeline rendering
  const sorted = [...records].sort(
    (a, b) => new Date(a.recorded_at).getTime() - new Date(b.recorded_at).getTime()
  );

  const weights = sorted.map((r) => Number(r.weight_kg));
  const minWeight = Math.min(...weights);
  const maxWeight = Math.max(...weights);
  const range = maxWeight - minWeight === 0 ? 1 : maxWeight - minWeight;

  const chartHeight = 120;
  const chartWidth = 500;
  const padding = 24;

  const points = sorted.map((r, i) => {
    const x =
      sorted.length === 1
        ? chartWidth / 2
        : padding + (i / (sorted.length - 1)) * (chartWidth - padding * 2);
    const weight = Number(r.weight_kg);
    const y =
      chartHeight - padding - ((weight - minWeight) / range) * (chartHeight - padding * 2);
    return { x, y, weight, date: r.recorded_at };
  });

  const pathD =
    points.length > 1
      ? points.reduce(
          (acc, p, i) => (i === 0 ? `M ${p.x} ${p.y}` : `${acc} L ${p.x} ${p.y}`),
          ''
        )
      : '';

  return (
    <Card className="p-5 bg-white border border-stone-200/80 rounded-3xl space-y-3">
      <div className="flex items-center justify-between">
        <div>
          <h4 className="font-heading font-bold text-sm text-teal-900">
            Recorded Weight History
          </h4>
          <p className="text-[11px] text-charcoal-500">
            Physical measurements recorded across care visits.
          </p>
        </div>
      </div>

      <div className="w-full overflow-x-auto py-2">
        <svg
          viewBox={`0 0 ${chartWidth} ${chartHeight}`}
          className="w-full h-32 overflow-visible"
        >
          {/* Baseline Grid */}
          <line
            x1={padding}
            y1={chartHeight - padding}
            x2={chartWidth - padding}
            y2={chartHeight - padding}
            stroke="#e5e7eb"
            strokeDasharray="4 4"
          />

          {/* Trend Line */}
          {points.length > 1 && (
            <path
              d={pathD}
              fill="none"
              stroke="#0F4C5C"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          )}

          {/* Data Points */}
          {points.map((p, idx) => (
            <g key={idx} className="group">
              <circle
                cx={p.x}
                cy={p.y}
                r="4.5"
                fill="#E07A5F"
                stroke="#ffffff"
                strokeWidth="2"
              />
              {/* Point Label */}
              <text
                x={p.x}
                y={p.y - 8}
                textAnchor="middle"
                fontSize="10"
                fontWeight="bold"
                fill="#0F4C5C"
              >
                {p.weight} kg
              </text>
              <text
                x={p.x}
                y={chartHeight - 8}
                textAnchor="middle"
                fontSize="9"
                fill="#6B7280"
              >
                {new Date(p.date).toLocaleDateString(undefined, {
                  month: 'numeric',
                  day: 'numeric',
                })}
              </text>
            </g>
          ))}
        </svg>
      </div>
    </Card>
  );
};
