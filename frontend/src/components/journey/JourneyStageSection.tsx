import React, { useState } from 'react';
import { ChevronDown, ChevronUp, CheckCircle2 } from 'lucide-react';
import { JourneyMilestone, JourneyStage, MilestoneStatus } from '../../types';
import { Badge } from '../ui/Badge';
import { MilestoneItemCard } from './MilestoneItemCard';

interface JourneyStageSectionProps {
  stage: JourneyStage;
  onSelectMilestone: (milestone: JourneyMilestone) => void;
  onToggleStatus: (milestoneId: string, currentStatus: MilestoneStatus) => void;
}

export const JourneyStageSection: React.FC<JourneyStageSectionProps> = ({
  stage,
  onSelectMilestone,
  onToggleStatus,
}) => {
  const [isOpen, setIsOpen] = useState(true);

  const isCompleted = stage.status === 'completed';
  const isActive = stage.status === 'in_progress';

  return (
    <section className="bg-white rounded-3xl border border-stone-200/80 shadow-warm-sm overflow-hidden transition-all">
      {/* Stage Header */}
      <div
        onClick={() => setIsOpen(!isOpen)}
        className={`p-5 sm:p-6 cursor-pointer flex flex-col sm:flex-row sm:items-center justify-between gap-4 transition ${
          isActive
            ? 'bg-teal-50/30'
            : isCompleted
            ? 'bg-sage-50/20'
            : 'bg-white hover:bg-stone-50/50'
        }`}
      >
        <div className="flex items-start sm:items-center gap-3.5 min-w-0">
          {/* Stage Number Icon */}
          <div
            className={`w-10 h-10 rounded-2xl flex items-center justify-center font-heading font-bold text-sm shadow-warm-xs flex-shrink-0 ${
              isCompleted
                ? 'bg-sage-600 text-white'
                : isActive
                ? 'bg-teal-900 text-white'
                : 'bg-stone-100 text-charcoal-700'
            }`}
          >
            {isCompleted ? <CheckCircle2 className="w-5 h-5" /> : stage.stage_number}
          </div>

          <div className="min-w-0 space-y-1">
            <div className="flex items-center gap-2 flex-wrap">
              <h3 className="font-heading font-bold text-base sm:text-lg text-teal-900 truncate">
                Stage {stage.stage_number}: {stage.title}
              </h3>
              <span className="text-xs font-semibold text-charcoal-600 bg-stone-100 px-2.5 py-0.5 rounded-full">
                {stage.age_range_label}
              </span>
            </div>
            <p className="text-xs text-charcoal-600 line-clamp-1">{stage.description}</p>
          </div>
        </div>

        {/* Stage Progress Summary & Accordion Toggle */}
        <div className="flex items-center justify-between sm:justify-end gap-3 flex-shrink-0">
          <div className="text-right">
            <div className="text-[11px] font-bold text-charcoal-500">
              {stage.completed_milestones} of {stage.total_milestones} Done
            </div>
            <div className="text-xs font-bold text-teal-900">{stage.progress_percentage}%</div>
          </div>

          <Badge
            variant={isCompleted ? 'sage' : isActive ? 'coral' : 'stone'}
            size="sm"
          >
            {isCompleted ? 'Completed' : isActive ? 'Active Stage' : 'Upcoming'}
          </Badge>

          <button
            type="button"
            className="p-1 rounded-xl text-charcoal-400 hover:text-teal-900 hover:bg-stone-100 transition"
            aria-label={isOpen ? 'Collapse stage' : 'Expand stage'}
          >
            {isOpen ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Milestones List */}
      {isOpen && (
        <div className="p-4 sm:p-6 pt-0 sm:pt-0 space-y-2.5 border-t border-stone-100 bg-ivory-50/20">
          {stage.milestones.length === 0 ? (
            <div className="py-6 text-center text-xs text-charcoal-500 font-medium">
              No milestones recorded for this stage yet.
            </div>
          ) : (
            stage.milestones.map((milestone) => (
              <MilestoneItemCard
                key={milestone.id}
                milestone={milestone}
                onSelect={onSelectMilestone}
                onToggleStatus={onToggleStatus}
              />
            ))
          )}
        </div>
      )}
    </section>
  );
};
