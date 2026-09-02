import React from 'react';
import { Card } from '../ui/Card';
import { Skeleton } from '../ui/Skeleton';

export const AppointmentSkeleton: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Hero Skeleton */}
      <Card className="p-6 rounded-3xl bg-teal-900/10 border border-teal-900/20 space-y-4">
        <Skeleton variant="text" className="w-28 h-4" />
        <Skeleton variant="text" className="w-3/4 h-8" />
        <div className="flex gap-4">
          <Skeleton variant="text" className="w-40 h-4" />
          <Skeleton variant="text" className="w-32 h-4" />
        </div>
      </Card>

      {/* Cards List Skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Card key={i} className="p-5 rounded-3xl bg-white border border-stone-200/80 space-y-3">
            <div className="flex justify-between">
              <Skeleton variant="rectangular" className="w-36 h-6 rounded-xl" />
              <Skeleton variant="rectangular" className="w-20 h-6 rounded-full" />
            </div>
            <Skeleton variant="text" className="w-2/3 h-5" />
            <Skeleton variant="text" className="w-1/2 h-4" />
            <div className="pt-3 border-t border-stone-100 flex justify-between">
              <Skeleton variant="text" className="w-24 h-4" />
              <Skeleton variant="text" className="w-16 h-4" />
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};
