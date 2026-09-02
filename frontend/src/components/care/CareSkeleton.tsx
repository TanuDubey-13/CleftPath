import React from 'react';
import { Card } from '../ui/Card';
import { Skeleton } from '../ui/Skeleton';

export const CareSkeleton: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* 3 Header Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {Array.from({ length: 3 }).map((_, i) => (
          <Card key={i} className="p-5 bg-white rounded-3xl border border-stone-200/80 space-y-3">
            <Skeleton variant="text" className="w-24 h-4" />
            <Skeleton variant="text" className="w-16 h-8" />
            <Skeleton variant="text" className="w-32 h-4" />
          </Card>
        ))}
      </div>

      {/* Main Container Skeleton */}
      <Card className="p-6 bg-white rounded-3xl border border-stone-200/80 space-y-4">
        <div className="flex justify-between">
          <Skeleton variant="rectangular" className="w-48 h-8 rounded-xl" />
          <Skeleton variant="rectangular" className="w-28 h-8 rounded-xl" />
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="p-4 bg-stone-50 rounded-2xl space-y-2">
              <Skeleton variant="text" className="w-32 h-5" />
              <Skeleton variant="text" className="w-20 h-6" />
              <Skeleton variant="text" className="w-full h-4" />
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};
