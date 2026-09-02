import React, { useState, useEffect } from 'react';
import { X, Mic } from 'lucide-react';
import { VoiceSession, VoiceSessionUpdateRequest } from '../../types';
import { Button } from '../ui/Button';

interface VoiceSessionModalProps {
  session: VoiceSession | null;
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (sessionId: string, data: VoiceSessionUpdateRequest) => Promise<void>;
}

export const VoiceSessionModal: React.FC<VoiceSessionModalProps> = ({
  session,
  isOpen,
  onClose,
  onSubmit,
}) => {
  const [durationSeconds, setDurationSeconds] = useState<number>(30);
  const [repetitionCount, setRepetitionCount] = useState<number>(1);
  const [parentNotes, setParentNotes] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (session) {
      setDurationSeconds(session.duration_seconds);
      setRepetitionCount(session.repetition_count);
      setParentNotes(session.parent_notes || '');
    }
  }, [session, isOpen]);

  if (!isOpen || !session) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setIsSubmitting(true);
      await onSubmit(session.id, {
        duration_seconds: durationSeconds,
        repetition_count: repetitionCount,
        parent_notes: parentNotes.trim() || undefined,
      });
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
              <Mic className="w-4 h-4" />
            </div>
            <div>
              <h2 className="font-heading font-bold text-lg text-teal-900">
                Edit Practice Session
              </h2>
              <span className="text-[11px] text-charcoal-500">
                {session.exercise ? session.exercise.title : 'General Practice'}
              </span>
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
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-bold text-charcoal-700 mb-1">
                Duration (seconds) *
              </label>
              <input
                type="number"
                min="1"
                max="3600"
                required
                value={durationSeconds}
                onChange={(e) => setDurationSeconds(Number(e.target.value))}
                className="w-full bg-white border border-stone-200 rounded-xl px-3 py-2 text-charcoal-900 focus:outline-none focus:ring-2 focus:ring-teal-700/20"
              />
            </div>

            <div>
              <label className="block font-bold text-charcoal-700 mb-1">
                Repetitions Completed
              </label>
              <input
                type="number"
                min="1"
                max="100"
                required
                value={repetitionCount}
                onChange={(e) => setRepetitionCount(Number(e.target.value))}
                className="w-full bg-white border border-stone-200 rounded-xl px-3 py-2 text-charcoal-900 focus:outline-none focus:ring-2 focus:ring-teal-700/20"
              />
            </div>
          </div>

          <div>
            <label className="block font-bold text-charcoal-700 mb-1">
              Parent Observations / Notes
            </label>
            <textarea
              rows={3}
              value={parentNotes}
              onChange={(e) => setParentNotes(e.target.value)}
              className="w-full bg-white border border-stone-200 rounded-xl px-3 py-2 text-charcoal-900 focus:outline-none focus:ring-2 focus:ring-teal-700/20 resize-none"
            />
          </div>

          <div className="pt-3 border-t border-stone-100 flex items-center justify-end gap-2">
            <Button variant="outline" size="sm" type="button" onClick={onClose}>
              Cancel
            </Button>
            <Button
              variant="primary"
              size="sm"
              type="submit"
              isLoading={isSubmitting}
            >
              Save Changes
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
