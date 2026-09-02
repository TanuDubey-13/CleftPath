import React from 'react';
import { Calendar, Clock, MapPin, Plus, Sparkles } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';

export const AppointmentsPage: React.FC = () => {
  return (
    <div className="space-y-6 animate-fadeIn">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-heading font-bold text-2xl text-teal-900">Appointments & Care Team</h1>
          <p className="text-sm text-charcoal-600">
            Manage multidisciplinary cleft team visits, specialist contacts, and question prep-sheets.
          </p>
        </div>
        <Button variant="primary" size="md" leftIcon={<Plus className="w-4 h-4" />}>
          Schedule Visit
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Upcoming Appointments List */}
        <div className="lg:col-span-2 space-y-4">
          <h3 className="font-heading font-bold text-lg text-teal-900">Upcoming Appointments</h3>
          
          <Card className="space-y-4 border-l-4 border-l-coral-500">
            <div className="flex justify-between items-start">
              <div>
                <Badge variant="coral" size="sm">Pre-Op Consultation</Badge>
                <h4 className="font-bold text-lg text-charcoal-900 mt-1">Dr. Robert Sterling, MD</h4>
                <p className="text-xs text-charcoal-600 font-medium">Plastic & Reconstructive Cleft Surgeon</p>
              </div>
              <Button variant="secondary" size="sm" leftIcon={<Sparkles className="w-3.5 h-3.5" />}>
                Question Prep
              </Button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-charcoal-700 bg-ivory-50 p-3 rounded-xl">
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-teal-900" />
                <span>Monday, Oct 14, 2026</span>
              </div>
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-teal-900" />
                <span>10:00 AM – 10:45 AM</span>
              </div>
              <div className="flex items-center gap-2 sm:col-span-2">
                <MapPin className="w-4 h-4 text-teal-900" />
                <span>Children’s Craniofacial Center, Suite 402</span>
              </div>
            </div>
          </Card>
        </div>

        {/* Multidisciplinary Care Team Sidebar */}
        <div className="space-y-4">
          <h3 className="font-heading font-bold text-lg text-teal-900">Cleft Team Specialists</h3>
          <Card className="space-y-3">
            <div className="p-2.5 bg-stone-50 rounded-xl">
              <p className="font-bold text-xs text-charcoal-900">Dr. Karen Vance, CCC-SLP</p>
              <p className="text-[11px] text-charcoal-600">Speech-Language Pathologist</p>
            </div>
            <div className="p-2.5 bg-stone-50 rounded-xl">
              <p className="font-bold text-xs text-charcoal-900">Dr. Nathan Chen, DDS</p>
              <p className="text-[11px] text-charcoal-600">Pediatric Craniofacial Orthodontist</p>
            </div>
            <div className="p-2.5 bg-stone-50 rounded-xl">
              <p className="font-bold text-xs text-charcoal-900">Dr. Elena Rostova, MD</p>
              <p className="text-[11px] text-charcoal-600">Pediatric Otolaryngologist (ENT)</p>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};
