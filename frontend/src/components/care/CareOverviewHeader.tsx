import React from 'react';
import { Milk, Scale, Clock, Plus } from 'lucide-react';
import { CareOverview } from '../../types';
import { Card } from '../ui/Card';

interface CareOverviewHeaderProps {
  overview?: CareOverview;
  onOpenFeedingModal: () => void;
  onOpenGrowthModal: () => void;
  onOpenNamModal: () => void;
}

export const CareOverviewHeader: React.FC<CareOverviewHeaderProps> = ({
  overview,
  onOpenFeedingModal,
  onOpenGrowthModal,
  onOpenNamModal,
}) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
      {/* Feeding Stat Card */}
      <Card className="p-5 bg-white border border-stone-200/80 rounded-3xl shadow-warm-xs flex flex-col justify-between gap-4">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <span className="text-[11px] font-bold text-teal-800 uppercase tracking-wider">
              Today's Feeding
            </span>
            <div className="flex items-baseline gap-1.5">
              <span className="font-heading font-extrabold text-2xl text-teal-900">
                {overview ? overview.today_feeding_volume_ml : 0}
              </span>
              <span className="text-xs font-semibold text-charcoal-500">ml</span>
            </div>
            <p className="text-[11px] text-charcoal-600">
              {overview ? overview.today_feeding_count : 0} sessions logged today
            </p>
          </div>
          <div className="w-10 h-10 rounded-2xl bg-coral-50 text-coral-600 flex items-center justify-center">
            <Milk className="w-5 h-5" />
          </div>
        </div>

        <button
          type="button"
          onClick={onOpenFeedingModal}
          className="text-xs font-bold text-teal-900 hover:text-coral-600 transition flex items-center gap-1 self-start"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Log Feeding</span>
        </button>
      </Card>

      {/* Growth Stat Card */}
      <Card className="p-5 bg-white border border-stone-200/80 rounded-3xl shadow-warm-xs flex flex-col justify-between gap-4">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <span className="text-[11px] font-bold text-teal-800 uppercase tracking-wider">
              Latest Weight
            </span>
            <div className="flex items-baseline gap-1.5">
              <span className="font-heading font-extrabold text-2xl text-teal-900">
                {overview?.latest_growth ? overview.latest_growth.weight_kg : '--'}
              </span>
              <span className="text-xs font-semibold text-charcoal-500">kg</span>
            </div>
            <p className="text-[11px] text-charcoal-600">
              {overview?.latest_growth
                ? `Measured on ${new Date(overview.latest_growth.recorded_at).toLocaleDateString()}`
                : 'No measurements yet'}
            </p>
          </div>
          <div className="w-10 h-10 rounded-2xl bg-teal-50 text-teal-900 flex items-center justify-center">
            <Scale className="w-5 h-5" />
          </div>
        </div>

        <button
          type="button"
          onClick={onOpenGrowthModal}
          className="text-xs font-bold text-teal-900 hover:text-coral-600 transition flex items-center gap-1 self-start"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Record Weight</span>
        </button>
      </Card>

      {/* NAM / Taping Stat Card */}
      <Card className="p-5 bg-white border border-stone-200/80 rounded-3xl shadow-warm-xs flex flex-col justify-between gap-4">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <span className="text-[11px] font-bold text-teal-800 uppercase tracking-wider">
              Today's NAM Wear
            </span>
            <div className="flex items-baseline gap-1.5">
              <span className="font-heading font-extrabold text-2xl text-teal-900">
                {overview ? overview.today_nam_hours : 0}
              </span>
              <span className="text-xs font-semibold text-charcoal-500">/ 24 hrs</span>
            </div>
            <p className="text-[11px] text-charcoal-600">
              {overview?.latest_nam_log
                ? `Last logged on ${new Date(overview.latest_nam_log.logged_at).toLocaleDateString()}`
                : 'No logs recorded yet'}
            </p>
          </div>
          <div className="w-10 h-10 rounded-2xl bg-sage-50 text-sage-800 flex items-center justify-center">
            <Clock className="w-5 h-5" />
          </div>
        </div>

        <button
          type="button"
          onClick={onOpenNamModal}
          className="text-xs font-bold text-teal-900 hover:text-coral-600 transition flex items-center gap-1 self-start"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Log NAM Usage</span>
        </button>
      </Card>
    </div>
  );
};
