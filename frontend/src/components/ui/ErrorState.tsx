import React from 'react';
import { clsx } from 'clsx';
import { AlertCircle, RotateCcw } from 'lucide-react';
import { Button } from './Button';

export interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
  className?: string;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Unable to Load Information',
  message = 'We encountered an unexpected error while connecting to the CleftPath service. Please try again.',
  onRetry,
  className,
}) => {
  return (
    <div
      className={clsx(
        'bg-white rounded-2xl border border-rose-200 p-8 sm:p-10 text-center max-w-lg mx-auto space-y-4 shadow-warm-sm',
        className
      )}
    >
      <div className="w-14 h-14 bg-rose-50 text-rose-600 rounded-2xl flex items-center justify-center mx-auto">
        <AlertCircle className="w-7 h-7" />
      </div>
      <div className="space-y-1.5">
        <h3 className="text-base sm:text-lg font-bold text-rose-950">{title}</h3>
        <p className="text-xs sm:text-sm text-charcoal-600 leading-relaxed">{message}</p>
      </div>
      {onRetry && (
        <div className="pt-2">
          <Button variant="outline" size="sm" onClick={onRetry} leftIcon={<RotateCcw className="w-3.5 h-3.5" />}>
            Retry Connection
          </Button>
        </div>
      )}
    </div>
  );
};
