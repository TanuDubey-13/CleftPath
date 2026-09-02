import React from 'react';
import { Clock, Plus } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';

const STAGES = [
  { id: 0, name: 'Stage 0: Prenatal & Discovery', age: 'Prenatal', status: 'completed' },
  { id: 1, name: 'Stage 1: Infancy & Feeding Setup', age: '0–3 Months', status: 'completed' },
  { id: 2, name: 'Stage 2: Primary Lip Repair', age: '3–6 Months', status: 'active', active: true },
  { id: 3, name: 'Stage 3: Primary Palate Repair', age: '9–18 Months', status: 'upcoming' },
  { id: 4, name: 'Stage 4: Early Speech & Dental', age: '18m–5 Years', status: 'upcoming' },
  { id: 5, name: 'Stage 5: Bone Graft & Orthodontics', age: '6–10 Years', status: 'upcoming' },
  { id: 6, name: 'Stage 6: Adolescent & Orthognathic', age: '11–18 Years', status: 'upcoming' },
  { id: 7, name: 'Stage 7: Adulthood & Transition', age: '18+ Years', status: 'upcoming' },
];

export const JourneyPage: React.FC = () => {
  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header section */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-heading font-bold text-2xl text-teal-900">My Journey Roadmap</h1>
          <p className="text-sm text-charcoal-600">
            Longitudinal care pathway tailored for Unilateral Cleft Lip & Palate.
          </p>
        </div>
        <Button variant="primary" size="md" leftIcon={<Plus className="w-4 h-4" />}>
          Add Custom Milestone
        </Button>
      </div>

      {/* Stage Stepper Overview */}
      <Card className="p-6">
        <h3 className="font-heading font-bold text-base text-charcoal-900 mb-4">8 Care Stages</h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3">
          {STAGES.map((s) => (
            <div
              key={s.id}
              className={`p-3 rounded-xl border text-center transition ${
                s.active
                  ? 'border-coral-500 bg-coral-50/60 ring-2 ring-coral-500/20'
                  : s.status === 'completed'
                  ? 'border-sage-200 bg-sage-50/50'
                  : 'border-stone-200 bg-stone-50/50 opacity-70'
              }`}
            >
              <div className="text-[10px] font-bold uppercase tracking-wider text-charcoal-500">{s.age}</div>
              <div className="text-xs font-bold text-charcoal-900 mt-1 truncate">{s.name.split(':')[1]}</div>
              <div className="mt-2">
                {s.status === 'completed' && <Badge variant="sage" size="sm">✓ Done</Badge>}
                {s.active && <Badge variant="coral" size="sm">Active</Badge>}
                {s.status === 'upcoming' && <Badge variant="stone" size="sm">Upcoming</Badge>}
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Active Stage Milestones */}
      <div className="space-y-4">
        <h3 className="font-heading font-bold text-lg text-teal-900 flex items-center gap-2">
          <Clock className="w-5 h-5 text-coral-500" />
          <span>Stage 2 Milestones: Primary Lip Repair</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card variant="waypoint" className="space-y-3">
            <div className="flex justify-between items-start">
              <Badge variant="sage" size="sm">Completed</Badge>
              <span className="text-xs font-mono text-charcoal-500">Aug 20, 2026</span>
            </div>
            <h4 className="font-bold text-base text-charcoal-900">Surgical Consultation with Dr. Sterling</h4>
            <p className="text-xs text-charcoal-600 leading-relaxed">
              Reviewed pre-surgical markings, incision lines, and post-op arm restraint instructions.
            </p>
          </Card>

          <Card variant="waypoint" className="space-y-3 border-l-coral-500">
            <div className="flex justify-between items-start">
              <Badge variant="coral" size="sm">In Progress</Badge>
              <span className="text-xs font-mono text-coral-600 font-bold">Due in 4 Weeks</span>
            </div>
            <h4 className="font-bold text-base text-charcoal-900">Primary Lip Repair (Cheiloplasty)</h4>
            <p className="text-xs text-charcoal-600 leading-relaxed">
              Scheduled surgery date at Children’s Craniofacial Center. Fasting instructions will begin night prior.
            </p>
          </Card>
        </div>
      </div>
    </div>
  );
};
