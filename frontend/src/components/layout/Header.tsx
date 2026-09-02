import React from 'react';
import { useLocation } from 'react-router-dom';
import { Bell, Sparkles, Activity, ShieldCheck, AlertTriangle } from 'lucide-react';
import { useHealth } from '../../hooks/useHealth';
import { Badge } from '../ui/Badge';

const ROUTE_TITLES: Record<string, { title: string; subtitle: string }> = {
  '/dashboard': { title: 'Family Care Dashboard', subtitle: 'Overview of Baby Leo’s journey and active milestones' },
  '/journey': { title: 'My Journey', subtitle: 'Longitudinal milestone roadmap from infancy to adulthood' },
  '/library': { title: 'Health Library', subtitle: 'Medically verified, evidence-grounded cleft resources' },
  '/appointments': { title: 'Appointments & Care Team', subtitle: 'Multidisciplinary specialist directory and visit prep' },
  '/care': { title: 'Baby & Parent Care', subtitle: 'Specialized feeding logs, growth tracking, and NAM care' },
  '/voice': { title: 'Voice Journey', subtitle: 'Speech practice companion and longitudinal articulation awareness' },
  '/pathguide': { title: 'PathGuide AI Assistant', subtitle: 'Evidence-grounded guidance, prep questions, and safety triage' },
  '/village': { title: 'The Village', subtitle: 'Safe, moderated community peer support for cleft families' },
  '/profile': { title: 'User & Patient Profile', subtitle: 'Manage children profiles, cleft classifications, and data export' },
  '/settings': { title: 'Account Settings', subtitle: 'Notification preferences, security credentials, and privacy controls' },
};

export const Header: React.FC = () => {
  const location = useLocation();
  const { data: health, isPending, isError } = useHealth();

  const currentMeta = ROUTE_TITLES[location.pathname] || {
    title: 'CleftPath',
    subtitle: 'Every journey deserves a path forward',
  };

  return (
    <header className="sticky top-0 z-20 bg-white/80 backdrop-blur-md border-b border-stone-200/80 px-4 sm:px-6 lg:px-8 py-3.5 transition-all">
      <div className="flex items-center justify-between gap-4">
        {/* Page Title Context */}
        <div className="min-w-0">
          <h2 className="font-heading font-bold text-lg sm:text-xl text-teal-900 truncate">
            {currentMeta.title}
          </h2>
          <p className="hidden sm:block text-xs text-charcoal-600 truncate mt-0.5">
            {currentMeta.subtitle}
          </p>
        </div>

        {/* Status Indicators & User Controls */}
        <div className="flex items-center gap-2.5 sm:gap-3 flex-shrink-0">
          {/* Backend API Health Status Indicator */}
          {isPending ? (
            <Badge variant="stone" size="sm" className="hidden sm:inline-flex animate-pulse">
              <Activity className="w-3 h-3 text-charcoal-400" /> Connecting API...
            </Badge>
          ) : isError || health?.status === 'degraded' ? (
            <Badge variant="rose" size="sm" className="hidden sm:inline-flex">
              <AlertTriangle className="w-3 h-3 text-rose-600" /> API Degraded
            </Badge>
          ) : (
            <Badge variant="sage" size="sm" className="hidden sm:inline-flex">
              <ShieldCheck className="w-3 h-3 text-sage-600" /> API v{health?.version || '0.1.0'}
            </Badge>
          )}

          {/* Quick PathGuide Launch Button */}
          <button
            onClick={() => window.location.assign('/pathguide')}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-teal-50 text-teal-900 hover:bg-teal-100 text-xs font-semibold border border-teal-200/60 transition shadow-sm"
            title="Open PathGuide AI"
          >
            <Sparkles className="w-3.5 h-3.5 text-coral-500" />
            <span className="hidden sm:inline">Ask PathGuide</span>
          </button>

          {/* Notification Bell */}
          <button className="p-2 rounded-xl text-charcoal-600 hover:text-teal-900 hover:bg-stone-100 transition relative">
            <Bell className="w-4.5 h-4.5" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-coral-500 ring-2 ring-white"></span>
          </button>

          {/* User Profile Avatar */}
          <div className="w-8 h-8 rounded-full bg-teal-900 text-white flex items-center justify-center font-bold text-xs shadow-warm-sm ring-2 ring-teal-900/10">
            SJ
          </div>
        </div>
      </div>
    </header>
  );
};
