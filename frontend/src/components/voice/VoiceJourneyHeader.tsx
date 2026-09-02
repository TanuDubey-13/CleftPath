import React from 'react';
import { Mic, Clock, Sparkles, Plus } from 'lucide-react';
import { VoiceOverview } from '../../types';
import { Card } from '../ui/Card';

interface VoiceJourneyHeaderProps {
  overview?: VoiceOverview;
  onOpenQuickPractice: () => void;
}

export const VoiceJourneyHeader: React.FC<VoiceJourneyHeaderProps> = ({
  overview,
  onOpenQuickPractice,
}) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
      {/* Total Sessions Card */}
      <Card className="p-5 bg-white border border-stone-200/80 rounded-3xl shadow-warm-xs flex flex-col justify-between gap-4">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <span className="text-[11px] font-bold text-teal-800 uppercase tracking-wider">
              Practice Sessions
            </span>
            <div className="flex items-baseline gap-1.5">
              <span className="font-heading font-extrabold text-2xl text-teal-900">
                {overview ? overview.total_sessions_count : 0}
              </span>
              <span className="text-xs font-semibold text-charcoal-500">completed</span>
            </div>
            <p className="text-[11px] text-charcoal-600">
              {overview?.last_session
                ? `Last practiced ${new Date(overview.last_session.recorded_at).toLocaleDateString()}`
                : 'No sessions logged yet'}
            </p>
          </div>
          <div className="w-10 h-10 rounded-2xl bg-teal-50 text-teal-900 flex items-center justify-center">
            <Mic className="w-5 h-5" />
          </div>
        </div>

        <button
          type="button"
          onClick={onOpenQuickPractice}
          className="text-xs font-bold text-teal-900 hover:text-coral-600 transition flex items-center gap-1 self-start"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Quick Record Session</span>
        </button>
      </Card>

      {/* Total Practice Time Card */}
      <Card className="p-5 bg-white border border-stone-200/80 rounded-3xl shadow-warm-xs flex flex-col justify-between gap-4">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <span className="text-[11px] font-bold text-teal-800 uppercase tracking-wider">
              Total Practice Time
            </span>
            <div className="flex items-baseline gap-1.5">
              <span className="font-heading font-extrabold text-2xl text-teal-900">
                {overview ? overview.total_practice_minutes : 0}
              </span>
              <span className="text-xs font-semibold text-charcoal-500">minutes</span>
            </div>
            <p className="text-[11px] text-charcoal-600">
              Across all home practice routines
            </p>
          </div>
          <div className="w-10 h-10 rounded-2xl bg-coral-50 text-coral-600 flex items-center justify-center">
            <Clock className="w-5 h-5" />
          </div>
        </div>
      </Card>

      {/* Unique Exercises Practiced */}
      <Card className="p-5 bg-white border border-stone-200/80 rounded-3xl shadow-warm-xs flex flex-col justify-between gap-4">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <span className="text-[11px] font-bold text-teal-800 uppercase tracking-wider">
              Exercises Explored
            </span>
            <div className="flex items-baseline gap-1.5">
              <span className="font-heading font-extrabold text-2xl text-teal-900">
                {overview ? overview.unique_exercises_practiced : 0}
              </span>
              <span className="text-xs font-semibold text-charcoal-500">sound activities</span>
            </div>
            <p className="text-[11px] text-charcoal-600">
              Phoneme awareness & play games
            </p>
          </div>
          <div className="w-10 h-10 rounded-2xl bg-sage-50 text-sage-800 flex items-center justify-center">
            <Sparkles className="w-5 h-5" />
          </div>
        </div>
      </Card>
    </div>
  );
};
