import React from 'react';
import { Sparkles, ShieldCheck } from 'lucide-react';
import { PathGuideSuggestedPrompt } from '../../types';
import { PathGuideSuggestedPrompts } from './PathGuideSuggestedPrompts';

interface PathGuideEmptyStateProps {
  prompts: PathGuideSuggestedPrompt[];
  onSelectPrompt: (promptText: string) => void;
}

export const PathGuideEmptyState: React.FC<PathGuideEmptyStateProps> = ({
  prompts,
  onSelectPrompt,
}) => {
  return (
    <div className="flex-1 flex flex-col justify-center items-center text-center p-6 max-w-xl mx-auto space-y-6">
      <div className="space-y-2">
        <div className="w-12 h-12 rounded-2xl bg-teal-900 text-white flex items-center justify-center mx-auto shadow-warm-sm">
          <Sparkles className="w-6 h-6 text-coral-400" />
        </div>
        <h3 className="font-heading font-bold text-lg text-teal-900">
          How can PathGuide assist your journey today?
        </h3>
        <p className="text-xs text-charcoal-600 leading-relaxed">
          Ask questions about specialized feeding equipment, preparation for upcoming surgical milestones, speech exploration games, or recovery home routines.
        </p>
      </div>

      <div className="w-full">
        <PathGuideSuggestedPrompts prompts={prompts} onSelectPrompt={onSelectPrompt} />
      </div>

      <div className="flex items-center gap-1.5 text-[11px] text-charcoal-600 bg-stone-50 px-3 py-1.5 rounded-full border border-stone-200/70">
        <ShieldCheck className="w-3.5 h-3.5 text-teal-800" />
        <span>Grounded in verified CleftPath educational resources • Non-diagnostic</span>
      </div>
    </div>
  );
};
