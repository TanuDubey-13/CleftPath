import React, { useState } from 'react';
import { X, Calendar, Clock, MapPin, Phone, Mail, HelpCircle, FileText, AlertTriangle } from 'lucide-react';
import { Appointment } from '../../types';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';

interface AppointmentDetailModalProps {
  appointment: Appointment | null;
  isOpen: boolean;
  onClose: () => void;
  onCancel: (appointmentId: string) => Promise<void>;
}

export const AppointmentDetailModal: React.FC<AppointmentDetailModalProps> = ({
  appointment,
  isOpen,
  onClose,
  onCancel,
}) => {
  const [isConfirmingCancel, setIsConfirmingCancel] = useState(false);
  const [isCancelling, setIsCancelling] = useState(false);

  if (!isOpen || !appointment) return null;

  const dateObj = new Date(appointment.scheduled_at);
  const formattedDate = dateObj.toLocaleDateString(undefined, {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  });
  const formattedTime = dateObj.toLocaleTimeString(undefined, {
    hour: 'numeric',
    minute: '2-digit',
  });

  const handleConfirmCancel = async () => {
    try {
      setIsCancelling(true);
      await onCancel(appointment.id);
      setIsConfirmingCancel(false);
      onClose();
    } finally {
      setIsCancelling(false);
    }
  };

  const isCancelled = appointment.status === 'cancelled';
  const isCompleted = appointment.status === 'completed';

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
                  isCompleted ? 'sage' : isCancelled ? 'stone' : 'coral'
                }
                size="sm"
              >
                {appointment.status.replace(/_/g, ' ').toUpperCase()}
              </Badge>
              <span className="text-xs font-bold text-charcoal-600 bg-white px-2.5 py-0.5 rounded-full border border-stone-200/80">
                {appointment.duration_minutes} Minutes
              </span>
            </div>
            <h2 className="font-heading font-bold text-lg sm:text-xl text-teal-900">
              {appointment.specialist_name}
            </h2>
            <p className="text-xs font-semibold text-charcoal-600">
              {appointment.specialty}
            </p>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-xl text-charcoal-400 hover:text-charcoal-800 hover:bg-stone-100 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Scrollable Body */}
        <div className="p-5 sm:p-6 space-y-5 overflow-y-auto flex-1">
          {/* Schedule & Location Card */}
          <div className="p-4 bg-teal-50/40 rounded-2xl border border-teal-100/80 space-y-2.5">
            <div className="flex items-center gap-2 text-xs font-bold text-teal-900">
              <Calendar className="w-4 h-4 text-coral-500" />
              <span>{formattedDate}</span>
              <span>•</span>
              <Clock className="w-4 h-4 text-teal-900" />
              <span>{formattedTime}</span>
            </div>

            {appointment.clinic_location && (
              <div className="flex items-start gap-2 text-xs text-charcoal-700">
                <MapPin className="w-4 h-4 text-coral-500 flex-shrink-0 mt-0.5" />
                <span>{appointment.clinic_location}</span>
              </div>
            )}

            {appointment.care_team_member && (
              <div className="pt-2 border-t border-teal-100/60 flex flex-wrap gap-4 text-xs text-charcoal-600">
                {appointment.care_team_member.contact_phone && (
                  <div className="flex items-center gap-1">
                    <Phone className="w-3.5 h-3.5 text-teal-900" />
                    <span>{appointment.care_team_member.contact_phone}</span>
                  </div>
                )}
                {appointment.care_team_member.contact_email && (
                  <div className="flex items-center gap-1">
                    <Mail className="w-3.5 h-3.5 text-teal-900" />
                    <span>{appointment.care_team_member.contact_email}</span>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Specialist Prep Questions */}
          <div className="space-y-2">
            <div className="flex items-center gap-1.5">
              <HelpCircle className="w-4 h-4 text-coral-500" />
              <h3 className="font-heading font-bold text-sm text-teal-900">
                Specialist Visit Questions ({appointment.prep_questions?.length || 0})
              </h3>
            </div>

            {!appointment.prep_questions || appointment.prep_questions.length === 0 ? (
              <p className="text-xs text-charcoal-400 italic p-3 bg-stone-50 rounded-xl border border-stone-100">
                No preparation questions recorded for this appointment.
              </p>
            ) : (
              <ul className="space-y-2">
                {appointment.prep_questions.map((q, idx) => (
                  <li
                    key={idx}
                    className="p-3 bg-white rounded-xl border border-stone-200/80 text-xs text-charcoal-800 flex items-start gap-2.5 shadow-sm"
                  >
                    <span className="w-5 h-5 rounded-full bg-coral-50 text-coral-600 flex items-center justify-center font-bold text-[10px] flex-shrink-0">
                      {idx + 1}
                    </span>
                    <span className="leading-relaxed">{q}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Summary / Clinical Notes */}
          {appointment.summary_notes && (
            <div className="space-y-1.5">
              <div className="flex items-center gap-1.5">
                <FileText className="w-4 h-4 text-teal-900" />
                <h3 className="font-heading font-bold text-sm text-teal-900">
                  Caregiver Notes & Clinical Summary
                </h3>
              </div>
              <div className="p-3.5 bg-stone-50 rounded-2xl border border-stone-200/80 text-xs text-charcoal-800 whitespace-pre-wrap leading-relaxed">
                {appointment.summary_notes}
              </div>
            </div>
          )}

          {/* Destructive Cancel Confirmation State */}
          {isConfirmingCancel && (
            <div className="p-4 bg-coral-50 border border-coral-200 rounded-2xl space-y-3 animate-fade-in">
              <div className="flex items-start gap-2 text-coral-800 text-xs font-semibold">
                <AlertTriangle className="w-4 h-4 text-coral-600 flex-shrink-0 mt-0.5" />
                <span>Are you sure you want to cancel this visit with {appointment.specialist_name}?</span>
              </div>
              <div className="flex justify-end gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => setIsConfirmingCancel(false)}
                >
                  Keep Appointment
                </Button>
                <Button
                  size="sm"
                  variant="primary"
                  isLoading={isCancelling}
                  onClick={handleConfirmCancel}
                >
                  Yes, Cancel Visit
                </Button>
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="p-4 bg-stone-50 border-t border-stone-100 flex items-center justify-between">
          <div>
            {!isCancelled && !isCompleted && !isConfirmingCancel && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsConfirmingCancel(true)}
                className="text-coral-600 border-coral-200 hover:bg-coral-50"
              >
                Cancel Appointment
              </Button>
            )}
          </div>

          <Button variant="outline" size="sm" onClick={onClose}>
            Close
          </Button>
        </div>
      </div>
    </div>
  );
};
