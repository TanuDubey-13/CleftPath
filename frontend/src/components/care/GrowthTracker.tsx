import React, { useState } from 'react';
import { Scale, Plus } from 'lucide-react';
import { GrowthRecord, GrowthRecordCreateRequest } from '../../types';
import { useCreateGrowthRecord, useDeleteGrowthRecord, useGrowthRecords, useUpdateGrowthRecord } from '../../hooks/useCare';
import { GrowthRecordCard } from './GrowthRecordCard';
import { GrowthRecordModal } from './GrowthRecordModal';
import { GrowthTrendChart } from './GrowthTrendChart';
import { Button } from '../ui/Button';
import { Skeleton } from '../ui/Skeleton';

export const GrowthTracker: React.FC = () => {
  const [page, setPage] = useState(1);
  const pageSize = 8;
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingRecord, setEditingRecord] = useState<GrowthRecord | null>(null);

  const { data, isLoading } = useGrowthRecords({ page, page_size: pageSize });
  const createMutation = useCreateGrowthRecord();
  const updateMutation = useUpdateGrowthRecord();
  const deleteMutation = useDeleteGrowthRecord();

  const handleOpenCreate = () => {
    setEditingRecord(null);
    setIsModalOpen(true);
  };

  const handleEdit = (record: GrowthRecord) => {
    setEditingRecord(record);
    setIsModalOpen(true);
  };

  const handleDelete = async (recordId: string) => {
    if (window.confirm('Delete this growth measurement?')) {
      await deleteMutation.mutateAsync(recordId);
    }
  };

  const handleSubmit = async (payload: GrowthRecordCreateRequest) => {
    if (editingRecord) {
      await updateMutation.mutateAsync({ recordId: editingRecord.id, payload });
    } else {
      await createMutation.mutateAsync(payload);
    }
  };

  return (
    <div className="space-y-5">
      {/* Top Header Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-4 rounded-3xl border border-stone-200/80 shadow-warm-xs">
        <div>
          <h3 className="font-heading font-bold text-base text-teal-900">
            Growth & Physical Records ({data?.total ?? 0})
          </h3>
          <p className="text-xs text-charcoal-600">
            Latest Weight: <strong className="text-teal-900">{data?.latest_weight_kg ? `${data.latest_weight_kg} kg` : '--'}</strong>
          </p>
        </div>

        <Button
          variant="primary"
          size="sm"
          onClick={handleOpenCreate}
          leftIcon={<Plus className="w-4 h-4" />}
        >
          Record Measurement
        </Button>
      </div>

      {/* Visual Trend Chart */}
      {data && data.items.length > 0 && (
        <GrowthTrendChart records={data.items} />
      )}

      {/* Grid of Record Cards */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="p-4 bg-white rounded-3xl border border-stone-200/80 space-y-3">
              <Skeleton variant="rectangular" className="w-28 h-6 rounded-xl" />
              <Skeleton variant="text" className="w-20 h-6" />
            </div>
          ))}
        </div>
      ) : !data || data.items.length === 0 ? (
        <div className="p-8 bg-white rounded-3xl border border-stone-200 text-center space-y-3 max-w-md mx-auto">
          <div className="w-12 h-12 rounded-2xl bg-teal-50 text-teal-900 mx-auto flex items-center justify-center">
            <Scale className="w-6 h-6" />
          </div>
          <h4 className="font-heading font-bold text-base text-teal-900">
            No Growth Measurements Yet
          </h4>
          <p className="text-xs text-charcoal-600">
            Record physical growth measurements from clinic visits and pediatrician checkups.
          </p>
          <Button variant="outline" size="sm" onClick={handleOpenCreate}>
            Record First Measurement
          </Button>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {data.items.map((record) => (
              <GrowthRecordCard
                key={record.id}
                record={record}
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
      <GrowthRecordModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleSubmit}
        initialRecord={editingRecord}
      />
    </div>
  );
};
