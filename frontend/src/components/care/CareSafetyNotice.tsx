import React from 'react';
import { ShieldAlert } from 'lucide-react';
import { Card } from '../ui/Card';

export const CareSafetyNotice: React.FC = () => {
  return (
    <Card className="p-4 sm:p-5 bg-teal-50/50 border border-teal-200/60 rounded-3xl shadow-warm-xs">
      <div className="flex items-start gap-3.5">
        <div className="w-8 h-8 rounded-xl bg-teal-100 text-teal-900 flex items-center justify-center flex-shrink-0 mt-0.5">
          <ShieldAlert className="w-4 h-4 text-teal-900" />
        </div>
        <div className="space-y-1 text-xs">
          <h4 className="font-heading font-bold text-teal-900">
            Care & Tracking Safety Guidance
          </h4>
          <p className="text-charcoal-600 leading-relaxed">
            CleftPath provides tracking and educational support for daily routines. It does not diagnose medical conditions, calculate medical risk, or replace clinical advice from your multidisciplinary cleft healthcare team.
          </p>
        </div>
      </div>
    </Card>
  );
};
