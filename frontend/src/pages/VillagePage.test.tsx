import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { VillagePage } from './VillagePage';
import * as villageHooks from '../hooks/useVillage';
import * as authContext from '../context/AuthContext';

vi.mock('../hooks/useVillage');
vi.mock('../context/AuthContext');

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

describe('VillagePage Component', () => {
  const mockChannels = {
    items: [
      {
        id: 'ch-1',
        name: 'Surgery Prep & Recovery',
        slug: 'surgery-prep',
        description: 'Preparation tips',
        stage_id: 2,
        is_private: false,
        posts_count: 3,
      },
    ],
    total: 1,
    page: 1,
    page_size: 50,
    total_pages: 1,
    has_next: false,
    has_prev: false,
  };

  const mockPosts = {
    items: [
      {
        id: 'post-1',
        channel_id: 'ch-1',
        channel_name: 'Surgery Prep & Recovery',
        channel_slug: 'surgery-prep',
        user_id: 'user-1',
        author_alias: 'Parent Sarah',
        author_avatar_seed: 'avatar1',
        title: 'Tips for arm restraints during sleep?',
        content: 'Any tips on making sleep more comfortable with arm restraints?',
        status: 'published',
        is_flagged: false,
        upvotes_count: 4,
        comments_count: 1,
        has_reacted: false,
        created_at: '2026-09-02T10:00:00Z',
        updated_at: '2026-09-02T10:00:00Z',
      },
    ],
    total: 1,
    page: 1,
    page_size: 20,
    total_pages: 1,
    has_next: false,
    has_prev: false,
  };

  beforeEach(() => {
    vi.mocked(authContext.useAuth).mockReturnValue({
      user: { id: 'user-1', email: 'test@example.com', first_name: 'Sarah', last_name: 'Demo', role: 'caregiver' },
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      register: vi.fn(),
      logout: vi.fn(),
      refreshToken: vi.fn(),
    } as any);

    vi.mocked(villageHooks.useVillageChannels).mockReturnValue({
      data: mockChannels,
      isLoading: false,
      error: null,
    } as any);

    vi.mocked(villageHooks.useVillagePosts).mockReturnValue({
      data: mockPosts,
      isLoading: false,
      error: null,
    } as any);

    vi.mocked(villageHooks.useVillagePost).mockReturnValue({
      data: mockPosts.items[0],
      isLoading: false,
      error: null,
    } as any);

    vi.mocked(villageHooks.useVillageComments).mockReturnValue({
      data: { items: [], total: 0 },
      isLoading: false,
      error: null,
    } as any);

    vi.mocked(villageHooks.useCreateVillagePost).mockReturnValue({
      mutateAsync: vi.fn(),
      isPending: false,
    } as any);

    vi.mocked(villageHooks.useUpdateVillagePost).mockReturnValue({
      mutateAsync: vi.fn(),
      isPending: false,
    } as any);

    vi.mocked(villageHooks.useDeleteVillagePost).mockReturnValue({
      mutate: vi.fn(),
      isPending: false,
    } as any);

    vi.mocked(villageHooks.useCreateVillageComment).mockReturnValue({
      mutateAsync: vi.fn(),
      isPending: false,
    } as any);

    vi.mocked(villageHooks.useDeleteVillageComment).mockReturnValue({
      mutateAsync: vi.fn(),
      isPending: false,
    } as any);

    vi.mocked(villageHooks.useToggleVillageReaction).mockReturnValue({
      mutateAsync: vi.fn(),
      isPending: false,
    } as any);

    vi.mocked(villageHooks.useReportVillagePost).mockReturnValue({
      mutateAsync: vi.fn(),
      isPending: false,
    } as any);

    vi.mocked(villageHooks.useReportVillageComment).mockReturnValue({
      mutateAsync: vi.fn(),
      isPending: false,
    } as any);
  });

  it('renders page header, safety disclaimer, channels sidebar, and community feed', () => {
    renderWithProviders(<VillagePage />);

    expect(screen.getByText('The Village')).toBeInTheDocument();
    expect(screen.getByText(/Community Peer Support Notice/i)).toBeInTheDocument();
    expect(screen.getByText('Community Channels')).toBeInTheDocument();
    expect(screen.getByText('Surgery Prep & Recovery')).toBeInTheDocument();
    expect(screen.getByText('Tips for arm restraints during sleep?')).toBeInTheDocument();
  });

  it('opens post composer modal on "New Post" button click', () => {
    renderWithProviders(<VillagePage />);

    const newPostBtn = screen.getByRole('button', { name: /new post/i });
    fireEvent.click(newPostBtn);

    expect(screen.getByText('New Community Post')).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/e.g. Tips for keeping arm restraints comfortable/i)).toBeInTheDocument();
  });
});
