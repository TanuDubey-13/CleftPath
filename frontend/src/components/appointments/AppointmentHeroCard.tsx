import React from 'react';
import { Calendar, Clock, MapPin, ChevronRight, HelpCircle } from 'lucide-react';
import { Appointment } from '../../types';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';

interface AppointmentHeroCardProps {
  appointment: Appointment;
  onSelect: (appointment: Appointment) => void;
}

export const AppointmentHeroCard: React.FC<AppointmentHeroCardProps> = ({
  appointment,
  onSelect,
}) => {
  const dateObj = new Date(appointment.scheduled_at);
  const formattedDate = dateObj.toLocaleDateString(undefined, {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  });
  const formattedTime = dateObj.toLocaleTimeString(undefined, {
    hour: 'numeric',
    minute: '2-digit',
  });

  return (
    <Card className="p-6 sm:p-7 bg-gradient-to-br from-teal-900 via-teal-900 to-teal-950 text-white rounded-3xl shadow-warm-md border border-teal-800/60 relative overflow-hidden">
      {/* Background Decorative Accents */}
      <div className="absolute right-0 top-0 translate-x-12 -translate-y-12 w-64 h-64 bg-teal-800/30 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute right-8 bottom-0 translate-y-8 w-40 h-40 bg-coral-500/10 rounded-full blur-2xl pointer-events-none" />

      <div className="relative z-10 space-y-5">
        {/* Banner Label */}
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-coral-400 animate-pulse" />
            <span className="text-xs font-bold uppercase tracking-wider text-teal-200">
              Next Care Visit
            </span>
          </div>

          <Badge variant="coral" size="sm">
            {appointment.status.toUpperCase()}
          </Badge>
        </div>

        {/* Main Content Grid */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-5">
          <div className="space-y-2 min-w-0">
            <h3 className="font-heading font-bold text-xl sm:text-2xl text-white truncate">
              {appointment.specialist_name}
            </h3>
            <p className="text-xs font-semibold text-teal-200">
              {appointment.specialty}
            </p>

            <div className="flex flex-wrap items-center gap-4 text-xs text-teal-100 pt-1">
              <div className="flex items-center gap-1.5">
                <Calendar className="w-4 h-4 text-coral-400 flex-shrink-0" />
                <span>{formattedDate}</span>
              </div>
              <div className="flex items-center gap-1.5">
                <Clock className="w-4 h-4 text-teal-300 flex-shrink-0" />
                <span>{formattedTime} ({appointment.duration_minutes} min)</span>
              </div>
            </div>

            {appointment.clinic_location && (
              <div className="flex items-center gap-1.5 text-xs text-teal-200/90 pt-0.5">
                <MapPin className="w-3.5 h-3.5 text-coral-400 flex-shrink-0" />
                <span className="truncate">{appointment.clinic_location}</span>
              </div>
            )}
          </div>

          {/* Action Trigger */}
          <div className="flex items-center gap-3 pt-2 md:pt-0">
            {appointment.prep_questions && appointment.prep_questions.length > 0 && (
              <div className="hidden sm:flex items-center gap-1 text-[11px] font-semibold bg-teal-800/80 px-3 py-1.5 rounded-xl border border-teal-700/50 text-teal-100">
                <HelpCircle className="w-3.5 h-3.5 text-coral-400" />
                <span>{appointment.prep_questions.length} Prep Questions</span>
              </div>
            )}

            <button
              type="button"
              onClick={() => onSelect(appointment)}
              className="px-4 py-2.5 bg-coral-500 hover:bg-coral-600 text-white font-semibold text-xs rounded-2xl transition flex items-center gap-1.5 shadow-sm hover:shadow"
            >
              <span>View Visit Details</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </Card>
  );
};
