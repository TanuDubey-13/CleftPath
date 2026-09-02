import React from 'react';
import { clsx } from 'clsx';
import { AlertCircle, AlertTriangle, CheckCircle2, Info, PhoneCall } from 'lucide-react';

export interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'info' | 'success' | 'warning' | 'danger' | 'emergency';
  title?: string;
  action?: React.ReactNode;
}

export const Alert: React.FC<AlertProps> = ({
  children,
  className,
  variant = 'info',
  title,
  action,
  ...props
}) => {
  const iconMap = {
    info: <Info className="w-5 h-5 text-teal-800 flex-shrink-0 mt-0.5" />,
    success: <CheckCircle2 className="w-5 h-5 text-sage-600 flex-shrink-0 mt-0.5" />,
    warning: <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />,
    danger: <AlertCircle className="w-5 h-5 text-rose-600 flex-shrink-0 mt-0.5" />,
    emergency: <AlertTriangle className="w-6 h-6 text-rose-600 flex-shrink-0 animate-bounce mt-0.5" />,
  };

  const variantStyles = {
    info: 'bg-teal-50 border border-teal-200/80 text-teal-950',
    success: 'bg-sage-100/60 border border-sage-200 text-sage-950',
    warning: 'bg-amber-50 border border-amber-200 text-amber-950',
    danger: 'bg-rose-50 border border-rose-200 text-rose-950',
    emergency: 'bg-rose-50 border-2 border-rose-500 text-rose-950 shadow-warm-md',
  };

  return (
    <div
      role="alert"
      className={clsx(
        'rounded-2xl p-4 sm:p-5 flex items-start gap-3.5 transition-all',
        variantStyles[variant],
        className
      )}
      {...props}
    >
      {iconMap[variant]}
      <div className="flex-1 space-y-1">
        {title && <h4 className="font-bold text-sm sm:text-base leading-tight">{title}</h4>}
        <div className="text-xs sm:text-sm leading-relaxed opacity-95">{children}</div>
        {variant === 'emergency' && (
          <div className="pt-2 flex flex-wrap gap-2.5">
            <a
              href="tel:911"
              className="inline-flex items-center gap-1.5 bg-rose-600 text-white font-bold px-3.5 py-1.5 rounded-xl text-xs sm:text-sm hover:bg-rose-700 transition"
            >
              <PhoneCall className="w-3.5 h-3.5" /> Call Emergency (911)
            </a>
            <button
              onClick={() => alert("Connecting to your accredited cleft team coordinator...")}
              className="inline-flex items-center gap-1.5 bg-white border border-rose-300 text-rose-900 font-semibold px-3.5 py-1.5 rounded-xl text-xs sm:text-sm hover:bg-rose-50 transition"
            >
              Contact Cleft On-Call Team
            </button>
          </div>
        )}
        {action && <div className="pt-2">{action}</div>}
      </div>
    </div>
  );
};
