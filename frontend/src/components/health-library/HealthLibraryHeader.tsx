import React from 'react';
import { BookOpen, ShieldAlert } from 'lucide-react';
import { Card } from '../ui/Card';

export const HealthLibraryHeader: React.FC = () => {
  return (
    <div className="space-y-4">
      {/* Title & Tagline Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <div className="w-10 h-10 rounded-2xl bg-teal-50 text-teal-900 flex items-center justify-center shadow-warm-xs">
              <BookOpen className="w-5 h-5 text-teal-900" />
            </div>
            <div>
              <h1 className="font-heading font-bold text-2xl text-teal-900">Health Library</h1>
              <p className="text-xs text-charcoal-600">
                Reliable information for every step of your journey.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Medical Safety & Educational Disclaimer */}
      <Card className="p-4 bg-gradient-to-r from-ivory-100/80 to-white border border-stone-200/80 shadow-warm-xs">
        <div className="flex items-start gap-3">
          <ShieldAlert className="w-4 h-4 text-coral-500 flex-shrink-0 mt-0.5" />
          <p className="text-xs text-charcoal-700 leading-relaxed">
            <strong className="font-semibold text-charcoal-900">Educational Resource Notice:</strong>{' '}
            All information in this library is grounded in ACPA-approved clinical standards and curated for parent education. This library provides general educational information and is not a substitute for advice from your healthcare team.
          </p>
        </div>
      </Card>
    </div>
  );
};
