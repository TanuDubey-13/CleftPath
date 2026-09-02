import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, it, expect } from 'vitest';
import { HealthArticleCard } from './HealthArticleCard';
import { HealthArticleCard as HealthArticleCardType } from '../../types';

const mockArticle: HealthArticleCardType = {
  id: 'a_123',
  slug: 'understanding-specialized-feeders',
  title: 'Understanding Specialized Cleft Feeders',
  category: 'Feeding & Nutrition',
  stage_id: 1,
  stage_title: 'Stage 1: Infancy & Feeding',
  summary: 'A clinical guide comparing Dr. Brown and Haberman valves.',
  author_source: 'ACPA Guidelines',
  clinical_verified_by: 'Pediatric Cleft Council',
  reading_time_minutes: 4,
  created_at: '2026-09-02T10:00:00Z',
  updated_at: '2026-09-02T10:00:00Z',
};

describe('HealthArticleCard Component', () => {
  it('renders article card with category, title, summary, and reading time', () => {
    render(
      <MemoryRouter>
        <HealthArticleCard article={mockArticle} />
      </MemoryRouter>
    );

    expect(screen.getByText('Feeding & Nutrition')).toBeInTheDocument();
    expect(screen.getByText('Stage 1: Infancy & Feeding')).toBeInTheDocument();
    expect(screen.getByText('Understanding Specialized Cleft Feeders')).toBeInTheDocument();
    expect(screen.getByText(/A clinical guide comparing Dr. Brown/i)).toBeInTheDocument();
    expect(screen.getByText('4 min read')).toBeInTheDocument();
    expect(screen.getByText('Verified')).toBeInTheDocument();
  });

  it('links to the article detail slug route', () => {
    render(
      <MemoryRouter>
        <HealthArticleCard article={mockArticle} />
      </MemoryRouter>
    );

    const link = screen.getByRole('link');
    expect(link).toHaveAttribute('href', '/health-library/understanding-specialized-feeders');
  });
});
