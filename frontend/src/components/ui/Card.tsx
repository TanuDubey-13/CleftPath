import React from 'react';
import { clsx } from 'clsx';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'interactive' | 'waypoint' | 'subtle';
  stageColorHex?: string;
}

export const Card: React.FC<CardProps> = ({
  children,
  className,
  variant = 'default',
  stageColorHex,
  ...props
}) => {
  const baseStyles = 'bg-white rounded-2xl border border-stone-200/80 p-6 transition-all duration-200';

  const variantStyles = {
    default: 'shadow-warm-sm',
    interactive: 'shadow-warm-sm hover:shadow-warm-md hover:border-teal-800/30 cursor-pointer',
    waypoint: 'border-l-4 border-l-coral-500 rounded-l-md rounded-r-2xl shadow-warm-sm',
    subtle: 'bg-ivory-100/70 border-stone-200/60 shadow-none',
  };

  const dynamicStyle =
    variant === 'waypoint' && stageColorHex
      ? { borderLeftColor: stageColorHex }
      : undefined;

  return (
    <div
      className={clsx(baseStyles, variantStyles[variant], className)}
      style={dynamicStyle}
      {...props}
    >
      {children}
    </div>
  );
};
