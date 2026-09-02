import React from 'react';
import { ShieldAlert } from 'lucide-react';
import { Card } from '../ui/Card';

export const VoiceSafetyNotice: React.FC = () => {
  return (
    <Card className="p-4 sm:p-5 bg-teal-50/50 border border-teal-200/60 rounded-3xl shadow-warm-xs">
      <div className="flex items-start gap-3.5">
        <div className="w-8 h-8 rounded-xl bg-teal-100 text-teal-900 flex items-center justify-center flex-shrink-0 mt-0.5">
          <ShieldAlert className="w-4 h-4 text-teal-900" />
        </div>
        <div className="space-y-1 text-xs">
          <h4 className="font-heading font-bold text-teal-900">
            Speech Practice & Educational Notice
          </h4>
          <p className="text-charcoal-600 leading-relaxed">
            Voice Journey provides educational speech exploration and practice journal tracking. It does not diagnose speech disorders, assess articulation or resonance clinically, or replace care from your licensed Speech-Language Pathologist (SLP). Always practice according to your cleft team's tailored guidance.
          </p>
        </div>
      </div>
    </Card>
  );
};
