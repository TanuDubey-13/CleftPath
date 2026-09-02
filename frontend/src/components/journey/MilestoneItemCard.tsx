import React from 'react';
import { CheckCircle2, Circle, Clock, MessageSquare, ChevronRight } from 'lucide-react';
import { JourneyMilestone, MilestoneStatus } from '../../types';
import { Badge } from '../ui/Badge';

interface MilestoneItemCardProps {
  milestone: JourneyMilestone;
  onSelect: (milestone: JourneyMilestone) => void;
  onToggleStatus: (milestoneId: string, currentStatus: MilestoneStatus) => void;
}

export const MilestoneItemCard: React.FC<MilestoneItemCardProps> = ({
  milestone,
  onSelect,
  onToggleStatus,
}) => {
  const isCompleted = milestone.status === 'completed';
  const isInProgress = milestone.status === 'in_progress';

  const handleStatusToggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    onToggleStatus(milestone.id, milestone.status);
  };

  return (
    <div
      onClick={() => onSelect(milestone)}
      className={`group relative p-4 rounded-2xl border transition cursor-pointer flex flex-col sm:flex-row sm:items-center justify-between gap-3 ${
        isCompleted
          ? 'bg-sage-50/40 border-sage-200/80 hover:bg-sage-50/70'
          : isInProgress
          ? 'bg-teal-50/40 border-teal-200/80 hover:bg-teal-50/70 shadow-warm-xs'
          : 'bg-white border-stone-200/70 hover:border-teal-700/40 hover:bg-stone-50/50'
      }`}
    >
      {/* Left Column: Status Check Trigger & Info */}
      <div className="flex items-start sm:items-center gap-3 min-w-0">
        <button
          type="button"
          onClick={handleStatusToggle}
          title={isCompleted ? 'Mark upcoming' : 'Mark completed'}
          className={`p-1 rounded-full transition flex-shrink-0 mt-0.5 sm:mt-0 ${
            isCompleted
              ? 'text-sage-600 hover:text-charcoal-400'
              : isInProgress
              ? 'text-teal-900 hover:text-sage-600'
              : 'text-stone-300 hover:text-sage-600'
          }`}
        >
          {isCompleted ? (
            <CheckCircle2 className="w-5 h-5 fill-sage-100" />
          ) : isInProgress ? (
            <Clock className="w-5 h-5" />
          ) : (
            <Circle className="w-5 h-5" />
          )}
        </button>

        <div className="min-w-0 space-y-0.5">
          <div className="flex items-center gap-2 flex-wrap">
            <h4
              className={`text-sm font-bold truncate ${
                isCompleted ? 'text-charcoal-700 line-through opacity-80' : 'text-charcoal-900'
              }`}
            >
              {milestone.title}
            </h4>
            {milestone.target_age_months !== null && milestone.target_age_months !== undefined && (
              <span className="text-[10px] font-semibold text-charcoal-500 bg-stone-100 px-2 py-0.5 rounded-full">
                {milestone.target_age_months === 0
                  ? 'At Birth'
                  : `${milestone.target_age_months}m target`}
              </span>
            )}
          </div>
          <p className="text-xs text-charcoal-600 line-clamp-1">{milestone.description}</p>
        </div>
      </div>

      {/* Right Column: Badges & Details Action */}
      <div className="flex items-center justify-between sm:justify-end gap-2.5 flex-shrink-0 pt-2 sm:pt-0 border-t sm:border-t-0 border-stone-100">
        {milestone.notes_count > 0 && (
          <div className="flex items-center gap-1 text-[11px] font-semibold text-charcoal-600 bg-white/80 px-2.5 py-1 rounded-xl border border-stone-200/60">
            <MessageSquare className="w-3.5 h-3.5 text-coral-500" />
            <span>{milestone.notes_count}</span>
          </div>
        )}

        <Badge
          variant={isCompleted ? 'sage' : isInProgress ? 'teal' : 'stone'}
          size="sm"
        >
          {isCompleted ? 'Completed' : isInProgress ? 'In Progress' : 'Upcoming'}
        </Badge>

        <ChevronRight className="w-4 h-4 text-charcoal-400 group-hover:text-teal-900 group-hover:translate-x-0.5 transition" />
      </div>
    </div>
  );
};
