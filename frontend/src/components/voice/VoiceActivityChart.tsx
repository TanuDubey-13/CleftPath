import React from 'react';
import { VoiceSession } from '../../types';
import { Card } from '../ui/Card';

interface VoiceActivityChartProps {
  sessions: VoiceSession[];
}

export const VoiceActivityChart: React.FC<VoiceActivityChartProps> = ({ sessions }) => {
  if (!sessions || sessions.length === 0) return null;

  // Aggregate practice seconds by date
  const dateMap = new Map<string, { date: string; seconds: number; count: number }>();

  sessions.forEach((s) => {
    const dStr = new Date(s.recorded_at).toISOString().slice(0, 10);
    const existing = dateMap.get(dStr) || { date: dStr, seconds: 0, count: 0 };
    existing.seconds += s.duration_seconds;
    existing.count += 1;
    dateMap.set(dStr, existing);
  });

  const dataPoints = Array.from(dateMap.values())
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
    .slice(-7); // Last 7 active days

  const maxSeconds = Math.max(...dataPoints.map((d) => d.seconds), 60);

  const chartHeight = 120;
  const chartWidth = 500;
  const padding = 28;

  return (
    <Card className="p-5 bg-white border border-stone-200/80 rounded-3xl space-y-3">
      <div className="flex items-center justify-between">
        <div>
          <h4 className="font-heading font-bold text-sm text-teal-900">
            Practice Activity
          </h4>
          <p className="text-[11px] text-charcoal-500">
            Daily practice duration recorded across sound exploration sessions.
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

          {/* Bar Chart Representation */}
          {dataPoints.map((dp, idx) => {
            const barWidth = 32;
            const availableWidth = chartWidth - padding * 2;
            const x =
              dataPoints.length === 1
                ? chartWidth / 2 - barWidth / 2
                : padding + (idx / (dataPoints.length - 1)) * (availableWidth - barWidth);
            const barHeight = Math.max(
              8,
              (dp.seconds / maxSeconds) * (chartHeight - padding * 2)
            );
            const y = chartHeight - padding - barHeight;

            return (
              <g key={idx} className="group">
                <rect
                  x={x}
                  y={y}
                  width={barWidth}
                  height={barHeight}
                  rx="6"
                  fill="#0F4C5C"
                  className="opacity-90 hover:opacity-100 transition"
                />
                {/* Value Label */}
                <text
                  x={x + barWidth / 2}
                  y={y - 5}
                  textAnchor="middle"
                  fontSize="10"
                  fontWeight="bold"
                  fill="#0F4C5C"
                >
                  {Math.round(dp.seconds / 60)}m
                </text>
                {/* Date Label */}
                <text
                  x={x + barWidth / 2}
                  y={chartHeight - 10}
                  textAnchor="middle"
                  fontSize="9"
                  fill="#6B7280"
                >
                  {new Date(dp.date).toLocaleDateString(undefined, {
                    month: 'numeric',
                    day: 'numeric',
                  })}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
    </Card>
  );
};
