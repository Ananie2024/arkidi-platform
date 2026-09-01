import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Input } from '../../components/common/Input';
import { Button } from '../../components/common/Button';

export const ForgotPasswordPage: React.FC = () => {
  const { t } = useTranslation();
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
        <div className="text-center mb-6">
          <h2 className="text-xl font-bold text-gray-900">{t('auth.forgot.title')}</h2>
          <p className="text-xs text-gray-500 mt-1">
            {t('auth.forgot.subtitle')}
          </p>
        </div>
        <form className="space-y-4">
          <Input label={t('auth.forgot.email_label')} type="email" placeholder="name@archidiocesekigali.org" />
          <Button type="button" className="w-full">{t('auth.forgot.send_link')}</Button>
          <div className="text-center text-xs pt-2">
            <Link to="/login" className="text-brand-500 hover:text-brand-600 font-medium">
              {t('auth.forgot.back_to_sign_in')}
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
};
