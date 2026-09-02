import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, vi } from 'vitest';
import { AppointmentsPage } from './AppointmentsPage';
import * as appointmentHooks from '../hooks/useAppointments';
import { PaginatedAppointments } from '../types';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

const mockAppointmentsData: PaginatedAppointments = {
  items: [
    {
      id: 'app_1',
      patient_id: 'pt_1',
      specialist_name: 'Dr. Robert Sterling',
      specialty: 'Cleft Surgeon',
      clinic_location: 'Suite 402',
      scheduled_at: '2026-10-14T10:00:00Z',
      duration_minutes: 45,
      prep_questions: ['Fasting instructions?'],
      summary_notes: 'Bring specialized feeder.',
      status: 'scheduled',
      created_at: '2026-09-02T10:00:00Z',
      updated_at: '2026-09-02T10:00:00Z',
    },
  ],
  total: 1,
  page: 1,
  page_size: 10,
  total_pages: 1,
  has_next: false,
  has_prev: false,
  upcoming_count: 1,
  past_count: 0,
  next_appointment: {
    id: 'app_1',
    patient_id: 'pt_1',
    specialist_name: 'Dr. Robert Sterling',
    specialty: 'Cleft Surgeon',
    clinic_location: 'Suite 402',
    scheduled_at: '2026-10-14T10:00:00Z',
    duration_minutes: 45,
    prep_questions: ['Fasting instructions?'],
    summary_notes: 'Bring specialized feeder.',
    status: 'scheduled',
    created_at: '2026-09-02T10:00:00Z',
    updated_at: '2026-09-02T10:00:00Z',
  },
};

describe('AppointmentsPage Component', () => {
  it('renders loading skeleton when appointments are fetching', () => {
    vi.spyOn(appointmentHooks, 'useAppointments').mockReturnValue({
      data: undefined,
      isLoading: true,
      isError: false,
      error: null,
      refetch: vi.fn(),
    } as any);

    vi.spyOn(appointmentHooks, 'useCareTeamMembers').mockReturnValue({
      data: [],
      isLoading: false,
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <AppointmentsPage />
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(screen.getByText('Appointments')).toBeInTheDocument();
    expect(screen.getByText(/Keep track of the people and visits/i)).toBeInTheDocument();
  });

  it('renders empty state when no upcoming appointments exist', () => {
    vi.spyOn(appointmentHooks, 'useAppointments').mockReturnValue({
      data: { items: [], total: 0, page: 1, page_size: 10, total_pages: 0, has_next: false, has_prev: false, upcoming_count: 0, past_count: 0, next_appointment: null },
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    } as any);

    vi.spyOn(appointmentHooks, 'useCareTeamMembers').mockReturnValue({
      data: [],
      isLoading: false,
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <AppointmentsPage />
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(screen.getByText('No Upcoming Appointments')).toBeInTheDocument();
  });

  it('renders error state with friendly retry button', () => {
    const mockRefetch = vi.fn();
    vi.spyOn(appointmentHooks, 'useAppointments').mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
      error: new Error('Network error loading appointments'),
      refetch: mockRefetch,
    } as any);

    vi.spyOn(appointmentHooks, 'useCareTeamMembers').mockReturnValue({
      data: [],
      isLoading: false,
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <AppointmentsPage />
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(screen.getByText('Unable to Load Appointments')).toBeInTheDocument();
    expect(screen.getByText('Network error loading appointments')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /retry loading/i })).toBeInTheDocument();
  });

  it('renders hero spotlight and appointment cards on successful load', async () => {
    vi.spyOn(appointmentHooks, 'useAppointments').mockReturnValue({
      data: mockAppointmentsData,
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    } as any);

    vi.spyOn(appointmentHooks, 'useCareTeamMembers').mockReturnValue({
      data: [],
      isLoading: false,
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <AppointmentsPage />
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(screen.getByText(/Next Care Visit/i)).toBeInTheDocument();
    expect(screen.getAllByText('Dr. Robert Sterling').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('Upcoming Visits')).toBeInTheDocument();
    expect(screen.getByText('Past History')).toBeInTheDocument();
  });

  it('opens scheduling modal when Schedule Care Visit is clicked', async () => {
    vi.spyOn(appointmentHooks, 'useAppointments').mockReturnValue({
      data: mockAppointmentsData,
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    } as any);

    vi.spyOn(appointmentHooks, 'useCareTeamMembers').mockReturnValue({
      data: [],
      isLoading: false,
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <AppointmentsPage />
        </MemoryRouter>
      </QueryClientProvider>
    );

    const scheduleBtn = screen.getByRole('button', { name: /schedule care visit/i });
    await userEvent.click(scheduleBtn);

    expect(screen.getByText('Schedule New Care Visit')).toBeInTheDocument();
    expect(screen.getByText('Specialist Name *')).toBeInTheDocument();
  });
});
