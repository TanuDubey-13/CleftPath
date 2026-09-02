import React, { useState } from 'react';
import { X, ShieldAlert, CheckCircle2 } from 'lucide-react';
import { Button } from '../ui/Button';

interface VillageReportModalProps {
  isOpen: boolean;
  targetType: 'post' | 'comment';
  targetId: string;
  onClose: () => void;
  onSubmitReport: (targetId: string, reason: string, details?: string) => Promise<void>;
}

const REPORT_REASONS = [
  { id: 'medical_misinformation', label: 'Medical Misinformation / Unverified Claims' },
  { id: 'harassment', label: 'Harassment or Disrespectful Behavior' },
  { id: 'hate_or_abuse', label: 'Hate Speech or Abusive Language' },
  { id: 'privacy_violation', label: 'Privacy Violation / Personal Health Info of Others' },
  { id: 'spam', label: 'Spam or Commercial Promotion' },
  { id: 'other', label: 'Other Concern' },
];

export const VillageReportModal: React.FC<VillageReportModalProps> = ({
  isOpen,
  targetType,
  targetId,
  onClose,
  onSubmitReport,
}) => {
  const [selectedReason, setSelectedReason] = useState('medical_misinformation');
  const [details, setDetails] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await onSubmitReport(targetId, selectedReason, details.trim() || undefined);
      setIsSuccess(true);
      setTimeout(() => {
        setIsSuccess(false);
        onClose();
      }, 1500);
    } catch (err) {
      // Error handled by parent toast or error message
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-charcoal-900/50 backdrop-blur-sm animate-fadeIn"
      onClick={onClose}
    >
      <div
        className="bg-white w-full max-w-md rounded-3xl shadow-warm-lg border border-stone-200 overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="p-5 border-b border-stone-100 flex items-center justify-between bg-ivory-50/50">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-coral-50 text-coral-600 flex items-center justify-center">
              <ShieldAlert className="w-4 h-4" />
            </div>
            <h3 className="font-heading font-bold text-base text-teal-900">
              Report {targetType === 'post' ? 'Post' : 'Comment'}
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-xl text-charcoal-400 hover:text-charcoal-800 hover:bg-stone-100 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        {isSuccess ? (
          <div className="p-8 text-center space-y-3">
            <CheckCircle2 className="w-10 h-10 text-emerald-600 mx-auto animate-bounce" />
            <h4 className="font-heading font-bold text-base text-teal-900">
              Report Submitted
            </h4>
            <p className="text-xs text-charcoal-600">
              Thank you for keeping The Village safe and supportive. Our moderation team has been alerted.
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="p-5 space-y-4 text-xs">
            <div className="space-y-1.5">
              <label className="block font-bold text-charcoal-800">
                Why are you reporting this {targetType}?
              </label>
              <div className="space-y-1.5">
                {REPORT_REASONS.map((r) => (
                  <label
                    key={r.id}
                    className={`flex items-center gap-2.5 p-2.5 rounded-xl border cursor-pointer transition ${
                      selectedReason === r.id
                        ? 'bg-coral-50/50 border-coral-300 text-coral-950 font-semibold'
                        : 'border-stone-200 hover:bg-stone-50 text-charcoal-700'
                    }`}
                  >
                    <input
                      type="radio"
                      name="report_reason"
                      value={r.id}
                      checked={selectedReason === r.id}
                      onChange={(e) => setSelectedReason(e.target.value)}
                      className="text-coral-600 focus:ring-coral-500"
                    />
                    <span>{r.label}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="space-y-1">
              <label className="block font-bold text-charcoal-800">
                Additional Details (Optional)
              </label>
              <textarea
                rows={2}
                value={details}
                onChange={(e) => setDetails(e.target.value)}
                placeholder="Provide helpful context for moderators..."
                maxLength={1000}
                className="w-full p-2.5 bg-stone-50 border border-stone-200 rounded-xl outline-none focus:border-teal-700 focus:ring-1 focus:ring-teal-700 text-xs"
              />
            </div>

            <div className="pt-2 border-t border-stone-100 flex items-center justify-end gap-2">
              <Button type="button" variant="outline" size="sm" onClick={onClose} disabled={isSubmitting}>
                Cancel
              </Button>
              <Button type="submit" variant="primary" size="sm" isLoading={isSubmitting}>
                Submit Report
              </Button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};
