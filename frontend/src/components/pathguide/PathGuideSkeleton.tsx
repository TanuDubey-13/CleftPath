import React from 'react';
import { Skeleton } from '../ui/Skeleton';

export const PathGuideSkeleton: React.FC = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-6 h-[calc(100vh-10rem)]">
      {/* Sidebar Skeleton */}
      <div className="hidden md:block md:col-span-1 p-4 bg-white rounded-3xl border border-stone-200 space-y-3">
        <Skeleton variant="rectangular" className="w-full h-8 rounded-xl" />
        <Skeleton variant="text" className="w-full h-12 rounded-xl" />
        <Skeleton variant="text" className="w-full h-12 rounded-xl" />
        <Skeleton variant="text" className="w-full h-12 rounded-xl" />
      </div>

      {/* Main Conversation Skeleton */}
      <div className="md:col-span-3 p-6 bg-white rounded-3xl border border-stone-200 flex flex-col justify-between">
        <div className="space-y-4">
          <Skeleton variant="text" className="w-48 h-6" />
          <Skeleton variant="rectangular" className="w-3/4 h-20 rounded-2xl" />
          <Skeleton variant="rectangular" className="w-2/3 h-16 rounded-2xl ml-auto" />
          <Skeleton variant="rectangular" className="w-3/4 h-24 rounded-2xl" />
        </div>
        <Skeleton variant="rectangular" className="w-full h-12 rounded-2xl" />
      </div>
    </div>
  );
};
