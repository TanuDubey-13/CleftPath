import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, vi } from 'vitest';
import { JourneyPage } from './JourneyPage';
import * as journeyHooks from '../hooks/useJourney';
import { JourneyOverview } from '../types';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

const mockJourneyData: JourneyOverview = {
  patient: {
    id: 'pt_1',
    display_name: 'Baby Leo',
    date_of_birth: '2026-03-15',
    gender: 'male',
    cleft_lip: 'unilateral_left_complete',
    cleft_palate: 'hard_and_soft_complete',
    cleft_alveolus: 'involved_left',
  },
  stages: [
    {
      id: 1,
      stage_number: 1,
      title: 'Prenatal & Discovery',
      age_range_label: 'Diagnosis to Birth',
      description: 'Prenatal diagnosis and feeding guidance',
      color_hex: '#0F4C5C',
      status: 'completed',
      total_milestones: 1,
      completed_milestones: 1,
      progress_percentage: 100,
      milestones: [
        {
          id: 'm_1',
          patient_id: 'pt_1',
          stage_id: 1,
          title: 'Initial Team Consultation',
          description: 'Meet the cleft team specialists',
          target_age_months: 0,
          status: 'completed',
          is_custom: false,
          notes_count: 1,
          notes: [
            {
              id: 'n_1',
              milestone_id: 'm_1',
              user_id: 'u_1',
              note_text: 'Met with feeding team at 32 weeks',
              created_at: '2026-09-02T10:00:00Z',
              author_name: 'Sarah Jenkins',
            },
          ],
        },
      ],
    },
    {
      id: 2,
      stage_number: 2,
      title: 'Newborn & Feeding',
      age_range_label: '0 to 3 Months',
      description: 'Specialized feeder adjustments and NAM setup',
      color_hex: '#0F4C5C',
      status: 'in_progress',
      total_milestones: 1,
      completed_milestones: 0,
      progress_percentage: 0,
      milestones: [
        {
          id: 'm_2',
          patient_id: 'pt_1',
          stage_id: 2,
          title: 'Primary Lip Repair Surgery',
          description: 'Cheiloplasty surgical repair',
          target_age_months: 3,
          status: 'in_progress',
          is_custom: false,
          notes_count: 0,
          notes: [],
        },
      ],
    },
  ],
  summary: {
    total_milestones: 2,
    completed_milestones: 1,
    in_progress_milestones: 1,
    upcoming_milestones: 0,
    overall_progress_percentage: 50.0,
    current_stage_number: 2,
    current_stage_title: 'Newborn & Feeding',
  },
};

describe('JourneyPage Component', () => {
  it('renders loading state when journey is fetching', () => {
    vi.spyOn(journeyHooks, 'useJourney').mockReturnValue({
      data: undefined,
      isLoading: true,
      isError: false,
      error: null,
      refetch: vi.fn(),
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <JourneyPage />
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(screen.getByText(/Loading your longitudinal roadmap/i)).toBeInTheDocument();
  });

  it('renders empty state when no patient is associated', () => {
    vi.spyOn(journeyHooks, 'useJourney').mockReturnValue({
      data: { patient: null, stages: [], summary: { total_milestones: 0, completed_milestones: 0, in_progress_milestones: 0, upcoming_milestones: 0, overall_progress_percentage: 0 } },
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <JourneyPage />
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(screen.getByText('No Care Journey Profile Found')).toBeInTheDocument();
  });

  it('renders error state when API fails with retry option', () => {
    const mockRefetch = vi.fn();
    vi.spyOn(journeyHooks, 'useJourney').mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
      error: new Error('Network error'),
      refetch: mockRefetch,
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <JourneyPage />
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(screen.getByText('Unable to Load Care Journey')).toBeInTheDocument();
    expect(screen.getByText('Network error')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /retry loading/i })).toBeInTheDocument();
  });

  it('renders journey stages and milestones on successful data load', () => {
    vi.spyOn(journeyHooks, 'useJourney').mockReturnValue({
      data: mockJourneyData,
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <JourneyPage />
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(screen.getByText('Baby Leo’s Care Journey')).toBeInTheDocument();
    expect(screen.getAllByText('50%').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('Stage 1: Prenatal & Discovery')).toBeInTheDocument();
    expect(screen.getByText('Initial Team Consultation')).toBeInTheDocument();
    expect(screen.getAllByText('Stage 2: Newborn & Feeding').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('Primary Lip Repair Surgery')).toBeInTheDocument();
  });

  it('opens milestone detail modal when a milestone is clicked', async () => {
    vi.spyOn(journeyHooks, 'useJourney').mockReturnValue({
      data: mockJourneyData,
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <JourneyPage />
        </MemoryRouter>
      </QueryClientProvider>
    );

    const milestoneCard = screen.getByText('Initial Team Consultation');
    await userEvent.click(milestoneCard);

    // Modal opens with detailed description & notes
    expect(screen.getByText('Update Milestone Status')).toBeInTheDocument();
    expect(screen.getByText('Family Memories & Clinical Notes (1)')).toBeInTheDocument();
    expect(screen.getByText('Met with feeding team at 32 weeks')).toBeInTheDocument();
  });
});
