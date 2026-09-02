import React, { useState, useEffect } from 'react';
import { X, Scale } from 'lucide-react';
import { GrowthRecord, GrowthRecordCreateRequest } from '../../types';
import { Button } from '../ui/Button';

interface GrowthRecordModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: GrowthRecordCreateRequest) => Promise<void>;
  initialRecord?: GrowthRecord | null;
}

export const GrowthRecordModal: React.FC<GrowthRecordModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  initialRecord,
}) => {
  const [recordedAt, setRecordedAt] = useState('');
  const [weightKg, setWeightKg] = useState<number>(4.0);
  const [heightCm, setHeightCm] = useState<number | ''>('');
  const [headCircumferenceCm, setHeadCircumferenceCm] = useState<number | ''>('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (initialRecord) {
      setRecordedAt(initialRecord.recorded_at);
      setWeightKg(initialRecord.weight_kg);
      setHeightCm(initialRecord.height_cm ?? '');
      setHeadCircumferenceCm(initialRecord.head_circumference_cm ?? '');
    } else {
      setRecordedAt(new Date().toISOString().slice(0, 10));
      setWeightKg(4.0);
      setHeightCm('');
      setHeadCircumferenceCm('');
    }
  }, [initialRecord, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (weightKg <= 0 || !recordedAt) return;

    try {
      setIsSubmitting(true);
      const payload: GrowthRecordCreateRequest = {
        recorded_at: recordedAt,
        weight_kg: weightKg,
        height_cm: heightCm !== '' ? Number(heightCm) : undefined,
        head_circumference_cm: headCircumferenceCm !== '' ? Number(headCircumferenceCm) : undefined,
      };
      await onSubmit(payload);
      onClose();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-charcoal-900/50 backdrop-blur-sm animate-fade-in"
      onClick={onClose}
    >
      <div
        className="bg-white w-full max-w-lg rounded-3xl shadow-warm-lg border border-stone-200 overflow-hidden flex flex-col max-h-[90vh]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="p-5 border-b border-stone-100 flex items-center justify-between bg-ivory-50/50">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-teal-50 text-teal-900 flex items-center justify-center">
              <Scale className="w-4 h-4" />
            </div>
            <div>
              <h2 className="font-heading font-bold text-lg text-teal-900">
                {initialRecord ? 'Edit Growth Measurement' : 'Record Growth Measurement'}
              </h2>
              <p className="text-[11px] text-charcoal-600">
                Record weight, length, and head circumference.
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-xl text-charcoal-400 hover:text-charcoal-800 hover:bg-stone-100 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-5 space-y-4 overflow-y-auto flex-1 text-xs">
          {/* Date */}
          <div>
            <label className="block font-bold text-charcoal-700 mb-1">
              Measurement Date *
            </label>
            <input
              type="date"
              required
              value={recordedAt}
              onChange={(e) => setRecordedAt(e.target.value)}
              className="w-full bg-white border border-stone-200 rounded-xl px-3 py-2 text-charcoal-900 focus:outline-none focus:ring-2 focus:ring-teal-700/20"
            />
          </div>

          {/* Weight */}
          <div>
            <label className="block font-bold text-charcoal-700 mb-1">
              Weight (kg) *
            </label>
            <input
              type="number"
              step="0.01"
              min="0.5"
              max="50.0"
              required
              placeholder="e.g. 4.35"
              value={weightKg}
              onChange={(e) => setWeightKg(Number(e.target.value))}
              className="w-full bg-white border border-stone-200 rounded-xl px-3 py-2 text-charcoal-900 focus:outline-none focus:ring-2 focus:ring-teal-700/20"
            />
          </div>

          {/* Height & Head Circumference */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-bold text-charcoal-700 mb-1">
                Length / Height (cm)
              </label>
              <input
                type="number"
                step="0.1"
                min="20"
                max="150"
                placeholder="e.g. 54.5"
                value={heightCm}
                onChange={(e) => setHeightCm(e.target.value === '' ? '' : Number(e.target.value))}
                className="w-full bg-white border border-stone-200 rounded-xl px-3 py-2 text-charcoal-900 focus:outline-none focus:ring-2 focus:ring-teal-700/20"
              />
            </div>

            <div>
              <label className="block font-bold text-charcoal-700 mb-1">
                Head Circumference (cm)
              </label>
              <input
                type="number"
                step="0.1"
                min="15"
                max="70"
                placeholder="e.g. 37.0"
                value={headCircumferenceCm}
                onChange={(e) => setHeadCircumferenceCm(e.target.value === '' ? '' : Number(e.target.value))}
                className="w-full bg-white border border-stone-200 rounded-xl px-3 py-2 text-charcoal-900 focus:outline-none focus:ring-2 focus:ring-teal-700/20"
              />
            </div>
          </div>

          {/* Actions */}
          <div className="pt-4 border-t border-stone-100 flex items-center justify-end gap-2">
            <Button variant="outline" size="sm" type="button" onClick={onClose}>
              Cancel
            </Button>
            <Button
              variant="primary"
              size="sm"
              type="submit"
              isLoading={isSubmitting}
            >
              {initialRecord ? 'Save Changes' : 'Record Measurement'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
