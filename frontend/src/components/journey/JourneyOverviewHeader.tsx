import React from 'react';
import { Compass, CheckCircle2, Clock, Calendar, Sparkles } from 'lucide-react';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { ProgressBar } from '../ui/ProgressBar';
import { JourneyPatientSummary, JourneySummary } from '../../types';

interface JourneyOverviewHeaderProps {
  patient: JourneyPatientSummary | null;
  summary: JourneySummary;
}

export const JourneyOverviewHeader: React.FC<JourneyOverviewHeaderProps> = ({
  patient,
  summary,
}) => {
  return (
    <Card className="p-5 sm:p-6 bg-gradient-to-br from-white to-ivory-100/60 border border-stone-200/80 shadow-warm-sm">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-stone-100">
        <div className="space-y-1">
          <div className="flex items-center gap-2 flex-wrap">
            <h1 className="font-heading font-bold text-xl sm:text-2xl text-teal-900">
              {patient ? `${patient.display_name}’s Care Journey` : 'Longitudinal Cleft Journey'}
            </h1>
            {summary.current_stage_title && (
              <Badge variant="teal" size="sm">
                Stage {summary.current_stage_number}: {summary.current_stage_title}
              </Badge>
            )}
          </div>
          <p className="text-xs text-charcoal-600">
            {patient
              ? `Born ${new Date(patient.date_of_birth).toLocaleDateString()} • ${patient.cleft_lip.replace(/_/g, ' ')}`
              : 'ACPA Evidence-Grounded Longitudinal Care Roadmap'}
          </p>
        </div>

        {/* Overall Completion Percentage Badge */}
        <div className="flex items-center gap-3 bg-teal-50 px-3.5 py-2 rounded-2xl border border-teal-100">
          <Compass className="w-5 h-5 text-teal-900 flex-shrink-0" />
          <div>
            <div className="text-[11px] font-bold text-teal-900 uppercase tracking-wider">
              Roadmap Progress
            </div>
            <div className="text-lg font-heading font-bold text-teal-900">
              {summary.overall_progress_percentage}%
            </div>
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="py-4">
        <ProgressBar
          progress={summary.overall_progress_percentage}
          variant="teal"
          size="md"
          showLabel
        />
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
        <div className="p-3 bg-white rounded-xl border border-stone-100 shadow-sm flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-stone-100 text-charcoal-700 flex items-center justify-center font-bold text-xs">
            <Calendar className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[11px] text-charcoal-500 font-medium">Total Milestones</div>
            <div className="text-base font-bold text-charcoal-900">{summary.total_milestones}</div>
          </div>
        </div>

        <div className="p-3 bg-white rounded-xl border border-stone-100 shadow-sm flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-sage-50 text-sage-700 flex items-center justify-center font-bold text-xs">
            <CheckCircle2 className="w-4 h-4 text-sage-600" />
          </div>
          <div>
            <div className="text-[11px] text-charcoal-500 font-medium">Completed</div>
            <div className="text-base font-bold text-sage-700">{summary.completed_milestones}</div>
          </div>
        </div>

        <div className="p-3 bg-white rounded-xl border border-stone-100 shadow-sm flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-teal-50 text-teal-900 flex items-center justify-center font-bold text-xs">
            <Clock className="w-4 h-4 text-teal-900" />
          </div>
          <div>
            <div className="text-[11px] text-charcoal-500 font-medium">In Progress</div>
            <div className="text-base font-bold text-teal-900">{summary.in_progress_milestones}</div>
          </div>
        </div>

        <div className="p-3 bg-white rounded-xl border border-stone-100 shadow-sm flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-coral-50 text-coral-700 flex items-center justify-center font-bold text-xs">
            <Sparkles className="w-4 h-4 text-coral-500" />
          </div>
          <div>
            <div className="text-[11px] text-charcoal-500 font-medium">Upcoming</div>
            <div className="text-base font-bold text-coral-600">{summary.upcoming_milestones}</div>
          </div>
        </div>
      </div>
    </Card>
  );
};
