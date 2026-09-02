import React, { useState } from 'react';
import { Milk, Plus } from 'lucide-react';
import { FeedingLog, FeedingLogCreateRequest } from '../../types';
import { useCreateFeedingLog, useDeleteFeedingLog, useFeedingLogs, useUpdateFeedingLog } from '../../hooks/useCare';
import { FeedingLogCard } from './FeedingLogCard';
import { FeedingLogModal } from './FeedingLogModal';
import { Button } from '../ui/Button';
import { Skeleton } from '../ui/Skeleton';

export const FeedingTracker: React.FC = () => {
  const [page, setPage] = useState(1);
  const pageSize = 8;
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingLog, setEditingLog] = useState<FeedingLog | null>(null);

  const { data, isLoading } = useFeedingLogs({ page, page_size: pageSize });
  const createMutation = useCreateFeedingLog();
  const updateMutation = useUpdateFeedingLog();
  const deleteMutation = useDeleteFeedingLog();

  const handleOpenCreate = () => {
    setEditingLog(null);
    setIsModalOpen(true);
  };

  const handleEdit = (log: FeedingLog) => {
    setEditingLog(log);
    setIsModalOpen(true);
  };

  const handleDelete = async (logId: string) => {
    if (window.confirm('Delete this feeding record?')) {
      await deleteMutation.mutateAsync(logId);
    }
  };

  const handleSubmit = async (payload: FeedingLogCreateRequest) => {
    if (editingLog) {
      await updateMutation.mutateAsync({ logId: editingLog.id, payload });
    } else {
      await createMutation.mutateAsync(payload);
    }
  };

  return (
    <div className="space-y-4">
      {/* Top Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-4 rounded-3xl border border-stone-200/80 shadow-warm-xs">
        <div>
          <h3 className="font-heading font-bold text-base text-teal-900">
            Feeding Sessions ({data?.total ?? 0})
          </h3>
          <p className="text-xs text-charcoal-600">
            Today's Total: <strong className="text-teal-900">{data?.today_total_volume_ml ?? 0} ml</strong> across{' '}
            <strong>{data?.today_total_feeds ?? 0}</strong> feeds.
          </p>
        </div>

        <Button
          variant="primary"
          size="sm"
          onClick={handleOpenCreate}
          leftIcon={<Plus className="w-4 h-4" />}
        >
          Log Feeding
        </Button>
      </div>

      {/* Content Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="p-4 bg-white rounded-3xl border border-stone-200/80 space-y-3">
              <Skeleton variant="rectangular" className="w-32 h-6 rounded-xl" />
              <Skeleton variant="text" className="w-24 h-6" />
              <Skeleton variant="text" className="w-3/4 h-4" />
            </div>
          ))}
        </div>
      ) : !data || data.items.length === 0 ? (
        <div className="p-8 bg-white rounded-3xl border border-stone-200 text-center space-y-3 max-w-md mx-auto">
          <div className="w-12 h-12 rounded-2xl bg-coral-50 text-coral-600 mx-auto flex items-center justify-center">
            <Milk className="w-6 h-6" />
          </div>
          <h4 className="font-heading font-bold text-base text-teal-900">
            No Feeding Records Yet
          </h4>
          <p className="text-xs text-charcoal-600">
            Track daily volume, specialty bottles, and feeding comfort over time.
          </p>
          <Button variant="outline" size="sm" onClick={handleOpenCreate}>
            Record First Feed
          </Button>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {data.items.map((log) => (
              <FeedingLogCard
                key={log.id}
                log={log}
                onEdit={handleEdit}
                onDelete={handleDelete}
              />
            ))}
          </div>

          {/* Pagination Controls */}
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

      {/* Feeding Modal */}
      <FeedingLogModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleSubmit}
        initialLog={editingLog}
      />
    </div>
  );
};
