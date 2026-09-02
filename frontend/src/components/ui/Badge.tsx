import React from 'react';
import { clsx } from 'clsx';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'teal' | 'sage' | 'coral' | 'stone' | 'rose';
  size?: 'sm' | 'md';
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  className,
  variant = 'teal',
  size = 'md',
  ...props
}) => {
  const baseStyles =
    'inline-flex items-center gap-1.5 font-semibold tracking-wide rounded-full';

  const variantStyles = {
    teal: 'bg-teal-100 text-teal-900 border border-teal-200/50',
    sage: 'bg-sage-100 text-sage-800 border border-sage-200/50',
    coral: 'bg-coral-100 text-coral-800 border border-coral-200/50',
    stone: 'bg-stone-100 text-charcoal-800 border border-stone-200',
    rose: 'bg-rose-100 text-rose-800 border border-rose-200',
  };

  const sizeStyles = {
    sm: 'px-2.5 py-0.5 text-[11px]',
    md: 'px-3 py-1 text-xs',
  };

  return (
    <span className={clsx(baseStyles, variantStyles[variant], sizeStyles[size], className)} {...props}>
      {children}
    </span>
  );
};
