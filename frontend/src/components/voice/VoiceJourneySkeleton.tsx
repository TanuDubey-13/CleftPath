import React from 'react';
import { Skeleton } from '../ui/Skeleton';

export const VoiceJourneySkeleton: React.FC = () => {
  return (
    <div className="space-y-6 animate-pulse">
      {/* Header Cards Skeleton */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="p-5 bg-white rounded-3xl border border-stone-200/80 space-y-3">
            <Skeleton variant="text" className="w-24 h-4" />
            <Skeleton variant="rectangular" className="w-32 h-8 rounded-xl" />
            <Skeleton variant="text" className="w-40 h-3" />
          </div>
        ))}
      </div>

      {/* Safety Notice Skeleton */}
      <div className="p-5 bg-white rounded-3xl border border-stone-200/80 space-y-2">
        <Skeleton variant="text" className="w-48 h-5" />
        <Skeleton variant="text" className="w-full h-4" />
        <Skeleton variant="text" className="w-3/4 h-4" />
      </div>

      {/* Grid of Exercises Skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="p-5 bg-white rounded-3xl border border-stone-200/80 space-y-3">
            <Skeleton variant="text" className="w-3/4 h-6" />
            <Skeleton variant="rectangular" className="w-full h-16 rounded-2xl" />
            <Skeleton variant="text" className="w-full h-4" />
            <div className="flex justify-between pt-2">
              <Skeleton variant="text" className="w-16 h-4" />
              <Skeleton variant="rectangular" className="w-24 h-8 rounded-xl" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
