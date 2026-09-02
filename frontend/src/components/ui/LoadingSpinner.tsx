import React from 'react';
import { clsx } from 'clsx';
import { Loader2 } from 'lucide-react';

export interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  label?: string;
  className?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  label,
  className,
}) => {
  const sizeMap = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-10 h-10',
  };

  return (
    <div className={clsx('flex flex-col items-center justify-center gap-3 p-6 text-teal-900', className)}>
      <Loader2 className={clsx('animate-spin text-teal-900', sizeMap[size])} />
      {label && <p className="text-xs sm:text-sm font-medium text-charcoal-600">{label}</p>}
    </div>
  );
};
