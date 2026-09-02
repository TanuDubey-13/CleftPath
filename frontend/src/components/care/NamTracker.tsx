import React, { useState } from 'react';
import { Clock, Plus } from 'lucide-react';
import { NAMTapingLog, NAMTapingLogCreateRequest } from '../../types';
import { useCreateNAMLog, useDeleteNAMLog, useNAMLogs, useUpdateNAMLog } from '../../hooks/useCare';
import { NamLogCard } from './NamLogCard';
import { NamLogModal } from './NamLogModal';
import { Button } from '../ui/Button';
import { Skeleton } from '../ui/Skeleton';

export const NamTracker: React.FC = () => {
  const [page, setPage] = useState(1);
  const pageSize = 8;
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingLog, setEditingLog] = useState<NAMTapingLog | null>(null);

  const { data, isLoading } = useNAMLogs({ page, page_size: pageSize });
  const createMutation = useCreateNAMLog();
  const updateMutation = useUpdateNAMLog();
  const deleteMutation = useDeleteNAMLog();

  const handleOpenCreate = () => {
    setEditingLog(null);
    setIsModalOpen(true);
  };

  const handleEdit = (log: NAMTapingLog) => {
    setEditingLog(log);
    setIsModalOpen(true);
  };

  const handleDelete = async (logId: string) => {
    if (window.confirm('Delete this NAM log?')) {
      await deleteMutation.mutateAsync(logId);
    }
  };

  const handleSubmit = async (payload: NAMTapingLogCreateRequest) => {
    if (editingLog) {
      await updateMutation.mutateAsync({ logId: editingLog.id, payload });
    } else {
      await createMutation.mutateAsync(payload);
    }
  };

  return (
    <div className="space-y-4">
      {/* Header Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-4 rounded-3xl border border-stone-200/80 shadow-warm-xs">
        <div>
          <h3 className="font-heading font-bold text-base text-teal-900">
            NAM & Taping Usage ({data?.total ?? 0})
          </h3>
          <p className="text-xs text-charcoal-600">
            Today's Wear: <strong className="text-teal-900">{data?.today_hours_worn ?? 0} hours</strong> recorded
          </p>
        </div>

        <Button
          variant="primary"
          size="sm"
          onClick={handleOpenCreate}
          leftIcon={<Plus className="w-4 h-4" />}
        >
          Log NAM Wear
        </Button>
      </div>

      {/* List Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="p-4 bg-white rounded-3xl border border-stone-200/80 space-y-3">
              <Skeleton variant="rectangular" className="w-28 h-6 rounded-xl" />
              <Skeleton variant="text" className="w-24 h-6" />
            </div>
          ))}
        </div>
      ) : !data || data.items.length === 0 ? (
        <div className="p-8 bg-white rounded-3xl border border-stone-200 text-center space-y-3 max-w-md mx-auto">
          <div className="w-12 h-12 rounded-2xl bg-sage-50 text-sage-800 mx-auto flex items-center justify-center">
            <Clock className="w-6 h-6" />
          </div>
          <h4 className="font-heading font-bold text-base text-teal-900">
            No NAM Logs Yet
          </h4>
          <p className="text-xs text-charcoal-600">
            Record daily appliance wear hours, tape changes, and skin checks.
          </p>
          <Button variant="outline" size="sm" onClick={handleOpenCreate}>
            Record First NAM Entry
          </Button>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {data.items.map((log) => (
              <NamLogCard
                key={log.id}
                log={log}
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

      {/* Modal */}
      <NamLogModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleSubmit}
        initialLog={editingLog}
      />
    </div>
  );
};
