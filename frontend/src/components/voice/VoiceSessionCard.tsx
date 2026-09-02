import React from 'react';
import { Clock, Edit2, Trash2 } from 'lucide-react';
import { VoiceSession } from '../../types';
import { Card } from '../ui/Card';

interface VoiceSessionCardProps {
  session: VoiceSession;
  onEdit: (session: VoiceSession) => void;
  onDelete: (sessionId: string) => void;
}

export const VoiceSessionCard: React.FC<VoiceSessionCardProps> = ({
  session,
  onEdit,
  onDelete,
}) => {
  const dateObj = new Date(session.recorded_at);
  const formattedDate = dateObj.toLocaleDateString(undefined, {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
  });
  const formattedTime = dateObj.toLocaleTimeString(undefined, {
    hour: 'numeric',
    minute: '2-digit',
  });

  return (
    <Card className="p-4 bg-white border border-stone-200/80 rounded-3xl hover:border-teal-700/30 hover:shadow-warm-xs transition flex flex-col justify-between gap-3">
      <div className="space-y-2.5">
        {/* Header */}
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-1.5 text-xs font-bold text-teal-900 bg-teal-50 px-2.5 py-1 rounded-xl">
            <Clock className="w-3.5 h-3.5 text-teal-900" />
            <span>{formattedDate}, {formattedTime}</span>
          </div>

          <div className="flex items-center gap-1">
            <button
              type="button"
              onClick={() => onEdit(session)}
              className="p-1.5 text-charcoal-400 hover:text-teal-900 hover:bg-teal-50 rounded-lg transition"
              aria-label="Edit voice session"
            >
              <Edit2 className="w-3.5 h-3.5" />
            </button>
            <button
              type="button"
              onClick={() => onDelete(session.id)}
              className="p-1.5 text-charcoal-400 hover:text-coral-600 hover:bg-coral-50 rounded-lg transition"
              aria-label="Delete voice session"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Exercise Title */}
        <div>
          <h4 className="font-heading font-bold text-sm text-teal-900 leading-snug">
            {session.exercise ? session.exercise.title : 'General Speech Practice'}
          </h4>
          <span className="text-xs font-semibold text-charcoal-500">
            {session.duration_seconds} seconds • {session.repetition_count} reps
          </span>
        </div>

        {/* Notes */}
        {session.parent_notes && (
          <p className="text-[11px] text-charcoal-600 bg-stone-50 p-2.5 rounded-xl border border-stone-100">
            {session.parent_notes}
          </p>
        )}
      </div>
    </Card>
  );
};
