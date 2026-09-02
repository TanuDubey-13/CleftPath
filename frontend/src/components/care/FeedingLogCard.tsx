import React from 'react';
import { Clock, Edit2, Trash2 } from 'lucide-react';
import { FeedingBottleType, FeedingLog, RefluxSeverity } from '../../types';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';

interface FeedingLogCardProps {
  log: FeedingLog;
  onEdit: (log: FeedingLog) => void;
  onDelete: (logId: string) => void;
}

const BOTTLE_LABELS: Record<FeedingBottleType, string> = {
  dr_browns_specialty: "Dr. Brown's Specialty Feeder",
  pigeon_cleft: 'Pigeon Cleft Feeder',
  medela_specialneeds_haberman: 'Medela SpecialNeeds (Haberman)',
  syringe_with_tubing: 'Syringe with Tubing',
  supplemental_nursing: 'Supplemental Nursing System (SNS)',
  cup_open: 'Open Cup',
  standard_bottle: 'Standard Bottle',
  other: 'Other Method',
};

const REFLUX_BADGE_VARIANT: Record<RefluxSeverity, 'stone' | 'teal' | 'coral'> = {
  none: 'stone',
  mild: 'teal',
  moderate: 'coral',
  severe: 'coral',
};

export const FeedingLogCard: React.FC<FeedingLogCardProps> = ({
  log,
  onEdit,
  onDelete,
}) => {
  const dateObj = new Date(log.logged_at);
  const formattedTime = dateObj.toLocaleTimeString(undefined, {
    hour: 'numeric',
    minute: '2-digit',
  });
  const formattedDate = dateObj.toLocaleDateString(undefined, {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
  });

  return (
    <Card className="p-4 bg-white border border-stone-200/80 rounded-3xl hover:border-teal-700/30 hover:shadow-warm-xs transition flex flex-col justify-between gap-3">
      <div className="space-y-2.5">
        {/* Top Header: Time & Method */}
        <div className="flex items-center justify-between gap-2 flex-wrap">
          <div className="flex items-center gap-2 text-xs font-bold text-teal-900 bg-teal-50 px-2.5 py-1 rounded-xl">
            <Clock className="w-3.5 h-3.5 text-teal-900" />
            <span>{formattedDate}, {formattedTime}</span>
          </div>

          <Badge variant={REFLUX_BADGE_VARIANT[log.reflux_severity] || 'stone'} size="sm">
            Reflux: {log.reflux_severity.toUpperCase()}
          </Badge>
        </div>

        {/* Volume & Duration */}
        <div className="flex items-baseline justify-between pt-1">
          <div>
            <span className="font-heading font-extrabold text-xl text-charcoal-900">
              {log.volume_ml}
            </span>
            <span className="text-xs font-semibold text-charcoal-500 ml-1">ml</span>
          </div>
          <span className="text-xs font-medium text-charcoal-600">
            {log.duration_minutes} min • {log.burping_breaks} burps
          </span>
        </div>

        <p className="text-xs font-semibold text-teal-900 truncate">
          {BOTTLE_LABELS[log.bottle_type] || log.bottle_type}
        </p>

        {log.notes && (
          <p className="text-[11px] text-charcoal-600 bg-stone-50 p-2.5 rounded-xl border border-stone-100">
            {log.notes}
          </p>
        )}
      </div>

      {/* Card Actions */}
      <div className="pt-2 border-t border-stone-100 flex items-center justify-end gap-2 text-xs">
        <button
          type="button"
          onClick={() => onEdit(log)}
          className="p-1.5 text-charcoal-500 hover:text-teal-900 hover:bg-teal-50 rounded-lg transition"
          aria-label="Edit feeding session"
        >
          <Edit2 className="w-3.5 h-3.5" />
        </button>
        <button
          type="button"
          onClick={() => onDelete(log.id)}
          className="p-1.5 text-charcoal-500 hover:text-coral-600 hover:bg-coral-50 rounded-lg transition"
          aria-label="Delete feeding session"
        >
          <Trash2 className="w-3.5 h-3.5" />
        </button>
      </div>
    </Card>
  );
};
