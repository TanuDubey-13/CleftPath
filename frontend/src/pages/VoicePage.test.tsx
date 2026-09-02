import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { VoicePage } from './VoicePage';
import * as voiceHooks from '../hooks/useVoice';

vi.mock('../hooks/useVoice');

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });

const renderWithProviders = (ui: React.ReactElement) => {
  const queryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>{ui}</BrowserRouter>
    </QueryClientProvider>
  );
};

describe('VoicePage Component', () => {
  const mockOverview = {
    patient_id: 'patient-123',
    total_sessions_count: 5,
    total_practice_minutes: 15,
    unique_exercises_practiced: 2,
    last_session: {
      id: 'session-1',
      patient_id: 'patient-123',
      exercise_id: 'ex-1',
      recorded_at: '2026-09-02T10:00:00Z',
      audio_s3_key: 'local_session',
      duration_seconds: 60,
      repetition_count: 3,
      dsp_features_json: {},
      parent_notes: 'Great practice session.',
      created_at: '2026-09-02T10:00:00Z',
      exercise: {
        id: 'ex-1',
        title: 'Bilabial Sound Exploration',
        target_phonemes: ['p', 'b', 'm'],
        prompt_text: 'Practice /pa/ and /ba/',
        instructions: 'Model lip closure',
        difficulty_level: 'beginner',
        created_at: '2026-09-02T10:00:00Z',
      },
    },
    practice_guidance_notes: [
      'Short daily practice sessions support natural vocal play.',
    ],
  };

  const mockExercises = {
    items: [
      {
        id: 'ex-1',
        title: 'Bilabial Sound Exploration',
        target_phonemes: ['p', 'b', 'm'],
        stage_id: 2,
        prompt_text: 'Practice /pa/ and /ba/',
        instructions: 'Model lip closure',
        difficulty_level: 'beginner',
        created_at: '2026-09-02T10:00:00Z',
      },
    ],
    total: 1,
    page: 1,
    page_size: 20,
    total_pages: 1,
    has_next: false,
    has_prev: false,
  };

  const mockSessions = {
    items: [
      {
        id: 'session-1',
        patient_id: 'patient-123',
        exercise_id: 'ex-1',
        recorded_at: '2026-09-02T10:00:00Z',
        audio_s3_key: 'local_session',
        duration_seconds: 60,
        repetition_count: 3,
        dsp_features_json: {},
        parent_notes: 'Great practice session.',
        created_at: '2026-09-02T10:00:00Z',
        exercise: mockExercises.items[0],
      },
    ],
    total: 1,
    page: 1,
    page_size: 20,
    total_pages: 1,
    has_next: false,
    has_prev: false,
    total_practice_minutes: 15,
    total_sessions_count: 1,
  };

  beforeEach(() => {
    vi.mocked(voiceHooks.useVoiceOverview).mockReturnValue({
      data: mockOverview,
      isLoading: false,
      error: null,
    } as any);

    vi.mocked(voiceHooks.useVoiceExercises).mockReturnValue({
      data: mockExercises,
      isLoading: false,
      error: null,
    } as any);

    vi.mocked(voiceHooks.useVoiceSessions).mockReturnValue({
      data: mockSessions,
      isLoading: false,
      error: null,
    } as any);

    vi.mocked(voiceHooks.useCreateVoiceSession).mockReturnValue({
      mutateAsync: vi.fn(),
      isPending: false,
    } as any);

    vi.mocked(voiceHooks.useUpdateVoiceSession).mockReturnValue({
      mutateAsync: vi.fn(),
      isPending: false,
    } as any);

    vi.mocked(voiceHooks.useDeleteVoiceSession).mockReturnValue({
      mutateAsync: vi.fn(),
      isPending: false,
    } as any);
  });

  it('renders page header, safety notice, and summary metrics', () => {
    renderWithProviders(<VoicePage />);

    expect(screen.getByRole('heading', { name: /voice journey/i, level: 1 })).toBeInTheDocument();
    expect(screen.getByText(/Speech Practice & Educational Notice/i)).toBeInTheDocument();
    expect(screen.getByText('5')).toBeInTheDocument(); // total sessions
    expect(screen.getByText('15')).toBeInTheDocument(); // total minutes
  });

  it('renders exercises in the Exercise Library tab', () => {
    renderWithProviders(<VoicePage />);

    expect(screen.getByText('Bilabial Sound Exploration')).toBeInTheDocument();
  });

  it('switches between tabs cleanly', () => {
    renderWithProviders(<VoicePage />);

    // Click Practice Journal Tab
    fireEvent.click(screen.getByRole('button', { name: /practice journal/i }));
    expect(screen.getByText(/practice session history/i)).toBeInTheDocument();

    // Click Activity & Guidance Tab
    fireEvent.click(screen.getByRole('button', { name: /activity & guidance/i }));
    expect(screen.getByText(/home speech play guidance/i)).toBeInTheDocument();
  });
});
