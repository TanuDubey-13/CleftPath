import React, { useState } from 'react';
import { Compass, RefreshCw, Sparkles } from 'lucide-react';
import { useAddMilestoneNote, useJourney, useUpdateMilestone } from '../hooks/useJourney';
import { JourneyMilestone, MilestoneStatus } from '../types';
import { JourneyOverviewHeader } from '../components/journey/JourneyOverviewHeader';
import { JourneyStageSection } from '../components/journey/JourneyStageSection';
import { MilestoneDetailModal } from '../components/journey/MilestoneDetailModal';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { Button } from '../components/ui/Button';
import { Alert } from '../components/ui/Alert';

export const JourneyPage: React.FC = () => {
  const { data: journey, isLoading, isError, error, refetch } = useJourney();
  const updateMilestoneMutation = useUpdateMilestone();
  const addNoteMutation = useAddMilestoneNote();

  const [selectedMilestone, setSelectedMilestone] = useState<JourneyMilestone | null>(null);

  // Toggle milestone status (Upcoming -> In Progress -> Completed -> Upcoming)
  const handleToggleStatus = async (milestoneId: string, currentStatus: MilestoneStatus) => {
    let nextStatus: MilestoneStatus = 'in_progress';
    if (currentStatus === 'upcoming') nextStatus = 'in_progress';
    else if (currentStatus === 'in_progress') nextStatus = 'completed';
    else if (currentStatus === 'completed') nextStatus = 'upcoming';

    await updateMilestoneMutation.mutateAsync({
      milestoneId,
      payload: { status: nextStatus },
    });
  };

  // Update status from modal
  const handleModalUpdateStatus = async (newStatus: MilestoneStatus) => {
    if (!selectedMilestone) return;
    const updated = await updateMilestoneMutation.mutateAsync({
      milestoneId: selectedMilestone.id,
      payload: { status: newStatus },
    });
    setSelectedMilestone(updated);
  };

  // Add note from modal
  const handleModalAddNote = async (noteText: string) => {
    if (!selectedMilestone) return;
    const newNote = await addNoteMutation.mutateAsync({
      milestoneId: selectedMilestone.id,
      payload: { note_text: noteText },
    });
    setSelectedMilestone({
      ...selectedMilestone,
      notes_count: selectedMilestone.notes_count + 1,
      notes: [newNote, ...selectedMilestone.notes],
    });
  };

  if (isLoading) {
    return (
      <div className="py-20 flex flex-col items-center justify-center space-y-3">
        <LoadingSpinner size="lg" />
        <p className="text-xs font-medium text-charcoal-600">Loading your longitudinal roadmap...</p>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="max-w-2xl mx-auto py-12 space-y-4">
        <Alert variant="danger" title="Unable to Load Care Journey">
          {error instanceof Error ? error.message : 'An error occurred while connecting to the server.'}
        </Alert>
        <div className="text-center">
          <Button
            variant="outline"
            size="md"
            onClick={() => refetch()}
            leftIcon={<RefreshCw className="w-4 h-4" />}
          >
            Retry Loading
          </Button>
        </div>
      </div>
    );
  }

  if (!journey || !journey.patient) {
    return (
      <div className="bg-white rounded-3xl border border-stone-200 p-8 sm:p-12 text-center max-w-xl mx-auto space-y-4 shadow-warm-sm">
        <div className="w-14 h-14 rounded-2xl bg-teal-50 text-teal-900 mx-auto flex items-center justify-center">
          <Compass className="w-8 h-8 text-teal-900" />
        </div>
        <h2 className="font-heading font-bold text-xl text-teal-900">
          No Care Journey Profile Found
        </h2>
        <p className="text-xs text-charcoal-600 leading-relaxed">
          Create or link a patient profile to begin your customized cleft care roadmap with longitudinal milestones.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-12 animate-fade-in">
      {/* Journey Overview Banner with Progress */}
      <JourneyOverviewHeader patient={journey.patient} summary={journey.summary} />

      {/* Longitudinal Stages Timeline */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="font-heading font-bold text-lg text-teal-900 flex items-center gap-2">
            <Sparkles className="w-4.5 h-4.5 text-coral-500" />
            <span>Longitudinal Care Roadmap (8 Stages)</span>
          </h2>
        </div>

        <div className="space-y-4">
          {journey.stages.map((stage) => (
            <JourneyStageSection
              key={stage.id}
              stage={stage}
              onSelectMilestone={(m) => setSelectedMilestone(m)}
              onToggleStatus={handleToggleStatus}
            />
          ))}
        </div>
      </div>

      {/* Milestone Detail & Notes Modal */}
      <MilestoneDetailModal
        milestone={selectedMilestone}
        isOpen={!!selectedMilestone}
        onClose={() => setSelectedMilestone(null)}
        onUpdateStatus={handleModalUpdateStatus}
        onAddNote={handleModalAddNote}
      />
    </div>
  );
};
