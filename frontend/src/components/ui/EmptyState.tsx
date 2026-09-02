import React from 'react';
import { clsx } from 'clsx';
import { FolderOpen } from 'lucide-react';
import { Button } from './Button';

export interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  description,
  actionLabel,
  onAction,
  className,
}) => {
  return (
    <div
      className={clsx(
        'bg-white rounded-2xl border border-stone-200/80 p-8 sm:p-12 text-center max-w-lg mx-auto space-y-4 shadow-warm-sm',
        className
      )}
    >
      <div className="w-14 h-14 sm:w-16 sm:h-16 bg-teal-50 text-teal-900 rounded-2xl flex items-center justify-center mx-auto shadow-inner">
        {icon || <FolderOpen className="w-7 h-7 sm:w-8 sm:h-8" />}
      </div>
      <div className="space-y-1.5">
        <h3 className="text-base sm:text-lg font-bold text-charcoal-900">{title}</h3>
        <p className="text-xs sm:text-sm text-charcoal-600 leading-relaxed">{description}</p>
      </div>
      {actionLabel && onAction && (
        <div className="pt-2">
          <Button variant="primary" size="md" onClick={onAction}>
            {actionLabel}
          </Button>
        </div>
      )}
    </div>
  );
};
