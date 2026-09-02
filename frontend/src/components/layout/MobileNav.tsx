import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Compass, HeartPulse, Mic, Sparkles } from 'lucide-react';
import { clsx } from 'clsx';

const MOBILE_NAV = [
  { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
  { name: 'Journey', path: '/journey', icon: Compass },
  { name: 'Care', path: '/care', icon: HeartPulse },
  { name: 'Voice', path: '/voice', icon: Mic },
  { name: 'PathGuide', path: '/pathguide', icon: Sparkles },
];

export const MobileNav: React.FC = () => {
  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-white/95 backdrop-blur-md border-t border-stone-200/80 px-2 py-1.5 flex items-center justify-around shadow-warm-lg">
      {MOBILE_NAV.map((item) => {
        const Icon = item.icon;
        return (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              clsx(
                'flex flex-col items-center justify-center py-1 px-3 rounded-xl text-[10px] font-medium transition-all',
                isActive
                  ? 'text-teal-900 font-bold'
                  : 'text-charcoal-400 hover:text-teal-800'
              )
            }
          >
            {({ isActive }) => (
              <>
                <div
                  className={clsx(
                    'p-1 rounded-lg transition-colors',
                    isActive ? 'bg-teal-100 text-teal-900' : 'text-current'
                  )}
                >
                  <Icon className="w-5 h-5" />
                </div>
                <span className="mt-0.5">{item.name}</span>
              </>
            )}
          </NavLink>
        );
      })}
    </nav>
  );
};
