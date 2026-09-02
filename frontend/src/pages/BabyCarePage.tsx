import React from 'react';
import { Plus, Scale } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';

export const BabyCarePage: React.FC = () => {
  return (
    <div className="space-y-6 animate-fadeIn">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-heading font-bold text-2xl text-teal-900">Baby & Parent Care</h1>
          <p className="text-sm text-charcoal-600">
            High-precision tracking for specialized feeding methods, WHO growth curves, and NAM taping care.
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="md" leftIcon={<Scale className="w-4 h-4" />}>
            Record Weight
          </Button>
          <Button variant="primary" size="md" leftIcon={<Plus className="w-4 h-4" />}>
            Log Feeding Session
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-xs font-bold uppercase text-charcoal-500">Today's Total Intake</span>
            <Badge variant="sage" size="sm">Normal</Badge>
          </div>
          <p className="font-mono font-bold text-2xl text-teal-900">680 ml</p>
          <p className="text-xs text-charcoal-600">Target: 650–750 ml based on 6.2 kg weight</p>
        </Card>

        <Card className="space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-xs font-bold uppercase text-charcoal-500">Active Feeding Device</span>
            <Badge variant="teal" size="sm">Specialty</Badge>
          </div>
          <p className="font-bold text-base text-charcoal-900">Dr. Brown’s Specialty Feeder</p>
          <p className="text-xs text-charcoal-600">Blue unidirectional valve, Level 2 teat</p>
        </Card>

        <Card className="space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-xs font-bold uppercase text-charcoal-500">Weight Velocity</span>
            <Badge variant="sage" size="sm">50th %ile</Badge>
          </div>
          <p className="font-mono font-bold text-2xl text-sage-700">6.20 kg</p>
          <p className="text-xs text-charcoal-600">+180g gained over past 7 days</p>
        </Card>
      </div>

      {/* NAM / Taping Section */}
      <Card className="p-6">
        <h3 className="font-heading font-bold text-base text-teal-900 mb-2">
          Nasoalveolar Molding (NAM) & Lip Taping Log
        </h3>
        <p className="text-xs text-charcoal-600 mb-4">
          Tracking appliance hygiene, skin barrier integrity, and daily wear duration.
        </p>
        <div className="p-4 bg-ivory-50 rounded-xl border border-stone-200/80 flex items-center justify-between">
          <div>
            <p className="text-xs font-bold text-charcoal-900">Appliance Status: Cleaned & Worn (22h today)</p>
            <p className="text-[11px] text-charcoal-600">Skin inspection: No redness on cheek taping site</p>
          </div>
          <Button variant="outline" size="sm">Update NAM Log</Button>
        </div>
      </Card>
    </div>
  );
};
