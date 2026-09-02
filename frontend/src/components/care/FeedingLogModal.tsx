import React, { useState, useEffect } from 'react';
import { X, Milk } from 'lucide-react';
import { FeedingBottleType, FeedingLog, FeedingLogCreateRequest, RefluxSeverity } from '../../types';
import { Button } from '../ui/Button';

interface FeedingLogModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: FeedingLogCreateRequest) => Promise<void>;
  initialLog?: FeedingLog | null;
}

const BOTTLE_OPTIONS: { value: FeedingBottleType; label: string }[] = [
  { value: 'dr_browns_specialty', label: "Dr. Brown's Specialty Feeder" },
  { value: 'pigeon_cleft', label: 'Pigeon Cleft Feeder' },
  { value: 'medela_specialneeds_haberman', label: 'Medela SpecialNeeds (Haberman)' },
  { value: 'syringe_with_tubing', label: 'Syringe with Tubing' },
  { value: 'supplemental_nursing', label: 'Supplemental Nursing System (SNS)' },
  { value: 'cup_open', label: 'Open Cup' },
  { value: 'standard_bottle', label: 'Standard Bottle' },
  { value: 'other', label: 'Other Method' },
];

export const FeedingLogModal: React.FC<FeedingLogModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  initialLog,
}) => {
  const [loggedAt, setLoggedAt] = useState('');
  const [bottleType, setBottleType] = useState<FeedingBottleType>('dr_browns_specialty');
  const [volumeMl, setVolumeMl] = useState<number>(100);
  const [durationMinutes, setDurationMinutes] = useState<number>(20);
  const [burpingBreaks, setBurpingBreaks] = useState<number>(2);
  const [refluxSeverity, setRefluxSeverity] = useState<RefluxSeverity>('none');
  const [notes, setNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (initialLog) {
      setLoggedAt(new Date(initialLog.logged_at).toISOString().slice(0, 16));
      setBottleType(initialLog.bottle_type);
      setVolumeMl(initialLog.volume_ml);
      setDurationMinutes(initialLog.duration_minutes);
      setBurpingBreaks(initialLog.burping_breaks);
      setRefluxSeverity(initialLog.reflux_severity);
      setNotes(initialLog.notes || '');
    } else {
      setLoggedAt(new Date().toISOString().slice(0, 16));
      setBottleType('dr_browns_specialty');
      setVolumeMl(100);
      setDurationMinutes(20);
      setBurpingBreaks(2);
      setRefluxSeverity('none');
      setNotes('');
    }
  }, [initialLog, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (volumeMl < 0 || durationMinutes <= 0) return;

    try {
      setIsSubmitting(true);
      const payload: FeedingLogCreateRequest = {
        logged_at: loggedAt ? new Date(loggedAt).toISOString() : undefined,
        bottle_type: bottleType,
        volume_ml: volumeMl,
        duration_minutes: durationMinutes,
        burping_breaks: burpingBreaks,
        reflux_severity: refluxSeverity,
        notes: notes.trim() || undefined,
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
        {/* Modal Header */}
        <div className="p-5 border-b border-stone-100 flex items-center justify-between bg-ivory-50/50">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-coral-50 text-coral-600 flex items-center justify-center">
              <Milk className="w-4 h-4" />
            </div>
            <div>
              <h2 className="font-heading font-bold text-lg text-teal-900">
                {initialLog ? 'Edit Feeding Session' : 'Log Feeding Session'}
              </h2>
              <p className="text-[11px] text-charcoal-600">
                Track volume, pacing, and feeding method.
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
          {/* Date & Time */}
          <div>
            <label className="block font-bold text-charcoal-700 mb-1">
              Feeding Date & Time *
            </label>
            <input
              type="datetime-local"
              required
              value={loggedAt}
              onChange={(e) => setLoggedAt(e.target.value)}
              className="w-full bg-white border border-stone-200 rounded-xl px-3 py-2 text-charcoal-900 focus:outline-none focus:ring-2 focus:ring-teal-700/20"
            />
          </div>

          {/* Specialty Feeding Bottle / Method */}
          <div>
            <label className="block font-bold text-charcoal-700 mb-1">
              Feeding Method / Bottle Type *
            </label>
            <select
              value={bottleType}
              onChange={(e) => setBottleType(e.target.value as FeedingBottleType)}
              className="w-full bg-white border border-stone-200 rounded-xl px-3 py-2 text-charcoal-900 focus:outline-none focus:ring-2 focus:ring-teal-700/20"
            >
              {BOTTLE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          {/* Volume & Duration */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-bold text-charcoal-700 mb-1">
                Volume Fed (ml) *
              </label>
              <input
                type="number"
                min="0"
                max="1000"
                step="5"
                required
                value={volumeMl}
                onChange={(e) => setVolumeMl(Number(e.target.value))}
                className="w-full bg-white border border-stone-200 rounded-xl px-3 py-2 text-charcoal-900 focus:outline-none focus:ring-2 focus:ring-teal-700/20"
              />
            </div>

            <div>
              <label className="block font-bold text-charcoal-700 mb-1">
                Duration (minutes) *
              </label>
              <input
                type="number"
                min="1"
                max="180"
                required
                value={durationMinutes}
                onChange={(e) => setDurationMinutes(Number(e.target.value))}
                className="w-full bg-white border border-stone-200 rounded-xl px-3 py-2 text-charcoal-900 focus:outline-none focus:ring-2 focus:ring-teal-700/20"
              />
            </div>
          </div>

          {/* Burping & Reflux */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-bold text-charcoal-700 mb-1">
                Burping Intervals
              </label>
              <input
                type="number"
                min="0"
                max="50"
                value={burpingBreaks}
                onChange={(e) => setBurpingBreaks(Number(e.target.value))}
                className="w-full bg-white border border-stone-200 rounded-xl px-3 py-2 text-charcoal-900 focus:outline-none focus:ring-2 focus:ring-teal-700/20"
              />
            </div>

            <div>
              <label className="block font-bold text-charcoal-700 mb-1">
                Reflux Severity
              </label>
              <select
                value={refluxSeverity}
                onChange={(e) => setRefluxSeverity(e.target.value as RefluxSeverity)}
                className="w-full bg-white border border-stone-200 rounded-xl px-3 py-2 text-charcoal-900 focus:outline-none focus:ring-2 focus:ring-teal-700/20"
              >
                <option value="none">None</option>
                <option value="mild">Mild (Occasional Spit-up)</option>
                <option value="moderate">Moderate</option>
                <option value="severe">Severe / Uncomfortable</option>
              </select>
            </div>
          </div>

          {/* Notes */}
          <div>
            <label className="block font-bold text-charcoal-700 mb-1">
              Observations / Notes (Optional)
            </label>
            <textarea
              rows={2}
              placeholder="e.g. Fed in 60° upright position, latched on blue valve easily..."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full bg-white border border-stone-200 rounded-xl px-3 py-2 text-charcoal-900 focus:outline-none focus:ring-2 focus:ring-teal-700/20 resize-none"
            />
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
              {initialLog ? 'Save Changes' : 'Record Session'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
