import React, { useState } from 'react';
import { Calendar, Plus, RefreshCw, Clock, History, CalendarX } from 'lucide-react';
import {
  useAppointments,
  useCancelAppointment,
  useCareTeamMembers,
  useCreateAppointment,
} from '../hooks/useAppointments';
import { Appointment, AppointmentCreateRequest, AppointmentStatus } from '../types';
import { AppointmentHeroCard } from '../components/appointments/AppointmentHeroCard';
import { AppointmentCard } from '../components/appointments/AppointmentCard';
import { AppointmentDetailModal } from '../components/appointments/AppointmentDetailModal';
import { AppointmentFormModal } from '../components/appointments/AppointmentFormModal';
import { AppointmentSkeleton } from '../components/appointments/AppointmentSkeleton';
import { Button } from '../components/ui/Button';
import { Alert } from '../components/ui/Alert';

export const AppointmentsPage: React.FC = () => {
  const [timeframe, setTimeframe] = useState<'upcoming' | 'past' | 'all'>('upcoming');
  const [statusFilter, setStatusFilter] = useState<AppointmentStatus | undefined>(undefined);
  const [page, setPage] = useState(1);
  const pageSize = 10;

  const [selectedAppointment, setSelectedAppointment] = useState<Appointment | null>(null);
  const [isFormOpen, setIsFormOpen] = useState(false);

  const {
    data: appointmentsData,
    isLoading,
    isError,
    error,
    refetch,
  } = useAppointments({
    timeframe,
    status: statusFilter,
    page,
    page_size: pageSize,
  });

  const { data: careTeamMembers } = useCareTeamMembers();
  const createAppointmentMutation = useCreateAppointment();
  const cancelAppointmentMutation = useCancelAppointment();

  const handleCreateAppointment = async (data: AppointmentCreateRequest) => {
    await createAppointmentMutation.mutateAsync(data);
  };

  const handleCancelAppointment = async (appointmentId: string) => {
    await cancelAppointmentMutation.mutateAsync(appointmentId);
  };

  const handleTimeframeChange = (newTimeframe: 'upcoming' | 'past' | 'all') => {
    setTimeframe(newTimeframe);
    setPage(1);
  };

  return (
    <div className="space-y-6 pb-12 animate-fade-in">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <div className="w-10 h-10 rounded-2xl bg-teal-50 text-teal-900 flex items-center justify-center shadow-warm-xs">
              <Calendar className="w-5 h-5 text-teal-900" />
            </div>
            <div>
              <h1 className="font-heading font-bold text-2xl text-teal-900">Appointments</h1>
              <p className="text-xs text-charcoal-600">
                Keep track of the people and visits supporting your journey.
              </p>
            </div>
          </div>
        </div>

        <Button
          variant="primary"
          size="md"
          onClick={() => setIsFormOpen(true)}
          leftIcon={<Plus className="w-4 h-4" />}
        >
          Schedule Care Visit
        </Button>
      </div>

      {/* Main Content Area */}
      {isLoading ? (
        <AppointmentSkeleton />
      ) : isError ? (
        <div className="max-w-2xl mx-auto py-12 space-y-4">
          <Alert variant="danger" title="Unable to Load Appointments">
            {error instanceof Error ? error.message : 'An error occurred while fetching your visits.'}
          </Alert>
          <div className="text-center">
            <Button
              variant="outline"
              size="md"
              onClick={() => refetch()}
              leftIcon={<RefreshCw className="w-4 h-4" />}
            >
              Retry Loading
            </Button>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Spotlight Next Upcoming Appointment (Shown on 'upcoming' or 'all' timeframe) */}
          {timeframe !== 'past' && appointmentsData?.next_appointment && (
            <AppointmentHeroCard
              appointment={appointmentsData.next_appointment}
              onSelect={(app) => setSelectedAppointment(app)}
            />
          )}

          {/* Timeframe Tabs & Status Filter Controls */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-3 sm:p-4 rounded-3xl border border-stone-200/80 shadow-warm-xs">
            {/* Tabs: Upcoming vs Past */}
            <div className="flex items-center gap-1.5" role="tablist">
              <button
                type="button"
                role="tab"
                aria-selected={timeframe === 'upcoming'}
                onClick={() => handleTimeframeChange('upcoming')}
                className={`px-4 py-2 rounded-2xl text-xs font-bold transition flex items-center gap-1.5 ${
                  timeframe === 'upcoming'
                    ? 'bg-teal-900 text-white shadow-warm-xs'
                    : 'bg-stone-50 text-charcoal-700 hover:bg-stone-100'
                }`}
              >
                <Clock className="w-3.5 h-3.5" />
                <span>Upcoming Visits</span>
                <span
                  className={`text-[10px] px-1.5 py-0.2 rounded-full font-bold ${
                    timeframe === 'upcoming'
                      ? 'bg-teal-800 text-teal-100'
                      : 'bg-stone-200 text-charcoal-600'
                  }`}
                >
                  {appointmentsData?.upcoming_count ?? 0}
                </span>
              </button>

              <button
                type="button"
                role="tab"
                aria-selected={timeframe === 'past'}
                onClick={() => handleTimeframeChange('past')}
                className={`px-4 py-2 rounded-2xl text-xs font-bold transition flex items-center gap-1.5 ${
                  timeframe === 'past'
                    ? 'bg-teal-900 text-white shadow-warm-xs'
                    : 'bg-stone-50 text-charcoal-700 hover:bg-stone-100'
                }`}
              >
                <History className="w-3.5 h-3.5" />
                <span>Past History</span>
                <span
                  className={`text-[10px] px-1.5 py-0.2 rounded-full font-bold ${
                    timeframe === 'past'
                      ? 'bg-teal-800 text-teal-100'
                      : 'bg-stone-200 text-charcoal-600'
                  }`}
                >
                  {appointmentsData?.past_count ?? 0}
                </span>
              </button>
            </div>

            {/* Status Filter Dropdown */}
            <div className="flex items-center gap-2">
              <label htmlFor="status-filter" className="text-xs font-semibold text-charcoal-600 whitespace-nowrap">
                Status:
              </label>
              <select
                id="status-filter"
                value={statusFilter || ''}
                onChange={(e) => setStatusFilter((e.target.value as AppointmentStatus) || undefined)}
                className="bg-stone-50 border border-stone-200 rounded-xl px-2.5 py-1.5 text-xs text-charcoal-800 focus:outline-none focus:ring-2 focus:ring-teal-700/20"
              >
                <option value="">All Statuses</option>
                <option value="scheduled">Scheduled</option>
                <option value="confirmed">Confirmed</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>
          </div>

          {/* Appointment Cards Grid */}
          {!appointmentsData || appointmentsData.items.length === 0 ? (
            <div className="bg-white rounded-3xl border border-stone-200 p-8 sm:p-12 text-center max-w-xl mx-auto space-y-4 shadow-warm-sm">
              <div className="w-14 h-14 rounded-2xl bg-teal-50 text-teal-900 mx-auto flex items-center justify-center">
                <CalendarX className="w-7 h-7" />
              </div>
              <h2 className="font-heading font-bold text-lg text-teal-900">
                {timeframe === 'upcoming'
                  ? 'No Upcoming Appointments'
                  : 'No Past Appointments Found'}
              </h2>
              <p className="text-xs text-charcoal-600 leading-relaxed">
                {timeframe === 'upcoming'
                  ? 'You have no visits scheduled on your roadmap right now. Click below to add an upcoming consultation.'
                  : 'No historical visits recorded under this filter.'}
              </p>
              {timeframe === 'upcoming' && (
                <Button variant="outline" size="sm" onClick={() => setIsFormOpen(true)}>
                  Schedule First Visit
                </Button>
              )}
            </div>
          ) : (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {appointmentsData.items.map((appointment) => (
                  <AppointmentCard
                    key={appointment.id}
                    appointment={appointment}
                    onSelect={(app) => setSelectedAppointment(app)}
                  />
                ))}
              </div>

              {/* Pagination Controls */}
              {appointmentsData.total_pages > 1 && (
                <div className="flex items-center justify-between pt-4 border-t border-stone-200/80">
                  <div className="text-xs text-charcoal-500 font-medium">
                    Page <strong className="text-charcoal-800">{appointmentsData.page}</strong> of{' '}
                    <strong className="text-charcoal-800">{appointmentsData.total_pages}</strong>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage((p) => Math.max(1, p - 1))}
                      disabled={!appointmentsData.has_prev}
                    >
                      Previous
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage((p) => p + 1)}
                      disabled={!appointmentsData.has_next}
                    >
                      Next
                    </Button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Appointment Detail Modal */}
      <AppointmentDetailModal
        appointment={selectedAppointment}
        isOpen={!!selectedAppointment}
        onClose={() => setSelectedAppointment(null)}
        onCancel={handleCancelAppointment}
      />

      {/* Schedule Visit Modal */}
      <AppointmentFormModal
        isOpen={isFormOpen}
        onClose={() => setIsFormOpen(false)}
        onSubmit={handleCreateAppointment}
        careTeamMembers={careTeamMembers}
      />
    </div>
  );
};
