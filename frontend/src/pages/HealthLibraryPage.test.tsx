import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, vi } from 'vitest';
import { HealthLibraryPage } from './HealthLibraryPage';
import * as healthHooks from '../hooks/useHealthLibrary';
import { PaginatedHealthArticles } from '../types';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

const mockArticlesData: PaginatedHealthArticles = {
  items: [
    {
      id: 'a1',
      slug: 'cleft-feeding-guide',
      title: 'Specialized Cleft Feeding Guide',
      category: 'Feeding & Nutrition',
      stage_id: 1,
      stage_title: 'Stage 1: Infancy & Feeding',
      summary: 'Practical feeding advice for newborns with cleft palate.',
      author_source: 'ACPA Guidelines',
      clinical_verified_by: 'Feeding Specialist',
      reading_time_minutes: 3,
      created_at: '2026-09-02T10:00:00Z',
      updated_at: '2026-09-02T10:00:00Z',
    },
    {
      id: 'a2',
      slug: 'lip-repair-prep',
      title: 'Preparing for Lip Repair Surgery',
      category: 'Surgery Prep & Recovery',
      stage_id: 2,
      stage_title: 'Stage 2: Primary Lip Repair',
      summary: 'Checklist and instructions for cheiloplasty day.',
      author_source: 'Craniofacial Surgical Board',
      clinical_verified_by: 'Dr. Sterling',
      reading_time_minutes: 5,
      created_at: '2026-09-02T10:00:00Z',
      updated_at: '2026-09-02T10:00:00Z',
    },
  ],
  total: 2,
  page: 1,
  page_size: 12,
  total_pages: 1,
  has_next: false,
  has_prev: false,
};

describe('HealthLibraryPage Component', () => {
  it('renders loading state when articles are fetching', () => {
    vi.spyOn(healthHooks, 'useHealthArticles').mockReturnValue({
      data: undefined,
      isLoading: true,
      isError: false,
      error: null,
      refetch: vi.fn(),
    } as any);

    vi.spyOn(healthHooks, 'useHealthCategories').mockReturnValue({
      data: [],
      isLoading: false,
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <HealthLibraryPage />
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(screen.getByText('Health Library')).toBeInTheDocument();
    expect(screen.getByText(/Educational Resource Notice/i)).toBeInTheDocument();
  });

  it('renders empty state when no articles match query', () => {
    vi.spyOn(healthHooks, 'useHealthArticles').mockReturnValue({
      data: { items: [], total: 0, page: 1, page_size: 12, total_pages: 0, has_next: false, has_prev: false },
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    } as any);

    vi.spyOn(healthHooks, 'useHealthCategories').mockReturnValue({
      data: [{ name: 'Feeding & Nutrition', article_count: 0 }],
      isLoading: false,
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <HealthLibraryPage />
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(screen.getByText('No Educational Articles Found')).toBeInTheDocument();
  });

  it('renders error state when API fails with retry option', () => {
    const mockRefetch = vi.fn();
    vi.spyOn(healthHooks, 'useHealthArticles').mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
      error: new Error('Network error loading library'),
      refetch: mockRefetch,
    } as any);

    vi.spyOn(healthHooks, 'useHealthCategories').mockReturnValue({
      data: [],
      isLoading: false,
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <HealthLibraryPage />
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(screen.getByText('Unable to Load Health Articles')).toBeInTheDocument();
    expect(screen.getByText('Network error loading library')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /retry loading/i })).toBeInTheDocument();
  });

  it('renders article cards, search input, and category filters', async () => {
    vi.spyOn(healthHooks, 'useHealthArticles').mockReturnValue({
      data: mockArticlesData,
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    } as any);

    vi.spyOn(healthHooks, 'useHealthCategories').mockReturnValue({
      data: [
        { name: 'Feeding & Nutrition', article_count: 1 },
        { name: 'Surgery Prep & Recovery', article_count: 1 },
      ],
      isLoading: false,
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <HealthLibraryPage />
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(screen.getByText('Specialized Cleft Feeding Guide')).toBeInTheDocument();
    expect(screen.getByText('Preparing for Lip Repair Surgery')).toBeInTheDocument();
    expect(screen.getByText('All Topics')).toBeInTheDocument();

    const searchInput = screen.getByPlaceholderText(/search articles/i);
    await userEvent.type(searchInput, 'Feeding');
    expect(searchInput).toHaveValue('Feeding');
  });
});
