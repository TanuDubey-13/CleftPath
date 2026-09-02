import React from 'react';
import { clsx } from 'clsx';

export interface ProgressBarProps {
  progress: number; // 0 - 100
  variant?: 'teal' | 'sage' | 'coral';
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  className?: string;
}

const VARIANT_MAP = {
  teal: 'bg-teal-900',
  sage: 'bg-sage-600',
  coral: 'bg-coral-500',
};

const SIZE_MAP = {
  sm: 'h-1.5',
  md: 'h-2.5',
  lg: 'h-4',
};

export const ProgressBar: React.FC<ProgressBarProps> = ({
  progress,
  variant = 'teal',
  size = 'md',
  showLabel = false,
  className,
}) => {
  const clampedProgress = Math.min(Math.max(progress, 0), 100);

  return (
    <div className={clsx('w-full space-y-1', className)}>
      <div className={clsx('w-full bg-stone-200/80 rounded-full overflow-hidden', SIZE_MAP[size])}>
        <div
          className={clsx('transition-all duration-500 rounded-full', VARIANT_MAP[variant], SIZE_MAP[size])}
          style={{ width: `${clampedProgress}%` }}
          role="progressbar"
          aria-valuenow={clampedProgress}
          aria-valuemin={0}
          aria-valuemax={100}
        />
      </div>
      {showLabel && (
        <div className="flex justify-between text-[11px] font-bold text-charcoal-500">
          <span>Progress</span>
          <span>{clampedProgress}%</span>
        </div>
      )}
    </div>
  );
};
