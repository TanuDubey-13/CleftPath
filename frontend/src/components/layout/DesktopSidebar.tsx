import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Compass,
  BookOpen,
  Calendar,
  HeartPulse,
  Mic,
  Sparkles,
  Users,
  User,
  Settings,
  PhoneCall,
  ChevronDown,
} from 'lucide-react';
import { clsx } from 'clsx';
import { Badge } from '../ui/Badge';

const NAV_ITEMS = [
  { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
  { name: 'My Journey', path: '/journey', icon: Compass, badge: 'Stage 2' },
  { name: 'Health Library', path: '/library', icon: BookOpen },
  { name: 'Appointments', path: '/appointments', icon: Calendar },
  { name: 'Baby & Parent Care', path: '/care', icon: HeartPulse },
  { name: 'Voice Journey', path: '/voice', icon: Mic },
  { name: 'PathGuide', path: '/pathguide', icon: Sparkles, highlight: true },
  { name: 'The Village', path: '/village', icon: Users },
];

const SECONDARY_NAV = [
  { name: 'Profile', path: '/profile', icon: User },
  { name: 'Settings', path: '/settings', icon: Settings },
];

export const DesktopSidebar: React.FC = () => {
  return (
    <aside className="hidden md:flex flex-col w-64 lg:w-72 bg-white border-r border-stone-200/80 min-h-screen sticky top-0 z-30 select-none">
      {/* Brand Header */}
      <div className="p-5 lg:p-6 border-b border-stone-100">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-teal-900 text-white flex items-center justify-center shadow-warm-sm">
            <svg className="w-6 h-6 text-sage-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M4 19C8 19 10 11 14 11C18 11 19 15 22 15" />
              <circle cx="22" cy="15" r="2" fill="#E07A5F" />
              <circle cx="4" cy="19" r="2" fill="#FAF7F2" />
            </svg>
          </div>
          <div>
            <h1 className="font-heading font-bold text-lg text-teal-900 leading-tight">CleftPath</h1>
            <p className="text-[11px] text-charcoal-600 font-medium tracking-tight truncate">
              Every journey deserves a path forward
            </p>
          </div>
        </div>
      </div>

      {/* Active Patient Switcher Card */}
      <div className="px-4 py-3 border-b border-stone-100 bg-ivory-50/50">
        <div className="flex items-center justify-between p-2.5 rounded-xl bg-white border border-stone-200/70 shadow-sm cursor-pointer hover:border-teal-700/40 transition">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-8 h-8 rounded-full bg-teal-100 text-teal-900 flex items-center justify-center font-bold text-xs">
              L
            </div>
            <div className="min-w-0">
              <p className="text-xs font-bold text-charcoal-900 truncate">Baby Leo</p>
              <p className="text-[10px] text-charcoal-600 truncate">4 months • Unilateral Cleft Lip/Palate</p>
            </div>
          </div>
          <ChevronDown className="w-4 h-4 text-charcoal-400 flex-shrink-0" />
        </div>
      </div>

      {/* Main Navigation Items */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <div className="px-3 pb-1 text-[11px] font-bold text-charcoal-400 uppercase tracking-wider">
          Journey Navigation
        </div>
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                clsx(
                  'flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all group',
                  isActive
                    ? 'bg-teal-900 text-white shadow-warm-sm font-semibold'
                    : item.highlight
                    ? 'text-teal-900 bg-teal-50/70 hover:bg-teal-100/80'
                    : 'text-charcoal-600 hover:text-teal-900 hover:bg-teal-50/50'
                )
              }
            >
              {({ isActive }) => (
                <>
                  <div className="flex items-center gap-3">
                    <Icon
                      className={clsx(
                        'w-4.5 h-4.5 transition-colors',
                        isActive
                          ? 'text-coral-400'
                          : item.highlight
                          ? 'text-teal-900'
                          : 'text-charcoal-400 group-hover:text-teal-900'
                      )}
                    />
                    <span>{item.name}</span>
                  </div>
                  {item.badge && (
                    <Badge variant={isActive ? 'coral' : 'sage'} size="sm">
                      {item.badge}
                    </Badge>
                  )}
                </>
              )}
            </NavLink>
          );
        })}

        <div className="pt-4 px-3 pb-1 text-[11px] font-bold text-charcoal-400 uppercase tracking-wider">
          Account & Safety
        </div>
        {SECONDARY_NAV.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                clsx(
                  'flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all group',
                  isActive
                    ? 'bg-teal-900 text-white shadow-warm-sm font-semibold'
                    : 'text-charcoal-600 hover:text-teal-900 hover:bg-teal-50/50'
                )
              }
            >
              <Icon className="w-4.5 h-4.5 text-charcoal-400 group-hover:text-teal-900" />
              <span>{item.name}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Emergency Hotline Trigger */}
      <div className="p-3 border-t border-stone-100">
        <a
          href="tel:911"
          className="flex items-center justify-center gap-2 w-full py-2.5 px-3 rounded-xl bg-rose-50 text-rose-800 border border-rose-200/80 text-xs font-bold hover:bg-rose-100 transition"
        >
          <PhoneCall className="w-3.5 h-3.5 text-rose-600" />
          <span>Emergency Triage Line</span>
        </a>
      </div>
    </aside>
  );
};
