import React from 'react';
import { Mic, Volume2, Info } from 'lucide-react';
import { VoiceExercise } from '../../types';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';

interface VoiceExerciseCardProps {
  exercise: VoiceExercise;
  onSelectPractice: (exercise: VoiceExercise) => void;
  onViewDetails: (exercise: VoiceExercise) => void;
}

const DIFFICULTY_BADGE: Record<string, 'sage' | 'teal' | 'coral' | 'stone'> = {
  beginner: 'sage',
  intermediate: 'teal',
  advanced: 'coral',
};

export const VoiceExerciseCard: React.FC<VoiceExerciseCardProps> = ({
  exercise,
  onSelectPractice,
  onViewDetails,
}) => {
  return (
    <Card className="p-5 bg-white border border-stone-200/80 rounded-3xl hover:border-teal-700/30 hover:shadow-warm-xs transition flex flex-col justify-between gap-4">
      <div className="space-y-3">
        {/* Top Header */}
        <div className="flex items-start justify-between gap-2">
          <div className="space-y-1">
            <h3 className="font-heading font-bold text-base text-teal-900 leading-snug">
              {exercise.title}
            </h3>
            {exercise.stage_id && (
              <span className="text-[11px] font-semibold text-charcoal-500">
                Journey Stage {exercise.stage_id}
              </span>
            )}
          </div>

          <Badge variant={DIFFICULTY_BADGE[exercise.difficulty_level] || 'stone'} size="sm">
            {exercise.difficulty_level.toUpperCase()}
          </Badge>
        </div>

        {/* Target Phonemes */}
        <div className="flex flex-wrap items-center gap-1.5 pt-1">
          <span className="text-[11px] font-bold text-charcoal-500 mr-1 flex items-center gap-1">
            <Volume2 className="w-3 h-3 text-teal-900" />
            <span>Target Sounds:</span>
          </span>
          {exercise.target_phonemes.map((ph, idx) => (
            <span
              key={idx}
              className="text-[11px] font-mono font-bold text-teal-900 bg-teal-50 px-2 py-0.5 rounded-md border border-teal-100"
            >
              /{ph}/
            </span>
          ))}
        </div>

        {/* Prompt Text */}
        <div className="p-3 bg-ivory-50/70 border border-stone-200/70 rounded-2xl">
          <p className="text-xs text-charcoal-800 italic font-medium leading-relaxed">
            "{exercise.prompt_text}"
          </p>
        </div>

        {/* Instructions Snippet */}
        <p className="text-xs text-charcoal-600 line-clamp-2 leading-relaxed">
          {exercise.instructions}
        </p>
      </div>

      {/* Actions */}
      <div className="pt-2 border-t border-stone-100 flex items-center justify-between gap-2">
        <button
          type="button"
          onClick={() => onViewDetails(exercise)}
          className="text-xs font-semibold text-charcoal-600 hover:text-teal-900 flex items-center gap-1 transition"
        >
          <Info className="w-3.5 h-3.5" />
          <span>Details</span>
        </button>

        <Button
          variant="primary"
          size="sm"
          onClick={() => onSelectPractice(exercise)}
          leftIcon={<Mic className="w-3.5 h-3.5" />}
        >
          Start Practice
        </Button>
      </div>
    </Card>
  );
};
