import React from 'react';
import { useTranslation } from 'react-i18next';

export const Footer: React.FC = () => {
  const { t } = useTranslation();
  return (
    <footer className="bg-white border-t border-gray-200 py-3 px-6 text-center text-xs text-gray-500">
      <div className="flex flex-col sm:flex-row items-center justify-between gap-2 max-w-7xl mx-auto">
        <div>{t('layout.footer_left')}</div>
        <div className="text-gray-400">{t('layout.footer_confidential')}</div>
      </div>
    </footer>
  );
};
