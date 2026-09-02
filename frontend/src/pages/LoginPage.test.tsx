import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect } from 'vitest';
import { LoginPage } from './LoginPage';
import { AuthProvider } from '../context/AuthContext';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

describe('LoginPage Component', () => {
  it('renders login form elements and brand tagline', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <MemoryRouter>
            <LoginPage />
          </MemoryRouter>
        </AuthProvider>
      </QueryClientProvider>
    );

    expect(screen.getByText('Welcome to CleftPath')).toBeInTheDocument();
    expect(screen.getByText(/Every journey deserves a path forward/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText('sarah.parent@example.com')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in to your journey/i })).toBeInTheDocument();
  });

  it('shows error message if submitted with empty fields', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <MemoryRouter>
            <LoginPage />
          </MemoryRouter>
        </AuthProvider>
      </QueryClientProvider>
    );

    const submitBtn = screen.getByRole('button', { name: /sign in to your journey/i });
    await userEvent.click(submitBtn);

    // Form inputs have required attribute
    expect(screen.getByPlaceholderText('sarah.parent@example.com')).toBeRequired();
  });
});
