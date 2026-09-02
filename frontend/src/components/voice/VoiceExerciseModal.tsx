import React from 'react';
import { X, Mic, Sparkles, CheckCircle2 } from 'lucide-react';
import { VoiceExercise } from '../../types';
import { Button } from '../ui/Button';

interface VoiceExerciseModalProps {
  exercise: VoiceExercise | null;
  isOpen: boolean;
  onClose: () => void;
  onStartPractice: (exercise: VoiceExercise) => void;
}

export const VoiceExerciseModal: React.FC<VoiceExerciseModalProps> = ({
  exercise,
  isOpen,
  onClose,
  onStartPractice,
}) => {
  if (!isOpen || !exercise) return null;

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
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h2 className="font-heading font-bold text-lg text-teal-900">
                {exercise.title}
              </h2>
              <span className="text-[11px] text-charcoal-500">
                Difficulty: {exercise.difficulty_level.toUpperCase()}
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

        {/* Modal Body */}
        <div className="p-5 space-y-4 overflow-y-auto flex-1 text-xs">
          {/* Target Phonemes */}
          <div>
            <span className="block font-bold text-charcoal-700 mb-1.5">
              Target Sounds / Phonemes:
            </span>
            <div className="flex flex-wrap gap-1.5">
              {exercise.target_phonemes.map((ph, idx) => (
                <span
                  key={idx}
                  className="font-mono font-bold text-teal-900 bg-teal-50 px-2.5 py-1 rounded-lg border border-teal-100"
                >
                  /{ph}/
                </span>
              ))}
            </div>
          </div>

          {/* Prompt Box */}
          <div>
            <span className="block font-bold text-charcoal-700 mb-1">
              Practice Prompt / Game Text:
            </span>
            <div className="p-3.5 bg-ivory-50 border border-stone-200 rounded-2xl">
              <p className="text-sm font-semibold text-charcoal-900 leading-relaxed">
                "{exercise.prompt_text}"
              </p>
            </div>
          </div>

          {/* Detailed Instructions */}
          <div>
            <span className="block font-bold text-charcoal-700 mb-1">
              Caregiver Instructions & Sound Modeling Tips:
            </span>
            <p className="text-charcoal-700 bg-stone-50 p-3 rounded-2xl border border-stone-100 leading-relaxed whitespace-pre-wrap">
              {exercise.instructions}
            </p>
          </div>

          {/* Educational Note */}
          <div className="p-3 bg-teal-50/40 rounded-2xl border border-teal-100 flex items-start gap-2 text-[11px] text-charcoal-600">
            <CheckCircle2 className="w-3.5 h-3.5 text-teal-900 flex-shrink-0 mt-0.5" />
            <span>
              Focus on relaxed play and sound exploration. Stop if your child becomes fatigued or disinterested.
            </span>
          </div>

          {/* Actions */}
          <div className="pt-3 border-t border-stone-100 flex items-center justify-end gap-2">
            <Button variant="outline" size="sm" onClick={onClose}>
              Close
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={() => {
                onClose();
                onStartPractice(exercise);
              }}
              leftIcon={<Mic className="w-3.5 h-3.5" />}
            >
              Start Recording
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};
