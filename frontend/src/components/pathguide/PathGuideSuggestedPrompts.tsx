import React from 'react';
import { Sparkles, ArrowRight } from 'lucide-react';
import { PathGuideSuggestedPrompt } from '../../types';
import { Card } from '../ui/Card';

interface PathGuideSuggestedPromptsProps {
  prompts: PathGuideSuggestedPrompt[];
  onSelectPrompt: (promptText: string) => void;
}

export const PathGuideSuggestedPrompts: React.FC<PathGuideSuggestedPromptsProps> = ({
  prompts,
  onSelectPrompt,
}) => {
  if (!prompts || prompts.length === 0) return null;

  return (
    <div className="space-y-2.5">
      <div className="flex items-center gap-1.5 text-xs font-bold text-teal-900">
        <Sparkles className="w-3.5 h-3.5 text-coral-500" />
        <span>Educational Starter Questions:</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
        {prompts.map((p) => (
          <Card
            key={p.id}
            onClick={() => onSelectPrompt(p.prompt)}
            className="p-3 bg-white border border-stone-200/80 rounded-2xl hover:border-teal-700/40 hover:shadow-warm-xs cursor-pointer transition flex flex-col justify-between gap-1.5 group text-left"
          >
            <div className="space-y-0.5">
              <span className="text-[10px] font-bold text-teal-800 uppercase tracking-wider">
                {p.category}
              </span>
              <p className="text-xs font-semibold text-charcoal-900 group-hover:text-teal-900 transition">
                {p.prompt}
              </p>
            </div>

            <div className="flex items-center justify-between text-[10px] text-charcoal-600 pt-1">
              <span>{p.description}</span>
              <ArrowRight className="w-3 h-3 text-teal-700 opacity-0 group-hover:opacity-100 transition transform group-hover:translate-x-0.5" />
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};
