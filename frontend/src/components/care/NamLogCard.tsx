import React from 'react';
import { Clock, CheckCircle2, Edit2, Trash2 } from 'lucide-react';
import { NAMTapingLog } from '../../types';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';

interface NamLogCardProps {
  log: NAMTapingLog;
  onEdit: (log: NAMTapingLog) => void;
  onDelete: (logId: string) => void;
}

export const NamLogCard: React.FC<NamLogCardProps> = ({
  log,
  onEdit,
  onDelete,
}) => {
  const dateObj = new Date(log.logged_at);
  const formattedDate = dateObj.toLocaleDateString(undefined, {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
  });

  return (
    <Card className="p-4 bg-white border border-stone-200/80 rounded-3xl hover:border-teal-700/30 hover:shadow-warm-xs transition flex flex-col justify-between gap-3">
      <div className="space-y-2.5">
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-1.5 text-xs font-bold text-teal-900 bg-teal-50 px-2.5 py-1 rounded-xl">
            <Clock className="w-3.5 h-3.5 text-teal-900" />
            <span>{formattedDate}</span>
          </div>

          <Badge variant={log.skin_condition === 'normal' ? 'sage' : 'coral'} size="sm">
            Skin: {log.skin_condition.replace(/_/g, ' ').toUpperCase()}
          </Badge>
        </div>

        {/* Hours Worn Highlight */}
        <div className="flex items-baseline gap-1.5">
          <span className="font-heading font-extrabold text-2xl text-teal-900">
            {log.hours_worn}
          </span>
          <span className="text-xs font-bold text-charcoal-500">/ 24 hrs recorded</span>
        </div>

        {/* Status Indicators */}
        <div className="flex flex-wrap gap-2 text-xs">
          {log.tape_changed && (
            <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-teal-800 bg-teal-50/80 px-2.5 py-1 rounded-lg border border-teal-100">
              <CheckCircle2 className="w-3 h-3 text-teal-900" />
              <span>Tape Changed</span>
            </span>
          )}
          {log.appliance_cleaned && (
            <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-sage-800 bg-sage-50/80 px-2.5 py-1 rounded-lg border border-sage-100">
              <CheckCircle2 className="w-3 h-3 text-sage-700" />
              <span>Appliance Cleaned</span>
            </span>
          )}
        </div>

        {log.notes && (
          <p className="text-[11px] text-charcoal-600 bg-stone-50 p-2.5 rounded-xl border border-stone-100">
            {log.notes}
          </p>
        )}
      </div>

      {/* Actions */}
      <div className="pt-2 border-t border-stone-100 flex items-center justify-end gap-2 text-xs">
        <button
          type="button"
          onClick={() => onEdit(log)}
          className="p-1.5 text-charcoal-500 hover:text-teal-900 hover:bg-teal-50 rounded-lg transition"
          aria-label="Edit NAM log"
        >
          <Edit2 className="w-3.5 h-3.5" />
        </button>
        <button
          type="button"
          onClick={() => onDelete(log.id)}
          className="p-1.5 text-charcoal-500 hover:text-coral-600 hover:bg-coral-50 rounded-lg transition"
          aria-label="Delete NAM log"
        >
          <Trash2 className="w-3.5 h-3.5" />
        </button>
      </div>
    </Card>
  );
};
