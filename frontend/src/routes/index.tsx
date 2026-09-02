import { createBrowserRouter, Navigate } from 'react-router-dom';
import { AppShell } from '../components/layout/AppShell';
import { DashboardPage } from '../pages/DashboardPage';
import { JourneyPage } from '../pages/JourneyPage';
import { LibraryPage } from '../pages/LibraryPage';
import { AppointmentsPage } from '../pages/AppointmentsPage';
import { BabyCarePage } from '../pages/BabyCarePage';
import { VoicePage } from '../pages/VoicePage';
import { PathGuidePage } from '../pages/PathGuidePage';
import { VillagePage } from '../pages/VillagePage';
import { ProfilePage } from '../pages/ProfilePage';
import { SettingsPage } from '../pages/SettingsPage';
import { NotFoundPage } from '../pages/NotFoundPage';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppShell />,
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
