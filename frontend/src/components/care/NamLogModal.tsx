import React, { useState, useEffect } from 'react';
import { X, Clock } from 'lucide-react';
import { NAMTapingLog, NAMTapingLogCreateRequest } from '../../types';
import { Button } from '../ui/Button';

interface NamLogModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: NAMTapingLogCreateRequest) => Promise<void>;
  initialLog?: NAMTapingLog | null;
}

export const NamLogModal: React.FC<NamLogModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  initialLog,
}) => {
  const [loggedAt, setLoggedAt] = useState('');
  const [hoursWorn, setHoursWorn] = useState<number>(22);
  const [applianceCleaned, setApplianceCleaned] = useState<boolean>(true);
  const [tapeChanged, setTapeChanged] = useState<boolean>(true);
  const [skinCondition, setSkinCondition] = useState<string>('normal');
  const [notes, setNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (initialLog) {
      setLoggedAt(new Date(initialLog.logged_at).toISOString().slice(0, 16));
      setHoursWorn(initialLog.hours_worn);
      setApplianceCleaned(initialLog.appliance_cleaned);
      setTapeChanged(initialLog.tape_changed);
      setSkinCondition(initialLog.skin_condition);
      setNotes(initialLog.notes || '');
    } else {
      setLoggedAt(new Date().toISOString().slice(0, 16));
      setHoursWorn(22);
      setApplianceCleaned(true);
      setTapeChanged(true);
      setSkinCondition('normal');
      setNotes('');
    }
  }, [initialLog, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (hoursWorn < 0 || hoursWorn > 24) return;

    try {
      setIsSubmitting(true);
      const payload: NAMTapingLogCreateRequest = {
        logged_at: loggedAt ? new Date(loggedAt).toISOString() : undefined,
        hours_worn: hoursWorn,
        appliance_cleaned: applianceCleaned,
        tape_changed: tapeChanged,
        skin_condition: skinCondition.trim(),
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
        {/* Header */}
        <div className="p-5 border-b border-stone-100 flex items-center justify-between bg-ivory-50/50">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-sage-50 text-sage-800 flex items-center justify-center">
              <Clock className="w-4 h-4" />
            </div>
            <div>
              <h2 className="font-heading font-bold text-lg text-teal-900">
                {initialLog ? 'Edit NAM / Taping Log' : 'Log NAM / Taping Usage'}
              </h2>
              <p className="text-[11px] text-charcoal-600">
                Record daily appliance wear hours and skin condition.
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
              Log Date & Time *
            </label>
            <input
              type="datetime-local"
              required
              value={loggedAt}
              onChange={(e) => setLoggedAt(e.target.value)}
              className="w-full bg-white border border-stone-200 rounded-xl px-3 py-2 text-charcoal-900 focus:outline-none focus:ring-2 focus:ring-teal-700/20"
            />
          </div>

          {/* Hours Worn */}
          <div>
            <label className="block font-bold text-charcoal-700 mb-1">
              Hours Worn (0 to 24) *
            </label>
            <input
              type="number"
              min="0"
              max="24"
              required
              value={hoursWorn}
              onChange={(e) => setHoursWorn(Number(e.target.value))}
              className="w-full bg-white border border-stone-200 rounded-xl px-3 py-2 text-charcoal-900 focus:outline-none focus:ring-2 focus:ring-teal-700/20"
            />
          </div>

          {/* Skin Condition */}
          <div>
            <label className="block font-bold text-charcoal-700 mb-1">
              Cheek / Lip Skin Condition
            </label>
            <select
              value={skinCondition}
              onChange={(e) => setSkinCondition(e.target.value)}
              className="w-full bg-white border border-stone-200 rounded-xl px-3 py-2 text-charcoal-900 focus:outline-none focus:ring-2 focus:ring-teal-700/20"
            >
              <option value="normal">Normal (Healthy & Intact)</option>
              <option value="mild_redness">Mild Redness (Under Tape)</option>
              <option value="irritation">Irritation / Soreness</option>
            </select>
          </div>

          {/* Routine Checkboxes */}
          <div className="space-y-2 pt-1">
            <label className="flex items-center gap-2 text-xs text-charcoal-800 cursor-pointer">
              <input
                type="checkbox"
                checked={tapeChanged}
                onChange={(e) => setTapeChanged(e.target.checked)}
                className="rounded text-teal-900 focus:ring-teal-700"
              />
              <span className="font-semibold">Tape and elastics were changed today</span>
            </label>

            <label className="flex items-center gap-2 text-xs text-charcoal-800 cursor-pointer">
              <input
                type="checkbox"
                checked={applianceCleaned}
                onChange={(e) => setApplianceCleaned(e.target.checked)}
                className="rounded text-teal-900 focus:ring-teal-700"
              />
              <span className="font-semibold">Appliance was cleaned with mild soap/water</span>
            </label>
          </div>

          {/* Notes */}
          <div>
            <label className="block font-bold text-charcoal-700 mb-1">
              Notes (Optional)
            </label>
            <textarea
              rows={2}
              placeholder="e.g. Applied skin barrier film before taping, retention was secure..."
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
              {initialLog ? 'Save Changes' : 'Record NAM Entry'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
