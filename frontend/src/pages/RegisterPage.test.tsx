import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect } from 'vitest';
import { RegisterPage } from './RegisterPage';
import { AuthProvider } from '../context/AuthContext';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

describe('RegisterPage Component', () => {
  it('renders registration form elements and role selectors', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <MemoryRouter>
            <RegisterPage />
          </MemoryRouter>
        </AuthProvider>
      </QueryClientProvider>
    );

    expect(screen.getByText('Create Your CleftPath Profile')).toBeInTheDocument();
    expect(screen.getByText('Parent / Caregiver')).toBeInTheDocument();
    expect(screen.getByText('Adult Patient')).toBeInTheDocument();
    expect(screen.getByText('Cleft Specialist')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Sarah')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Jenkins')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /create account/i })).toBeInTheDocument();
  });
});
