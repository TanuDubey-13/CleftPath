import React, { useState } from 'react';
import { Mic, BookOpen, History, BarChart3, Plus, Sparkles } from 'lucide-react';
import { VoiceExercise, VoiceSessionCreateRequest } from '../types';
import { useCreateVoiceSession, useVoiceExercises, useVoiceOverview, useVoiceSessions } from '../hooks/useVoice';
import { VoiceJourneyHeader } from '../components/voice/VoiceJourneyHeader';
import { VoiceSafetyNotice } from '../components/voice/VoiceSafetyNotice';
import { VoiceExerciseCard } from '../components/voice/VoiceExerciseCard';
import { VoiceExerciseModal } from '../components/voice/VoiceExerciseModal';
import { VoiceRecorderModal } from '../components/voice/VoiceRecorderModal';
import { VoiceSessionHistory } from '../components/voice/VoiceSessionHistory';
import { VoiceActivityChart } from '../components/voice/VoiceActivityChart';
import { VoiceJourneySkeleton } from '../components/voice/VoiceJourneySkeleton';
import { Button } from '../components/ui/Button';

type TabType = 'exercises' | 'history' | 'overview';

export const VoicePage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('exercises');
  const [selectedExerciseForModal, setSelectedExerciseForModal] = useState<VoiceExercise | null>(null);
  const [selectedExerciseForPractice, setSelectedExerciseForPractice] = useState<VoiceExercise | null>(null);
  const [isRecorderOpen, setIsRecorderOpen] = useState(false);

  // Queries & Mutations
  const { data: overview, isLoading: isOverviewLoading } = useVoiceOverview();
  const { data: exercisesData, isLoading: isExercisesLoading } = useVoiceExercises({ page: 1, page_size: 20 });
  const { data: sessionsData } = useVoiceSessions({ page: 1, page_size: 20 });
  const createSessionMutation = useCreateVoiceSession();

  const handleStartPractice = (exercise?: VoiceExercise | null) => {
    setSelectedExerciseForPractice(exercise || null);
    setIsRecorderOpen(true);
  };

  const handleSessionSubmit = async (payload: VoiceSessionCreateRequest) => {
    await createSessionMutation.mutateAsync(payload);
  };

  if (isOverviewLoading && isExercisesLoading) {
    return <VoiceJourneySkeleton />;
  }

  return (
    <div className="space-y-6 animate-fadeIn pb-12">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-heading font-bold text-2xl text-teal-900 flex items-center gap-2.5">
            <Mic className="w-6 h-6 text-teal-900" />
            <span>Voice Journey</span>
          </h1>
          <p className="text-sm text-charcoal-600">
            A calm, supportive practice journal for pre-speech play, sound exploration, and home routines.
          </p>
        </div>

        <Button
          variant="primary"
          size="sm"
          onClick={() => handleStartPractice(null)}
          leftIcon={<Plus className="w-4 h-4" />}
        >
          Record Practice Session
        </Button>
      </div>

      {/* Safety Notice */}
      <VoiceSafetyNotice />

      {/* Summary Header Cards */}
      <VoiceJourneyHeader
        overview={overview}
        onOpenQuickPractice={() => handleStartPractice(null)}
      />

      {/* Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-stone-200/80 pb-1">
        <button
          type="button"
          onClick={() => setActiveTab('exercises')}
          className={`px-4 py-2 rounded-2xl text-xs font-bold transition flex items-center gap-1.5 ${
            activeTab === 'exercises'
              ? 'bg-teal-900 text-white shadow-warm-xs'
              : 'text-charcoal-600 hover:text-teal-900 hover:bg-stone-100'
          }`}
        >
          <BookOpen className="w-3.5 h-3.5" />
          <span>Exercise Library ({exercisesData?.total ?? 0})</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab('history')}
          className={`px-4 py-2 rounded-2xl text-xs font-bold transition flex items-center gap-1.5 ${
            activeTab === 'history'
              ? 'bg-teal-900 text-white shadow-warm-xs'
              : 'text-charcoal-600 hover:text-teal-900 hover:bg-stone-100'
          }`}
        >
          <History className="w-3.5 h-3.5" />
          <span>Practice Journal ({overview?.total_sessions_count ?? 0})</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab('overview')}
          className={`px-4 py-2 rounded-2xl text-xs font-bold transition flex items-center gap-1.5 ${
            activeTab === 'overview'
              ? 'bg-teal-900 text-white shadow-warm-xs'
              : 'text-charcoal-600 hover:text-teal-900 hover:bg-stone-100'
          }`}
        >
          <BarChart3 className="w-3.5 h-3.5" />
          <span>Activity & Guidance</span>
        </button>
      </div>

      {/* Tab 1: Exercise Library */}
      {activeTab === 'exercises' && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {exercisesData?.items.map((ex) => (
              <VoiceExerciseCard
                key={ex.id}
                exercise={ex}
                onSelectPractice={(exercise) => handleStartPractice(exercise)}
                onViewDetails={(exercise) => setSelectedExerciseForModal(exercise)}
              />
            ))}
          </div>

          {(!exercisesData || exercisesData.items.length === 0) && (
            <div className="p-8 bg-white rounded-3xl border border-stone-200 text-center space-y-2 max-w-md mx-auto">
              <Sparkles className="w-8 h-8 text-teal-900 mx-auto" />
              <h4 className="font-heading font-bold text-sm text-teal-900">
                Exercise Library Ready
              </h4>
              <p className="text-xs text-charcoal-600">
                Speech exploration prompts and phoneme awareness games.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Practice Journal */}
      {activeTab === 'history' && (
        <VoiceSessionHistory onOpenQuickPractice={() => handleStartPractice(null)} />
      )}

      {/* Tab 3: Activity & Guidance */}
      {activeTab === 'overview' && (
        <div className="space-y-4">
          {/* Practice Activity Chart */}
          <VoiceActivityChart sessions={sessionsData?.items || []} />

          {/* Educational Guidance Notes */}
          {overview?.practice_guidance_notes && overview.practice_guidance_notes.length > 0 && (
            <div className="p-5 bg-white border border-stone-200/80 rounded-3xl space-y-3">
              <h4 className="font-heading font-bold text-sm text-teal-900">
                Home Speech Play Guidance
              </h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {overview.practice_guidance_notes.map((note, idx) => (
                  <div
                    key={idx}
                    className="p-3 bg-ivory-50/70 border border-stone-200/70 rounded-2xl flex items-start gap-2.5 text-xs text-charcoal-700"
                  >
                    <span className="w-5 h-5 rounded-full bg-teal-50 text-teal-900 font-bold flex items-center justify-center flex-shrink-0 text-[10px]">
                      {idx + 1}
                    </span>
                    <span className="leading-relaxed">{note}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Exercise Detail Modal */}
      <VoiceExerciseModal
        exercise={selectedExerciseForModal}
        isOpen={!!selectedExerciseForModal}
        onClose={() => setSelectedExerciseForModal(null)}
        onStartPractice={(exercise) => handleStartPractice(exercise)}
      />

      {/* Recorder Modal */}
      <VoiceRecorderModal
        isOpen={isRecorderOpen}
        onClose={() => setIsRecorderOpen(false)}
        onSubmit={handleSessionSubmit}
        selectedExercise={selectedExerciseForPractice}
      />
    </div>
  );
};
