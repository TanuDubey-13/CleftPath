import { createBrowserRouter, Navigate } from 'react-router-dom';
import { ProtectedRoute } from '../components/auth/ProtectedRoute';
import { AppShell } from '../components/layout/AppShell';
import { AppointmentsPage } from '../pages/AppointmentsPage';
import { BabyCarePage } from '../pages/BabyCarePage';
import { DashboardPage } from '../pages/DashboardPage';
import { JourneyPage } from '../pages/JourneyPage';
import { LibraryPage } from '../pages/LibraryPage';
import { LoginPage } from '../pages/LoginPage';
import { NotFoundPage } from '../pages/NotFoundPage';
import { PathGuidePage } from '../pages/PathGuidePage';
import { ProfilePage } from '../pages/ProfilePage';
import { RegisterPage } from '../pages/RegisterPage';
import { SettingsPage } from '../pages/SettingsPage';
import { VillagePage } from '../pages/VillagePage';
import { VoicePage } from '../pages/VoicePage';

export const router = createBrowserRouter([
  // Public Authentication Routes
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/register',
    element: <RegisterPage />,
  },
  // Protected Application Routes
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <AppShell />
      </ProtectedRoute>
    ),
    errorElement: <NotFoundPage />,
    children: [
      { index: true, element: <Navigate to="/dashboard" replace /> },
      { path: 'dashboard', element: <DashboardPage /> },
      { path: 'journey', element: <JourneyPage /> },
      { path: 'library', element: <LibraryPage /> },
      { path: 'appointments', element: <AppointmentsPage /> },
      { path: 'care', element: <BabyCarePage /> },
      { path: 'voice', element: <VoicePage /> },
      { path: 'pathguide', element: <PathGuidePage /> },
      { path: 'village', element: <VillagePage /> },
      { path: 'profile', element: <ProfilePage /> },
      { path: 'settings', element: <SettingsPage /> },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
]);
