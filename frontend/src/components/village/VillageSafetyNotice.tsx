import React from 'react';
import { Users } from 'lucide-react';
import { Card } from '../ui/Card';

export const VillageSafetyNotice: React.FC = () => {
  return (
    <Card className="p-3.5 bg-ivory-50/80 border border-stone-200/80 rounded-2xl shadow-warm-xs">
      <div className="flex items-start gap-3">
        <div className="w-7 h-7 rounded-lg bg-teal-100 text-teal-900 flex items-center justify-center flex-shrink-0 mt-0.5">
          <Users className="w-4 h-4 text-teal-900" />
        </div>
        <div className="space-y-0.5 text-xs">
          <h4 className="font-heading font-bold text-teal-900">
            Community Peer Support Notice
          </h4>
          <p className="text-charcoal-600 leading-relaxed text-[11px]">
            The Village is a supportive space to share lived experiences and practical daily care tips. <strong>Personal experiences are not professional medical advice.</strong> Please consult your multidisciplinary cleft care team or seek emergency medical care for any clinical, surgical, or medication concerns.
          </p>
        </div>
      </div>
    </Card>
  );
};
