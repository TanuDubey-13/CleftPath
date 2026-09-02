import React, { useState } from 'react';
import { Mic, Plus } from 'lucide-react';
import { VoiceSession, VoiceSessionUpdateRequest } from '../../types';
import { useDeleteVoiceSession, useUpdateVoiceSession, useVoiceSessions } from '../../hooks/useVoice';
import { VoiceSessionCard } from './VoiceSessionCard';
import { VoiceSessionModal } from './VoiceSessionModal';
import { Button } from '../ui/Button';
import { Skeleton } from '../ui/Skeleton';

interface VoiceSessionHistoryProps {
  onOpenQuickPractice: () => void;
}

export const VoiceSessionHistory: React.FC<VoiceSessionHistoryProps> = ({
  onOpenQuickPractice,
}) => {
  const [page, setPage] = useState(1);
  const pageSize = 8;
  const [editingSession, setEditingSession] = useState<VoiceSession | null>(null);

  const { data, isLoading } = useVoiceSessions({ page, page_size: pageSize });
  const updateMutation = useUpdateVoiceSession();
  const deleteMutation = useDeleteVoiceSession();

  const handleEdit = (session: VoiceSession) => {
    setEditingSession(session);
  };

  const handleDelete = async (sessionId: string) => {
    if (window.confirm('Delete this practice session record?')) {
      await deleteMutation.mutateAsync(sessionId);
    }
  };

  const handleUpdateSubmit = async (sessionId: string, payload: VoiceSessionUpdateRequest) => {
    await updateMutation.mutateAsync({ sessionId, payload });
  };

  return (
    <div className="space-y-4">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-4 rounded-3xl border border-stone-200/80 shadow-warm-xs">
        <div>
          <h3 className="font-heading font-bold text-base text-teal-900">
            Practice Session History ({data?.total ?? 0})
          </h3>
          <p className="text-xs text-charcoal-600">
            Total Practice Logged: <strong className="text-teal-900">{data?.total_practice_minutes ?? 0} minutes</strong>
          </p>
        </div>

        <Button
          variant="primary"
          size="sm"
          onClick={onOpenQuickPractice}
          leftIcon={<Plus className="w-4 h-4" />}
        >
          Record Practice Session
        </Button>
      </div>

      {/* Grid of Sessions */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="p-4 bg-white rounded-3xl border border-stone-200/80 space-y-3">
              <Skeleton variant="rectangular" className="w-32 h-6 rounded-xl" />
              <Skeleton variant="text" className="w-48 h-5" />
              <Skeleton variant="text" className="w-full h-4" />
            </div>
          ))}
        </div>
      ) : !data || data.items.length === 0 ? (
        <div className="p-8 bg-white rounded-3xl border border-stone-200 text-center space-y-3 max-w-md mx-auto">
          <div className="w-12 h-12 rounded-2xl bg-teal-50 text-teal-900 mx-auto flex items-center justify-center">
            <Mic className="w-6 h-6" />
          </div>
          <h4 className="font-heading font-bold text-base text-teal-900">
            No Practice Sessions Logged Yet
          </h4>
          <p className="text-xs text-charcoal-600">
            Record home sound play sessions, bilabial babbling, and repetition games.
          </p>
          <Button variant="outline" size="sm" onClick={onOpenQuickPractice}>
            Start First Practice Session
          </Button>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {data.items.map((session) => (
              <VoiceSessionCard
                key={session.id}
                session={session}
                onEdit={handleEdit}
                onDelete={handleDelete}
              />
            ))}
          </div>

          {/* Pagination */}
          {data.total_pages > 1 && (
            <div className="flex items-center justify-between pt-2 border-t border-stone-200/80 text-xs">
              <span className="text-charcoal-500">
                Page <strong>{data.page}</strong> of <strong>{data.total_pages}</strong>
              </span>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={!data.has_prev}
                >
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage((p) => p + 1)}
                  disabled={!data.has_next}
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Edit Session Modal */}
      <VoiceSessionModal
        session={editingSession}
        isOpen={!!editingSession}
        onClose={() => setEditingSession(null)}
        onSubmit={handleUpdateSubmit}
      />
    </div>
  );
};
