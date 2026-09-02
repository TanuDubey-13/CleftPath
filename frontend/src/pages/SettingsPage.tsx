import React from 'react';
import { Bell, Shield } from 'lucide-react';
import { Card } from '../components/ui/Card';

export const SettingsPage: React.FC = () => {
  return (
    <div className="space-y-6 max-w-4xl animate-fadeIn">
      <div>
        <h1 className="font-heading font-bold text-2xl text-teal-900">Account & Privacy Settings</h1>
        <p className="text-sm text-charcoal-600">
          Manage security credentials, notification frequencies, and AI consent preferences.
        </p>
      </div>

      <div className="space-y-4">
        <Card className="space-y-3">
          <div className="flex items-center gap-2 pb-2 border-b border-stone-100">
            <Bell className="w-4 h-4 text-teal-900" />
            <h3 className="font-bold text-base text-charcoal-900">Reminder Preferences</h3>
          </div>
          <p className="text-xs text-charcoal-600">
            Receive automated SMS and email reminders for upcoming surgical consults and fasting schedules.
          </p>
        </Card>

        <Card className="space-y-3">
          <div className="flex items-center gap-2 pb-2 border-b border-stone-100">
            <Shield className="w-4 h-4 text-teal-900" />
            <h3 className="font-bold text-base text-charcoal-900">Privacy & Consent Records</h3>
          </div>
          <p className="text-xs text-charcoal-600">
            Your data is strictly isolated per account and never shared for public AI foundation model training.
          </p>
        </Card>
      </div>
    </div>
  );
};
