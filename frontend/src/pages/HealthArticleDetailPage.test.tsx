import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, vi } from 'vitest';
import { HealthArticleDetailPage } from './HealthArticleDetailPage';
import * as healthHooks from '../hooks/useHealthLibrary';
import { HealthArticleDetail } from '../types';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

const mockArticleDetail: HealthArticleDetail = {
  id: 'a1',
  slug: 'cleft-feeding-guide',
  title: 'Specialized Cleft Feeding Guide',
  category: 'Feeding & Nutrition',
  stage_id: 1,
  stage_title: 'Stage 1: Infancy & Feeding',
  summary: 'Practical feeding advice for newborns with cleft palate.',
  content_markdown: `# Specialized Cleft Feeding

Babies with cleft palate need specialized bottles because they cannot generate negative suction.

### Key Feeding Systems
* **Dr. Brown's Specialty Feeder:** Uses a blue valve.
* **Pigeon Feeder:** Uses a Y-cut nipple.
`,
  author_source: 'ACPA Guidelines',
  clinical_verified_by: 'Feeding Specialist',
  reading_time_minutes: 3,
  created_at: '2026-09-02T10:00:00Z',
  updated_at: '2026-09-02T10:00:00Z',
};

describe('HealthArticleDetailPage Component', () => {
  it('renders loading state when article is fetching', () => {
    vi.spyOn(healthHooks, 'useHealthArticle').mockReturnValue({
      data: undefined,
      isLoading: true,
      isError: false,
      error: null,
      refetch: vi.fn(),
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={['/health-library/cleft-feeding-guide']}>
          <Routes>
            <Route path="/health-library/:articleId" element={<HealthArticleDetailPage />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    );

    // Skeleton elements render without error
    expect(document.querySelector('.animate-pulse')).toBeInTheDocument();
  });

  it('renders error state when article is not found', () => {
    vi.spyOn(healthHooks, 'useHealthArticle').mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
      error: new Error('Article not found'),
      refetch: vi.fn(),
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={['/health-library/non-existent']}>
          <Routes>
            <Route path="/health-library/:articleId" element={<HealthArticleDetailPage />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(screen.getByText('Article Not Found')).toBeInTheDocument();
    expect(screen.getByText('Back to Health Library')).toBeInTheDocument();
  });

  it('renders article markdown content, clinical source, and safety notice on success', () => {
    vi.spyOn(healthHooks, 'useHealthArticle').mockReturnValue({
      data: mockArticleDetail,
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    } as any);

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={['/health-library/cleft-feeding-guide']}>
          <Routes>
            <Route path="/health-library/:articleId" element={<HealthArticleDetailPage />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(screen.getAllByText('Specialized Cleft Feeding Guide').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('Source: ACPA Guidelines')).toBeInTheDocument();
    expect(screen.getByText('Verified by Feeding Specialist')).toBeInTheDocument();
    expect(screen.getByText('Key Feeding Systems')).toBeInTheDocument();
    expect(screen.getByText('Medical Safety & Care Team Notice')).toBeInTheDocument();
  });
});
