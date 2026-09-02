import React, { useState } from 'react';
import { X, Calendar, Plus, Trash2 } from 'lucide-react';
import { AppointmentCreateRequest, CareTeamMemberSummary } from '../../types';
import { Button } from '../ui/Button';

interface AppointmentFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: AppointmentCreateRequest) => Promise<void>;
  careTeamMembers?: CareTeamMemberSummary[];
}

const COMMON_SPECIALTIES = [
  'Plastic & Reconstructive Cleft Surgeon',
  'Speech-Language Pathologist',
  'Pediatric Otolaryngologist (ENT)',
  'Pediatric Craniofacial Orthodontist',
  'Pediatric Dentist',
  'Feeding Specialist / IBCLC',
  'Audiologist',
  'Pediatrician',
];

export const AppointmentFormModal: React.FC<AppointmentFormModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  careTeamMembers = [],
}) => {
  const [specialistName, setSpecialistName] = useState('');
  const [specialty, setSpecialty] = useState(COMMON_SPECIALTIES[0]);
  const [clinicLocation, setClinicLocation] = useState('');
  const [scheduledAt, setScheduledAt] = useState('');
  const [durationMinutes, setDurationMinutes] = useState(30);
  const [prepQuestions, setPrepQuestions] = useState<string[]>(['']);
  const [summaryNotes, setSummaryNotes] = useState('');
  const [selectedCareTeamId, setSelectedCareTeamId] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleCareTeamSelect = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const memberId = e.target.value;
    setSelectedCareTeamId(memberId);

    const member = careTeamMembers.find((m) => m.id === memberId);
    if (member) {
      setSpecialistName(member.specialist_name);
      setSpecialty(member.specialty);
      if (member.clinic_or_hospital) {
        setClinicLocation(member.clinic_or_hospital);
      }
    }
  };

  const handleAddQuestion = () => {
    setPrepQuestions([...prepQuestions, '']);
  };

  const handleQuestionChange = (index: number, val: string) => {
    const updated = [...prepQuestions];
    updated[index] = val;
    setPrepQuestions(updated);
  };

  const handleRemoveQuestion = (index: number) => {
    setPrepQuestions(prepQuestions.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!specialistName.trim() || !specialty.trim() || !scheduledAt) return;

    try {
      setIsSubmitting(true);
      const cleanedQuestions = prepQuestions.map((q) => q.trim()).filter(Boolean);

      const payload: AppointmentCreateRequest = {
        specialist_name: specialistName.trim(),
        specialty: specialty.trim(),
        clinic_location: clinicLocation.trim() || undefined,
        scheduled_at: new Date(scheduledAt).toISOString(),
        duration_minutes: durationMinutes,
        prep_questions: cleanedQuestions,
        summary_notes: summaryNotes.trim() || undefined,
        care_team_member_id: selectedCareTeamId || undefined,
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
        className="bg-white w-full max-w-2xl rounded-3xl shadow-warm-lg border border-stone-200 overflow-hidden flex flex-col max-h-[92vh]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="p-5 sm:p-6 border-b border-stone-100 flex items-center justify-between bg-ivory-50/50">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-teal-50 text-teal-900 flex items-center justify-center">
              <Calendar className="w-4 h-4" />
            </div>
            <div>
              <h2 className="font-heading font-bold text-lg text-teal-900">
                Schedule New Care Visit
              </h2>
              <p className="text-[11px] text-charcoal-600">
                Record an upcoming clinic or specialist consultation.
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
        <form onSubmit={handleSubmit} className="p-5 sm:p-6 space-y-4 overflow-y-auto flex-1 text-xs">
          {/* Linked Care Team Specialist Picker */}
          {careTeamMembers.length > 0 && (
            <div>
              <label className="block font-bold text-charcoal-700 mb-1">
                Select from Care Team (Optional)
              </label>
              <select
                value={selectedCareTeamId}
                onChange={handleCareTeamSelect}
                className="w-full bg-stone-50 border border-stone-200 rounded-xl px-3 py-2 text-charcoal-900 focus:outline-none focus:ring-2 focus:ring-teal-700/20 focus:border-teal-900"
              >
                <option value="">-- Choose known specialist or enter manually --</option>
                {careTeamMembers.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.specialist_name} ({m.specialty})
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Specialist Name & Specialty */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block font-bold text-charcoal-700 mb-1">
                Specialist Name *
              </label>
              <input
                type="text"
                required
                placeholder="e.g. Dr. Robert Sterling"
                value={specialistName}
                onChange={(e) => setSpecialistName(e.target.value)}
                className="w-full bg-white border border-stone-200 rounded-xl px-3 py-2 text-charcoal-900 focus:outline-none focus:ring-2 focus:ring-teal-700/20 focus:border-teal-900"
              />
            </div>

            <div>
              <label className="block font-bold text-charcoal-700 mb-1">
                Specialty *
              </label>
              <input
                type="text"
                required
                list="specialty-presets"
                placeholder="e.g. Plastic Cleft Surgeon"
                value={specialty}
                onChange={(e) => setSpecialty(e.target.value)}
                className="w-full bg-white border border-stone-200 rounded-xl px-3 py-2 text-charcoal-900 focus:outline-none focus:ring-2 focus:ring-teal-700/20 focus:border-teal-900"
              />
              <datalist id="specialty-presets">
                {COMMON_SPECIALTIES.map((spec) => (
                  <option key={spec} value={spec} />
                ))}
              </datalist>
            </div>
          </div>

          {/* Location */}
          <div>
            <label className="block font-bold text-charcoal-700 mb-1">
              Clinic or Hospital Location
            </label>
            <input
              type="text"
              placeholder="e.g. Children's Craniofacial Center, Suite 402"
              value={clinicLocation}
              onChange={(e) => setClinicLocation(e.target.value)}
              className="w-full bg-white border border-stone-200 rounded-xl px-3 py-2 text-charcoal-900 focus:outline-none focus:ring-2 focus:ring-teal-700/20 focus:border-teal-900"
            />
          </div>

          {/* Date/Time & Duration */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block font-bold text-charcoal-700 mb-1">
                Scheduled Date & Time *
              </label>
              <input
                type="datetime-local"
                required
                value={scheduledAt}
                onChange={(e) => setScheduledAt(e.target.value)}
                className="w-full bg-white border border-stone-200 rounded-xl px-3 py-2 text-charcoal-900 focus:outline-none focus:ring-2 focus:ring-teal-700/20 focus:border-teal-900"
              />
            </div>

            <div>
              <label className="block font-bold text-charcoal-700 mb-1">
                Expected Duration
              </label>
              <select
                value={durationMinutes}
                onChange={(e) => setDurationMinutes(Number(e.target.value))}
                className="w-full bg-white border border-stone-200 rounded-xl px-3 py-2 text-charcoal-900 focus:outline-none focus:ring-2 focus:ring-teal-700/20 focus:border-teal-900"
              >
                <option value={15}>15 Minutes (Brief Follow-up)</option>
                <option value={30}>30 Minutes (Standard Consult)</option>
                <option value={45}>45 Minutes (Comprehensive)</option>
                <option value={60}>60 Minutes (Team Evaluation)</option>
                <option value={90}>90 Minutes (Pre-Op Workup)</option>
              </select>
            </div>
          </div>

          {/* Prep Questions */}
          <div className="space-y-2 pt-2 border-t border-stone-100">
            <div className="flex items-center justify-between">
              <label className="font-bold text-charcoal-700">
                Questions to Ask the Specialist
              </label>
              <button
                type="button"
                onClick={handleAddQuestion}
                className="text-teal-900 hover:text-coral-600 font-semibold text-[11px] flex items-center gap-1 transition"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Add Question</span>
              </button>
            </div>

            {prepQuestions.map((q, idx) => (
              <div key={idx} className="flex items-center gap-2">
                <input
                  type="text"
                  placeholder={`Question ${idx + 1}, e.g. What is the fasting window before surgery?`}
                  value={q}
                  onChange={(e) => handleQuestionChange(idx, e.target.value)}
                  className="flex-1 bg-white border border-stone-200 rounded-xl px-3 py-1.5 text-charcoal-900 focus:outline-none focus:ring-2 focus:ring-teal-700/20 focus:border-teal-900"
                />
                {prepQuestions.length > 1 && (
                  <button
                    type="button"
                    onClick={() => handleRemoveQuestion(idx)}
                    className="p-1.5 text-charcoal-400 hover:text-coral-600 transition"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
            ))}
          </div>

          {/* Caregiver Notes */}
          <div className="pt-2 border-t border-stone-100">
            <label className="block font-bold text-charcoal-700 mb-1">
              Private Caregiver Notes (Optional)
            </label>
            <textarea
              rows={2}
              placeholder="Any specific reminders, parking instructions, or items to bring..."
              value={summaryNotes}
              onChange={(e) => setSummaryNotes(e.target.value)}
              className="w-full bg-white border border-stone-200 rounded-xl px-3 py-2 text-charcoal-900 focus:outline-none focus:ring-2 focus:ring-teal-700/20 focus:border-teal-900 resize-none"
            />
          </div>

          {/* Form Actions */}
          <div className="pt-4 border-t border-stone-100 flex items-center justify-end gap-2">
            <Button variant="outline" size="sm" type="button" onClick={onClose}>
              Cancel
            </Button>
            <Button
              variant="primary"
              size="sm"
              type="submit"
              isLoading={isSubmitting}
              disabled={!specialistName.trim() || !scheduledAt}
            >
              Save Appointment
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
