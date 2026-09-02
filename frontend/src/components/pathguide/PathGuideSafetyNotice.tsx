import React from 'react';
import { ShieldCheck, AlertTriangle } from 'lucide-react';
import { Card } from '../ui/Card';

interface PathGuideSafetyNoticeProps {
  hasEmergencyTrigger?: boolean;
}

export const PathGuideSafetyNotice: React.FC<PathGuideSafetyNoticeProps> = ({
  hasEmergencyTrigger = false,
}) => {
  return (
    <div className="space-y-3">
      {/* Standard Educational & Non-Diagnostic Notice */}
      <Card className="p-3.5 bg-teal-50/50 border border-teal-200/60 rounded-2xl shadow-warm-xs">
        <div className="flex items-start gap-3">
          <div className="w-7 h-7 rounded-lg bg-teal-100 text-teal-900 flex items-center justify-center flex-shrink-0 mt-0.5">
            <ShieldCheck className="w-4 h-4 text-teal-900" />
          </div>
          <div className="space-y-0.5 text-xs">
            <h4 className="font-heading font-bold text-teal-900">
              Educational Care Companion Notice
            </h4>
            <p className="text-charcoal-600 leading-relaxed text-[11px]">
              PathGuide provides educational information and care-navigation support grounded in CleftPath verified resources. It does not diagnose medical conditions, calculate medical risk, prescribe treatment, or replace clinical advice from your multidisciplinary cleft healthcare team.
            </p>
          </div>
        </div>
      </Card>

      {/* Emergency Routing Alert if Triggered */}
      {hasEmergencyTrigger && (
        <Card className="p-3.5 bg-coral-50/90 border border-coral-200 rounded-2xl shadow-warm-xs animate-fade-in">
          <div className="flex items-start gap-3">
            <div className="w-7 h-7 rounded-lg bg-coral-100 text-coral-700 flex items-center justify-center flex-shrink-0 mt-0.5">
              <AlertTriangle className="w-4 h-4 text-coral-700" />
            </div>
            <div className="space-y-1 text-xs">
              <h4 className="font-heading font-bold text-coral-900">
                Urgent Medical Care Recommendation
              </h4>
              <p className="text-coral-800 leading-relaxed text-[11px]">
                If your child is experiencing acute symptoms such as severe breathing difficulty, choking during feeding, uncontrolled bleeding, or sudden high fever after surgery, please contact emergency medical services (911 or local emergency number) or your nearest hospital immediately.
              </p>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};
