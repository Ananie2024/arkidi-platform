import React, { ReactNode } from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

interface CardProps {
  title?: string;
  subtitle?: string;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
}

export const Card: React.FC<CardProps> = ({ title, subtitle, action, children, className }) => {
  return (
    <div className={twMerge(clsx('bg-white rounded-2xl border border-gray-200 shadow-[0_8px_24px_rgba(16,43,69,0.055)] overflow-hidden', className))}>
      {(title || action) && (
        <div className="px-6 py-4 border-b border-gray-100 border-l-[3px] border-l-gold-400 bg-gradient-to-r from-brand-50/80 to-white flex items-center justify-between">
          <div>
            {title && <h3 className="font-semibold text-gray-900 text-base">{title}</h3>}
            {subtitle && <p className="text-xs text-gray-500 mt-0.5">{subtitle}</p>}
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      <div className="p-6">{children}</div>
    </div>
  );
};
