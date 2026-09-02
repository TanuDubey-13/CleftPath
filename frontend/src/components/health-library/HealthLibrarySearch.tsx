import React from 'react';
import { Search, X } from 'lucide-react';

interface HealthLibrarySearchProps {
  value: string;
  onChange: (value: string) => void;
  onClear: () => void;
  placeholder?: string;
}

export const HealthLibrarySearch: React.FC<HealthLibrarySearchProps> = ({
  value,
  onChange,
  onClear,
  placeholder = 'Search articles, surgical guides, feeding tips, speech milestones...',
}) => {
  return (
    <div className="relative w-full">
      <label htmlFor="health-library-search" className="sr-only">
        Search Health Library
      </label>
      <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-charcoal-400">
        <Search className="w-4 h-4" />
      </div>
      <input
        id="health-library-search"
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full bg-white border border-stone-200/90 rounded-2xl pl-10 pr-10 py-2.5 text-xs text-charcoal-900 placeholder:text-charcoal-400 shadow-warm-xs focus:outline-none focus:ring-2 focus:ring-teal-700/20 focus:border-teal-900 transition"
      />
      {value && (
        <button
          type="button"
          onClick={onClear}
          aria-label="Clear search input"
          className="absolute inset-y-0 right-0 pr-3 flex items-center text-charcoal-400 hover:text-charcoal-700 transition"
        >
          <X className="w-4 h-4" />
        </button>
      )}
    </div>
  );
};
