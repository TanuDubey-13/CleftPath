import React, { useState } from 'react';
import { X, CheckCircle2, Clock, Circle, MessageSquare, Send } from 'lucide-react';
import { JourneyMilestone, MilestoneStatus } from '../../types';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';

interface MilestoneDetailModalProps {
  milestone: JourneyMilestone | null;
  isOpen: boolean;
  onClose: () => void;
  onUpdateStatus: (status: MilestoneStatus) => Promise<void>;
  onAddNote: (noteText: string) => Promise<void>;
}

export const MilestoneDetailModal: React.FC<MilestoneDetailModalProps> = ({
  milestone,
  isOpen,
  onClose,
  onUpdateStatus,
  onAddNote,
}) => {
  const [newNoteText, setNewNoteText] = useState('');
  const [isSubmittingNote, setIsSubmittingNote] = useState(false);
  const [isUpdatingStatus, setIsUpdatingStatus] = useState(false);

  if (!isOpen || !milestone) return null;

  const handleStatusChange = async (newStatus: MilestoneStatus) => {
    try {
      setIsUpdatingStatus(true);
      await onUpdateStatus(newStatus);
    } finally {
      setIsUpdatingStatus(false);
    }
  };

  const handleNoteSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newNoteText.trim()) return;

    try {
      setIsSubmittingNote(true);
      await onAddNote(newNoteText.trim());
      setNewNoteText('');
    } finally {
      setIsSubmittingNote(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-charcoal-900/50 backdrop-blur-sm animate-fade-in"
      onClick={onClose}
    >
      <div
        className="bg-white w-full max-w-2xl rounded-3xl shadow-warm-lg border border-stone-200 overflow-hidden flex flex-col max-h-[90vh]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="p-5 sm:p-6 border-b border-stone-100 flex items-start justify-between gap-4 bg-ivory-50/50">
          <div className="space-y-1">
            <div className="flex items-center gap-2 flex-wrap">
              <Badge
                variant={
                  milestone.status === 'completed'
                    ? 'sage'
                    : milestone.status === 'in_progress'
                    ? 'teal'
                    : 'stone'
                }
                size="sm"
              >
                {milestone.status.replace(/_/g, ' ')}
              </Badge>
              {milestone.target_age_months !== null && milestone.target_age_months !== undefined && (
                <span className="text-xs font-bold text-charcoal-600 bg-white px-2.5 py-0.5 rounded-full border border-stone-200/80">
                  Target: {milestone.target_age_months === 0 ? 'Birth' : `${milestone.target_age_months} Months`}
                </span>
              )}
            </div>
            <h2 className="font-heading font-bold text-lg sm:text-xl text-teal-900">
              {milestone.title}
            </h2>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-xl text-charcoal-400 hover:text-charcoal-800 hover:bg-stone-100 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Scrollable Body */}
        <div className="p-5 sm:p-6 space-y-6 overflow-y-auto flex-1">
          {/* Milestone Description */}
          <div className="p-4 bg-stone-50/60 rounded-2xl border border-stone-100 text-sm text-charcoal-800 leading-relaxed">
            {milestone.description}
          </div>

          {/* Status Quick Switcher */}
          <div>
            <label className="block text-xs font-bold text-charcoal-700 uppercase tracking-wider mb-2">
              Update Milestone Status
            </label>
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                disabled={isUpdatingStatus}
                onClick={() => handleStatusChange('upcoming')}
                className={`py-2 px-3 text-xs font-bold rounded-xl border flex items-center justify-center gap-1.5 transition ${
                  milestone.status === 'upcoming'
                    ? 'bg-stone-800 text-white border-stone-800 shadow-sm'
                    : 'bg-white text-charcoal-700 border-stone-200 hover:bg-stone-50'
                }`}
              >
                <Circle className="w-3.5 h-3.5" />
                <span>Upcoming</span>
              </button>

              <button
                type="button"
                disabled={isUpdatingStatus}
                onClick={() => handleStatusChange('in_progress')}
                className={`py-2 px-3 text-xs font-bold rounded-xl border flex items-center justify-center gap-1.5 transition ${
                  milestone.status === 'in_progress'
                    ? 'bg-teal-900 text-white border-teal-900 shadow-sm'
                    : 'bg-white text-charcoal-700 border-stone-200 hover:bg-stone-50'
                }`}
              >
                <Clock className="w-3.5 h-3.5" />
                <span>In Progress</span>
              </button>

              <button
                type="button"
                disabled={isUpdatingStatus}
                onClick={() => handleStatusChange('completed')}
                className={`py-2 px-3 text-xs font-bold rounded-xl border flex items-center justify-center gap-1.5 transition ${
                  milestone.status === 'completed'
                    ? 'bg-sage-600 text-white border-sage-600 shadow-sm'
                    : 'bg-white text-charcoal-700 border-stone-200 hover:bg-stone-50'
                }`}
              >
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Completed</span>
              </button>
            </div>
          </div>

          {/* Notes & Memories Section */}
          <div className="space-y-4 pt-2 border-t border-stone-100">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <MessageSquare className="w-4 h-4 text-coral-500" />
                <h3 className="font-heading font-bold text-sm text-teal-900">
                  Family Memories & Clinical Notes ({milestone.notes.length})
                </h3>
              </div>
            </div>

            {/* Note Submission Input */}
            <form onSubmit={handleNoteSubmit} className="space-y-2">
              <textarea
                rows={2}
                value={newNoteText}
                onChange={(e) => setNewNoteText(e.target.value)}
                placeholder="Add a milestone note, clinic feedback, or personal memory..."
                className="w-full bg-white border border-stone-200 rounded-xl px-3.5 py-2 text-xs text-charcoal-900 placeholder:text-charcoal-400 focus:outline-none focus:ring-2 focus:ring-teal-700/20 focus:border-teal-900 transition resize-none"
              />
              <div className="flex justify-end">
                <Button
                  type="submit"
                  size="sm"
                  variant="primary"
                  isLoading={isSubmittingNote}
                  disabled={!newNoteText.trim()}
                  rightIcon={<Send className="w-3 h-3" />}
                >
                  Save Note
                </Button>
              </div>
            </form>

            {/* Notes Timeline List */}
            <div className="space-y-2.5 pt-2">
              {milestone.notes.length === 0 ? (
                <p className="text-xs text-charcoal-400 italic text-center py-3">
                  No notes recorded yet. Add the first family memory above.
                </p>
              ) : (
                milestone.notes.map((note) => (
                  <div
                    key={note.id}
                    className="p-3 bg-ivory-50 rounded-xl border border-stone-200/70 text-xs text-charcoal-800 space-y-1"
                  >
                    <div className="flex items-center justify-between text-[10px] text-charcoal-500 font-semibold">
                      <span>{note.author_name || 'Caregiver'}</span>
                      <span>{new Date(note.created_at).toLocaleDateString()}</span>
                    </div>
                    <p className="whitespace-pre-wrap">{note.note_text}</p>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="p-4 bg-stone-50 border-t border-stone-100 flex justify-end">
          <Button variant="outline" size="sm" onClick={onClose}>
            Close
          </Button>
        </div>
      </div>
    </div>
  );
};
