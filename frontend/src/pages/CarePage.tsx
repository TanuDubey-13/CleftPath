import React, { useState } from 'react';
import { HeartHandshake, Milk, Scale, Clock, Sparkles, CheckCircle2 } from 'lucide-react';
import {
  useCareOverview,
  useCreateFeedingLog,
  useCreateGrowthRecord,
  useCreateNAMLog,
} from '../hooks/useCare';
import {
  FeedingLogCreateRequest,
  GrowthRecordCreateRequest,
  NAMTapingLogCreateRequest,
} from '../types';
import { CareOverviewHeader } from '../components/care/CareOverviewHeader';
import { CareSafetyNotice } from '../components/care/CareSafetyNotice';
import { FeedingTracker } from '../components/care/FeedingTracker';
import { GrowthTracker } from '../components/care/GrowthTracker';
import { NamTracker } from '../components/care/NamTracker';
import { FeedingLogModal } from '../components/care/FeedingLogModal';
import { GrowthRecordModal } from '../components/care/GrowthRecordModal';
import { NamLogModal } from '../components/care/NamLogModal';
import { CareSkeleton } from '../components/care/CareSkeleton';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Alert } from '../components/ui/Alert';

type CareTab = 'overview' | 'feeding' | 'growth' | 'nam';

export const CarePage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<CareTab>('overview');

  const [isFeedingModalOpen, setIsFeedingModalOpen] = useState(false);
  const [isGrowthModalOpen, setIsGrowthModalOpen] = useState(false);
  const [isNamModalOpen, setIsNamModalOpen] = useState(false);

  const { data: overview, isLoading, isError, error, refetch } = useCareOverview();

  const createFeedingMutation = useCreateFeedingLog();
  const createGrowthMutation = useCreateGrowthRecord();
  const createNamMutation = useCreateNAMLog();

  const handleCreateFeeding = async (data: FeedingLogCreateRequest) => {
    await createFeedingMutation.mutateAsync(data);
  };

  const handleCreateGrowth = async (data: GrowthRecordCreateRequest) => {
    await createGrowthMutation.mutateAsync(data);
  };

  const handleCreateNam = async (data: NAMTapingLogCreateRequest) => {
    await createNamMutation.mutateAsync(data);
  };

  return (
    <div className="space-y-6 pb-12 animate-fade-in">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-teal-50 text-teal-900 flex items-center justify-center shadow-warm-xs">
            <HeartHandshake className="w-5 h-5 text-teal-900" />
          </div>
          <div>
            <h1 className="font-heading font-bold text-2xl text-teal-900">
              Baby & Parent Care
            </h1>
            <p className="text-xs text-charcoal-600">
              Structured daily tracking for specialty feeding, physical growth, and NAM appliance care.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsFeedingModalOpen(true)}
            leftIcon={<Milk className="w-3.5 h-3.5" />}
          >
            Log Feed
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsGrowthModalOpen(true)}
            leftIcon={<Scale className="w-3.5 h-3.5" />}
          >
            Log Weight
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsNamModalOpen(true)}
            leftIcon={<Clock className="w-3.5 h-3.5" />}
          >
            Log NAM
          </Button>
        </div>
      </div>

      {/* Safety Notice */}
      <CareSafetyNotice />

      {/* Content */}
      {isLoading ? (
        <CareSkeleton />
      ) : isError ? (
        <div className="max-w-2xl mx-auto py-12 space-y-4">
          <Alert variant="danger" title="Unable to Load Care Overview">
            {error instanceof Error ? error.message : 'An error occurred while loading care metrics.'}
          </Alert>
          <div className="text-center">
            <Button variant="outline" size="md" onClick={() => refetch()}>
              Retry Loading
            </Button>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Quick Stats Banner */}
          <CareOverviewHeader
            overview={overview}
            onOpenFeedingModal={() => setIsFeedingModalOpen(true)}
            onOpenGrowthModal={() => setIsGrowthModalOpen(true)}
            onOpenNamModal={() => setIsNamModalOpen(true)}
          />

          {/* Tab Navigation Controls */}
          <div className="flex items-center gap-2 overflow-x-auto pb-1" role="tablist">
            <button
              type="button"
              role="tab"
              aria-selected={activeTab === 'overview'}
              onClick={() => setActiveTab('overview')}
              className={`px-4 py-2 rounded-2xl text-xs font-bold transition whitespace-nowrap flex items-center gap-1.5 ${
                activeTab === 'overview'
                  ? 'bg-teal-900 text-white shadow-warm-xs'
                  : 'bg-white text-charcoal-700 hover:bg-stone-50 border border-stone-200/80'
              }`}
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Daily Overview</span>
            </button>

            <button
              type="button"
              role="tab"
              aria-selected={activeTab === 'feeding'}
              onClick={() => setActiveTab('feeding')}
              className={`px-4 py-2 rounded-2xl text-xs font-bold transition whitespace-nowrap flex items-center gap-1.5 ${
                activeTab === 'feeding'
                  ? 'bg-teal-900 text-white shadow-warm-xs'
                  : 'bg-white text-charcoal-700 hover:bg-stone-50 border border-stone-200/80'
              }`}
            >
              <Milk className="w-3.5 h-3.5" />
              <span>Feeding Tracker</span>
            </button>

            <button
              type="button"
              role="tab"
              aria-selected={activeTab === 'growth'}
              onClick={() => setActiveTab('growth')}
              className={`px-4 py-2 rounded-2xl text-xs font-bold transition whitespace-nowrap flex items-center gap-1.5 ${
                activeTab === 'growth'
                  ? 'bg-teal-900 text-white shadow-warm-xs'
                  : 'bg-white text-charcoal-700 hover:bg-stone-50 border border-stone-200/80'
              }`}
            >
              <Scale className="w-3.5 h-3.5" />
              <span>Growth Records</span>
            </button>

            <button
              type="button"
              role="tab"
              aria-selected={activeTab === 'nam'}
              onClick={() => setActiveTab('nam')}
              className={`px-4 py-2 rounded-2xl text-xs font-bold transition whitespace-nowrap flex items-center gap-1.5 ${
                activeTab === 'nam'
                  ? 'bg-teal-900 text-white shadow-warm-xs'
                  : 'bg-white text-charcoal-700 hover:bg-stone-50 border border-stone-200/80'
              }`}
            >
              <Clock className="w-3.5 h-3.5" />
              <span>NAM & Taping</span>
            </button>
          </div>

          {/* Active Tab View */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Daily Guidance & Reminders */}
              <Card className="p-6 bg-white border border-stone-200/80 rounded-3xl space-y-4 shadow-warm-xs">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-xl bg-teal-50 text-teal-900 flex items-center justify-center">
                    <Sparkles className="w-4 h-4 text-teal-900" />
                  </div>
                  <div>
                    <h3 className="font-heading font-bold text-base text-teal-900">
                      Care Guidance & Best Practices
                    </h3>
                    <p className="text-[11px] text-charcoal-500">
                      General educational guidance to discuss with your healthcare team.
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {(overview?.guidance_notes || []).map((tip, idx) => (
                    <div
                      key={idx}
                      className="p-3.5 bg-ivory-50/70 border border-stone-200/70 rounded-2xl flex items-start gap-3"
                    >
                      <CheckCircle2 className="w-4 h-4 text-sage-700 flex-shrink-0 mt-0.5" />
                      <p className="text-xs text-charcoal-800 leading-relaxed font-medium">
                        {tip}
                      </p>
                    </div>
                  ))}
                </div>
              </Card>

              {/* Mini Feed & Growth Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Recent Feeding */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <h4 className="font-heading font-bold text-sm text-teal-900">
                      Recent Feeding Activity
                    </h4>
                    <button
                      type="button"
                      onClick={() => setActiveTab('feeding')}
                      className="text-xs font-bold text-teal-900 hover:text-coral-600 transition"
                    >
                      View All →
                    </button>
                  </div>
                  {overview?.last_feeding ? (
                    <Card className="p-4 bg-white border border-stone-200/80 rounded-3xl space-y-2">
                      <div className="flex justify-between text-xs">
                        <span className="font-bold text-teal-900">
                          {new Date(overview.last_feeding.logged_at).toLocaleTimeString(undefined, {
                            hour: 'numeric',
                            minute: '2-digit',
                          })}
                        </span>
                        <span className="font-bold text-coral-600">
                          {overview.last_feeding.volume_ml} ml
                        </span>
                      </div>
                      <p className="text-xs text-charcoal-600">
                        {overview.last_feeding.bottle_type.replace(/_/g, ' ')} • {overview.last_feeding.duration_minutes} mins
                      </p>
                    </Card>
                  ) : (
                    <p className="text-xs text-charcoal-400 italic p-4 bg-stone-50 rounded-2xl">
                      No feeding recorded yet today.
                    </p>
                  )}
                </div>

                {/* Recent Growth */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <h4 className="font-heading font-bold text-sm text-teal-900">
                      Recent Growth Measurement
                    </h4>
                    <button
                      type="button"
                      onClick={() => setActiveTab('growth')}
                      className="text-xs font-bold text-teal-900 hover:text-coral-600 transition"
                    >
                      View History →
                    </button>
                  </div>
                  {overview?.latest_growth ? (
                    <Card className="p-4 bg-white border border-stone-200/80 rounded-3xl space-y-2">
                      <div className="flex justify-between text-xs">
                        <span className="font-bold text-teal-900">
                          {new Date(overview.latest_growth.recorded_at).toLocaleDateString()}
                        </span>
                        <span className="font-bold text-teal-900">
                          {overview.latest_growth.weight_kg} kg
                        </span>
                      </div>
                      <p className="text-xs text-charcoal-600">
                        Length: {overview.latest_growth.height_cm ? `${overview.latest_growth.height_cm} cm` : '--'} • Head: {overview.latest_growth.head_circumference_cm ? `${overview.latest_growth.head_circumference_cm} cm` : '--'}
                      </p>
                    </Card>
                  ) : (
                    <p className="text-xs text-charcoal-400 italic p-4 bg-stone-50 rounded-2xl">
                      No growth measurements recorded yet.
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'feeding' && <FeedingTracker />}
          {activeTab === 'growth' && <GrowthTracker />}
          {activeTab === 'nam' && <NamTracker />}
        </div>
      )}

      {/* Global Quick Action Modals */}
      <FeedingLogModal
        isOpen={isFeedingModalOpen}
        onClose={() => setIsFeedingModalOpen(false)}
        onSubmit={handleCreateFeeding}
      />

      <GrowthRecordModal
        isOpen={isGrowthModalOpen}
        onClose={() => setIsGrowthModalOpen(false)}
        onSubmit={handleCreateGrowth}
      />

      <NamLogModal
        isOpen={isNamModalOpen}
        onClose={() => setIsNamModalOpen(false)}
        onSubmit={handleCreateNam}
      />
    </div>
  );
};
