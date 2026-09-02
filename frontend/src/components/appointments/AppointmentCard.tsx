import React from 'react';
import { Calendar, Clock, MapPin, ChevronRight, HelpCircle } from 'lucide-react';
import { Appointment } from '../../types';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';

interface AppointmentCardProps {
  appointment: Appointment;
  onSelect: (appointment: Appointment) => void;
}

export const AppointmentCard: React.FC<AppointmentCardProps> = ({
  appointment,
  onSelect,
}) => {
  const dateObj = new Date(appointment.scheduled_at);
  const formattedDate = dateObj.toLocaleDateString(undefined, {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
  const formattedTime = dateObj.toLocaleTimeString(undefined, {
    hour: 'numeric',
    minute: '2-digit',
  });

  const getStatusBadgeVariant = (status: string): 'teal' | 'sage' | 'coral' | 'stone' => {
    switch (status) {
      case 'completed':
        return 'sage';
      case 'confirmed':
        return 'teal';
      case 'scheduled':
        return 'coral';
      default:
        return 'stone';
    }
  };

  return (
    <Card
      onClick={() => onSelect(appointment)}
      className="p-5 bg-white border border-stone-200/80 rounded-3xl hover:border-teal-700/40 hover:shadow-warm-sm transition-all cursor-pointer group flex flex-col justify-between gap-4"
    >
      <div className="space-y-3">
        {/* Top Header: Date/Time Pill & Status Badge */}
        <div className="flex items-center justify-between gap-2 flex-wrap">
          <div className="flex items-center gap-2 text-xs font-bold text-teal-900 bg-teal-50 px-3 py-1 rounded-xl border border-teal-100/60">
            <Calendar className="w-3.5 h-3.5 text-coral-500" />
            <span>{formattedDate}</span>
            <span className="text-charcoal-400">•</span>
            <Clock className="w-3.5 h-3.5 text-teal-900" />
            <span>{formattedTime}</span>
          </div>

          <Badge variant={getStatusBadgeVariant(appointment.status)} size="sm">
            {appointment.status.replace(/_/g, ' ').toUpperCase()}
          </Badge>
        </div>

        {/* Specialist & Specialty */}
        <div>
          <h4 className="font-heading font-bold text-base text-charcoal-900 group-hover:text-teal-900 transition">
            {appointment.specialist_name}
          </h4>
          <p className="text-xs font-medium text-charcoal-600">
            {appointment.specialty}
          </p>
        </div>

        {/* Location if provided */}
        {appointment.clinic_location && (
          <div className="flex items-center gap-1.5 text-xs text-charcoal-500">
            <MapPin className="w-3.5 h-3.5 text-coral-500 flex-shrink-0" />
            <span className="truncate">{appointment.clinic_location}</span>
          </div>
        )}
      </div>

      {/* Footer Meta & Action Trigger */}
      <div className="pt-3 border-t border-stone-100 flex items-center justify-between text-xs text-charcoal-500">
        <div className="flex items-center gap-2">
          <span>{appointment.duration_minutes} min visit</span>
          {appointment.prep_questions && appointment.prep_questions.length > 0 && (
            <span className="flex items-center gap-1 font-semibold text-coral-600">
              <HelpCircle className="w-3.5 h-3.5" />
              <span>{appointment.prep_questions.length} questions</span>
            </span>
          )}
        </div>

        <div className="flex items-center gap-1 font-bold text-teal-900 group-hover:text-coral-600 transition">
          <span>Details</span>
          <ChevronRight className="w-4 h-4 group-hover:translate-x-0.5 transition" />
        </div>
      </div>
    </Card>
  );
};
