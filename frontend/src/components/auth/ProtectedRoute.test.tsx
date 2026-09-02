import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { describe, it, expect, vi } from 'vitest';
import { ProtectedRoute } from './ProtectedRoute';
import * as authHooks from '../../hooks/useAuth';

describe('ProtectedRoute Component', () => {
  it('shows loading spinner when authentication is in progress', () => {
    vi.spyOn(authHooks, 'useAuth').mockReturnValue({
      user: null,
      isLoading: true,
      isAuthenticated: false,
      patientCount: 0,
      login: vi.fn(),
      register: vi.fn(),
      logout: vi.fn(),
    });

    render(
      <MemoryRouter initialEntries={['/protected']}>
        <ProtectedRoute>
          <div>Protected Content</div>
        </ProtectedRoute>
      </MemoryRouter>
    );

    expect(screen.getByText(/Verifying your care journey session/i)).toBeInTheDocument();
  });

  it('redirects to /login when unauthenticated', () => {
    vi.spyOn(authHooks, 'useAuth').mockReturnValue({
      user: null,
      isLoading: false,
      isAuthenticated: false,
      patientCount: 0,
      login: vi.fn(),
      register: vi.fn(),
      logout: vi.fn(),
    });

    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <Routes>
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <div>Secret Dashboard</div>
              </ProtectedRoute>
            }
          />
          <Route path="/login" element={<div>Login Page Target</div>} />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText('Login Page Target')).toBeInTheDocument();
    expect(screen.queryByText('Secret Dashboard')).not.toBeInTheDocument();
  });

  it('renders child content when user is authenticated', () => {
    vi.spyOn(authHooks, 'useAuth').mockReturnValue({
      user: {
        id: 'usr_1',
        email: 'test@example.com',
        first_name: 'Sarah',
        last_name: 'Parent',
        role: 'caregiver',
        is_active: true,
        is_verified: true,
        created_at: '2026-09-02T12:00:00Z',
      },
      isLoading: false,
      isAuthenticated: true,
      patientCount: 1,
      login: vi.fn(),
      register: vi.fn(),
      logout: vi.fn(),
    });

    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <ProtectedRoute>
          <div>Authorized Dashboard View</div>
        </ProtectedRoute>
      </MemoryRouter>
    );

    expect(screen.getByText('Authorized Dashboard View')).toBeInTheDocument();
  });
});
