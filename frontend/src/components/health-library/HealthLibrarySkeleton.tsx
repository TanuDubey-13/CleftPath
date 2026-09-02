import React from 'react';
import { Card } from '../ui/Card';
import { Skeleton } from '../ui/Skeleton';

export const HealthLibrarySkeleton: React.FC<{ count?: number }> = ({ count = 6 }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
      {Array.from({ length: count }).map((_, i) => (
        <Card key={i} className="p-5 sm:p-6 space-y-4 rounded-3xl bg-white border border-stone-200/80">
          <div className="flex gap-2">
            <Skeleton variant="rectangular" className="w-20 h-5 rounded-full" />
            <Skeleton variant="rectangular" className="w-24 h-5 rounded-full" />
          </div>
          <Skeleton variant="text" className="w-5/6 h-6" />
          <Skeleton variant="text" className="w-full h-4" />
          <Skeleton variant="text" className="w-3/4 h-4" />
          <div className="pt-3 border-t border-stone-100 flex justify-between">
            <Skeleton variant="text" className="w-16 h-3.5" />
            <Skeleton variant="text" className="w-12 h-3.5" />
          </div>
        </Card>
      ))}
    </div>
  );
};
