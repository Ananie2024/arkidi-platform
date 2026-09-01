import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { ShieldX } from 'lucide-react';

export const UnauthorizedPage: React.FC = () => {
  const { t } = useTranslation();
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="max-w-md w-full text-center">
        <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-red-50 text-red-500 mb-6">
          <ShieldX className="w-10 h-10" />
        </div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">{t('error_pages.unauthorized_title')}</h1>
        <p className="text-sm text-gray-500 mb-8">
          {t('error_pages.unauthorized_body')}
        </p>
        <Link
          to="/dashboard"
          className="inline-flex items-center justify-center px-5 py-2.5 rounded-lg bg-brand-500 text-white text-sm font-medium hover:bg-brand-600 transition-colors"
        >
          {t('error_pages.back_to_dashboard')}
        </Link>
      </div>
    </div>
  );
};
