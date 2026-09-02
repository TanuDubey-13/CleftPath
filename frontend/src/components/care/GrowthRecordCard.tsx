import React from 'react';
import { Calendar, Edit2, Trash2 } from 'lucide-react';
import { GrowthRecord } from '../../types';
import { Card } from '../ui/Card';

interface GrowthRecordCardProps {
  record: GrowthRecord;
  onEdit: (record: GrowthRecord) => void;
  onDelete: (recordId: string) => void;
}

export const GrowthRecordCard: React.FC<GrowthRecordCardProps> = ({
  record,
  onEdit,
  onDelete,
}) => {
  const formattedDate = new Date(record.recorded_at).toLocaleDateString(undefined, {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });

  return (
    <Card className="p-4 bg-white border border-stone-200/80 rounded-3xl hover:border-teal-700/30 hover:shadow-warm-xs transition flex flex-col justify-between gap-3">
      <div className="space-y-2.5">
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-1.5 text-xs font-bold text-teal-900 bg-teal-50 px-2.5 py-1 rounded-xl">
            <Calendar className="w-3.5 h-3.5 text-teal-900" />
            <span>{formattedDate}</span>
          </div>

          <div className="flex items-center gap-1">
            <button
              type="button"
              onClick={() => onEdit(record)}
              className="p-1.5 text-charcoal-400 hover:text-teal-900 hover:bg-teal-50 rounded-lg transition"
              aria-label="Edit growth measurement"
            >
              <Edit2 className="w-3.5 h-3.5" />
            </button>
            <button
              type="button"
              onClick={() => onDelete(record.id)}
              className="p-1.5 text-charcoal-400 hover:text-coral-600 hover:bg-coral-50 rounded-lg transition"
              aria-label="Delete growth measurement"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Weight Highlight */}
        <div className="flex items-baseline gap-1.5">
          <span className="font-heading font-extrabold text-2xl text-teal-900">
            {record.weight_kg}
          </span>
          <span className="text-xs font-bold text-charcoal-500">kg</span>
        </div>

        {/* Secondary Metrics */}
        <div className="grid grid-cols-2 gap-2 text-xs text-charcoal-600 bg-stone-50 p-2.5 rounded-xl border border-stone-100">
          <div>
            <span className="text-[10px] text-charcoal-400 block uppercase">Length / Height</span>
            <span className="font-bold text-charcoal-800">
              {record.height_cm ? `${record.height_cm} cm` : '--'}
            </span>
          </div>
          <div>
            <span className="text-[10px] text-charcoal-400 block uppercase">Head Circumf.</span>
            <span className="font-bold text-charcoal-800">
              {record.head_circumference_cm ? `${record.head_circumference_cm} cm` : '--'}
            </span>
          </div>
        </div>
      </div>
    </Card>
  );
};
