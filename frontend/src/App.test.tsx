import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect } from 'vitest';
import { AppShell } from './components/layout/AppShell';
import { AuthProvider } from './context/AuthContext';

describe('App Layout & Navigation', () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });

  it('renders the brand title and navigation links in AppShell', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <MemoryRouter initialEntries={['/dashboard']}>
            <AppShell />
          </MemoryRouter>
        </AuthProvider>
      </QueryClientProvider>
    );

    // Brand and Tagline
    const brandElements = screen.getAllByText('CleftPath');
    expect(brandElements.length).toBeGreaterThanOrEqual(1);

    const taglineElements = screen.getAllByText(/Every journey deserves a path forward/i);
    expect(taglineElements.length).toBeGreaterThanOrEqual(1);

    // Navigation links (Desktop + Mobile)
    expect(screen.getAllByText('Dashboard').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/Journey/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('Health Library')).toBeInTheDocument();
    expect(screen.getByText('Appointments')).toBeInTheDocument();
    expect(screen.getByText('Baby & Parent Care')).toBeInTheDocument();
    expect(screen.getByText('Voice Journey')).toBeInTheDocument();
    expect(screen.getAllByText(/PathGuide/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('The Village')).toBeInTheDocument();
  });
});
