import React from 'react';
import { Download } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';

export const ProfilePage: React.FC = () => {
  return (
    <div className="space-y-6 max-w-4xl animate-fadeIn">
      <div>
        <h1 className="font-heading font-bold text-2xl text-teal-900">Patient & Family Profiles</h1>
        <p className="text-sm text-charcoal-600">
          Manage linked child records, anatomical cleft classifications, and data export.
        </p>
      </div>

      <Card className="space-y-4">
        <div className="flex justify-between items-start">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-teal-900 text-white flex items-center justify-center font-bold text-lg shadow-warm-sm">
              L
            </div>
            <div>
              <h3 className="font-heading font-bold text-lg text-charcoal-900">Baby Leo</h3>
              <p className="text-xs text-charcoal-600">Born March 15, 2026 • 4 Months Old</p>
            </div>
          </div>
          <Badge variant="coral" size="sm">Primary Profile</Badge>
        </div>

        <div className="p-4 bg-stone-50 rounded-xl space-y-2 text-xs">
          <div className="flex justify-between">
            <span className="font-semibold text-charcoal-600">Cleft Classification:</span>
            <span className="font-bold text-teal-900">Unilateral Left Complete Lip & Palate</span>
          </div>
          <div className="flex justify-between">
            <span className="font-semibold text-charcoal-600">Primary Hospital:</span>
            <span className="font-medium text-charcoal-900">Children's Craniofacial Center</span>
          </div>
          <div className="flex justify-between">
            <span className="font-semibold text-charcoal-600">Primary Surgeon:</span>
            <span className="font-medium text-charcoal-900">Dr. Robert Sterling, MD</span>
          </div>
        </div>

        <div className="flex gap-2">
          <Button variant="outline" size="sm">Edit Medical Baseline</Button>
          <Button variant="ghost" size="sm" leftIcon={<Download className="w-3.5 h-3.5" />}>
            Export Medical Portfolio (ZIP)
          </Button>
        </div>
      </Card>
    </div>
  );
};
