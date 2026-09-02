import React from 'react';
import { Sparkles, User as UserIcon, BookOpen, AlertCircle } from 'lucide-react';
import { PathGuideCitation, PathGuideMessage as IPathGuideMessage } from '../../types';

interface PathGuideMessageProps {
  message: IPathGuideMessage;
  onSelectCitation: (citation: PathGuideCitation) => void;
}

export const PathGuideMessage: React.FC<PathGuideMessageProps> = ({
  message,
  onSelectCitation,
}) => {
  const isUser = message.role === 'user';
  const hasEmergencyTrigger = message.safety_flags?.emergency_trigger_detected;
  const timeStr = new Date(message.created_at).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} space-y-1.5 animate-fadeIn`}>
      <div className={`flex items-start gap-2.5 max-w-2xl ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        {/* Avatar */}
        <div
          className={`w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 shadow-warm-xs ${
            isUser ? 'bg-teal-900 text-white' : 'bg-coral-500 text-white'
          }`}
        >
          {isUser ? <UserIcon className="w-4 h-4" /> : <Sparkles className="w-4 h-4" />}
        </div>

        {/* Bubble */}
        <div
          className={`p-4 rounded-3xl text-xs sm:text-sm leading-relaxed shadow-warm-xs ${
            isUser
              ? 'bg-teal-900 text-white rounded-tr-none'
              : 'bg-white border border-stone-200/90 text-charcoal-900 rounded-tl-none space-y-3'
          }`}
        >
          {/* Content */}
          <div className="whitespace-pre-wrap">{message.content}</div>

          {/* Emergency Alert Badge in Assistant message if flagged */}
          {hasEmergencyTrigger && !isUser && (
            <div className="p-2.5 bg-coral-50 border border-coral-200 rounded-xl text-coral-800 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-coral-600 flex-shrink-0" />
              <span className="font-semibold">
                Urgent symptom note: please prioritize clinical evaluation.
              </span>
            </div>
          )}

          {/* Citations List if Assistant */}
          {!isUser && message.citations && message.citations.length > 0 && (
            <div className="pt-2 border-t border-stone-100 flex flex-wrap items-center gap-1.5">
              <span className="text-[11px] font-bold text-charcoal-500 mr-1 flex items-center gap-1">
                <BookOpen className="w-3 h-3 text-teal-900" />
                <span>Sources:</span>
              </span>
              {message.citations.map((c, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => onSelectCitation(c)}
                  className="text-[10px] font-semibold text-teal-900 bg-teal-50 hover:bg-teal-100 px-2 py-0.5 rounded-lg border border-teal-100 transition flex items-center gap-1"
                >
                  <span>{c.title}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Timestamp */}
      <span className="text-[10px] text-charcoal-600 px-2">{timeStr}</span>
    </div>
  );
};
