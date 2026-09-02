import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { CarePage } from './CarePage';
import * as careHooks from '../hooks/useCare';
import { CareOverview } from '../types';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

const mockOverview: CareOverview = {
  patient_id: 'pt_1',
  today_feeding_volume_ml: 480,
  today_feeding_count: 4,
  today_nam_hours: 22,
  guidance_notes: [
    'Hold baby in an upright or semi-upright (45° to 60°) position during feeding.',
    'Burp frequently every 15-30 ml to reduce swallowed air and reflux.',
  ],
  last_feeding: {
    id: 'feed_1',
    patient_id: 'pt_1',
    logged_at: '2026-09-02T08:30:00Z',
    bottle_type: 'dr_browns_specialty',
    volume_ml: 120,
    duration_minutes: 25,
    burping_breaks: 2,
    reflux_severity: 'none',
    created_at: '2026-09-02T08:30:00Z',
  },
  latest_growth: {
    id: 'growth_1',
    patient_id: 'pt_1',
    recorded_at: '2026-09-01',
    weight_kg: 4.65,
    height_cm: 55.0,
    head_circumference_cm: 38.0,
    created_at: '2026-09-01T10:00:00Z',
  },
  latest_nam_log: {
    id: 'nam_1',
    patient_id: 'pt_1',
    logged_at: '2026-09-02T07:00:00Z',
    hours_worn: 22,
    appliance_cleaned: true,
    tape_changed: true,
    skin_condition: 'normal',
    created_at: '2026-09-02T07:00:00Z',
  },
};

describe('CarePage Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders loading state when overview is fetching', () => {
    vi.spyOn(careHooks, 'useCareOverview').mockReturnValue({
      data: undefined,
      isLoading: true,
      isError: false,
      error: null,
      refetch: vi.fn(),
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <CarePage />
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(screen.getByText('Baby & Parent Care')).toBeInTheDocument();
    expect(screen.getByText(/Care & Tracking Safety Guidance/i)).toBeInTheDocument();
  });

  it('renders error state with retry button', () => {
    const mockRefetch = vi.fn();
    vi.spyOn(careHooks, 'useCareOverview').mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
      error: new Error('Failed to load care metrics'),
      refetch: mockRefetch,
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <CarePage />
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(screen.getByText('Unable to Load Care Overview')).toBeInTheDocument();
    expect(screen.getByText('Failed to load care metrics')).toBeInTheDocument();
  });

  it('renders overview stats, guidance tips, and tabs on successful load', () => {
    vi.spyOn(careHooks, 'useCareOverview').mockReturnValue({
      data: mockOverview,
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <CarePage />
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(screen.getByText(/Today's Feeding/i)).toBeInTheDocument();
    expect(screen.getByText('480')).toBeInTheDocument();
    expect(screen.getByText('4.65')).toBeInTheDocument();
    expect(screen.getByText('22')).toBeInTheDocument();
    expect(screen.getByText(/Daily Overview/i)).toBeInTheDocument();
    expect(screen.getByText(/Feeding Tracker/i)).toBeInTheDocument();
    expect(screen.getByText(/Growth Records/i)).toBeInTheDocument();
    expect(screen.getByText(/NAM & Taping/i)).toBeInTheDocument();
    expect(screen.getByText(/Hold baby in an upright or semi-upright/i)).toBeInTheDocument();
  });

  it('switches tabs and opens feeding tracker', async () => {
    vi.spyOn(careHooks, 'useCareOverview').mockReturnValue({
      data: mockOverview,
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    } as any);

    vi.spyOn(careHooks, 'useFeedingLogs').mockReturnValue({
      data: {
        items: [mockOverview.last_feeding!],
        total: 1,
        page: 1,
        page_size: 8,
        total_pages: 1,
        has_next: false,
        has_prev: false,
        today_total_volume_ml: 480,
        today_total_feeds: 4,
      },
      isLoading: false,
      isError: false,
      error: null,
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <CarePage />
        </MemoryRouter>
      </QueryClientProvider>
    );

    const feedingTab = screen.getByRole('tab', { name: /feeding tracker/i });
    await userEvent.click(feedingTab);

    expect(screen.getByText('Feeding Sessions (1)')).toBeInTheDocument();
  });

  it('opens quick add feeding modal from header action', async () => {
    vi.spyOn(careHooks, 'useCareOverview').mockReturnValue({
      data: mockOverview,
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <CarePage />
        </MemoryRouter>
      </QueryClientProvider>
    );

    const logFeedBtn = screen.getByRole('button', { name: /^log feed$/i });
    await userEvent.click(logFeedBtn);

    expect(screen.getByText('Log Feeding Session')).toBeInTheDocument();
    expect(screen.getByText('Volume Fed (ml) *')).toBeInTheDocument();
  });
});
