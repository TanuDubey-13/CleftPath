import React from 'react';
import { Skeleton } from '../ui/Skeleton';

export const VillageSkeleton: React.FC = () => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
      {/* Sidebar Skeleton */}
      <div className="lg:col-span-1 p-4 bg-white rounded-3xl border border-stone-200 space-y-3">
        <Skeleton variant="text" className="w-32 h-6" />
        <Skeleton variant="rectangular" className="w-full h-10 rounded-2xl" />
        <Skeleton variant="rectangular" className="w-full h-10 rounded-2xl" />
        <Skeleton variant="rectangular" className="w-full h-10 rounded-2xl" />
        <Skeleton variant="rectangular" className="w-full h-10 rounded-2xl" />
      </div>

      {/* Posts Feed Skeleton */}
      <div className="lg:col-span-3 space-y-4">
        <Skeleton variant="rectangular" className="w-full h-36 rounded-3xl" />
        <Skeleton variant="rectangular" className="w-full h-36 rounded-3xl" />
        <Skeleton variant="rectangular" className="w-full h-36 rounded-3xl" />
      </div>
    </div>
  );
};
