import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useTranslation } from 'react-i18next';
import { apiClient } from '../../core/api/client';
import { API_ENDPOINTS } from '../../core/api/endpoints';
import { Input } from '../../components/common/Input';
import { Button } from '../../components/common/Button';

type ForgotPasswordFormData = {
  email: string;
};

export const ForgotPasswordPage: React.FC = () => {
  const { t } = useTranslation();
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const forgotSchema = z.object({
    email: z.string().email(t('auth.forgot.email_required')),
  });

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ForgotPasswordFormData>({
    resolver: zodResolver(forgotSchema),
  });

  const emailField = register('email');

  const onSubmit = async (data: ForgotPasswordFormData) => {
    setErrorMessage(null);
    try {
      await apiClient.post(API_ENDPOINTS.auth.forgotPassword, { email: data.email });
      setIsSubmitted(true);
    } catch (err: unknown) {
      const error = err as {
        response?: {
          data?: {
            error?: { message?: string };
          };
        };
      };
      setErrorMessage(
        error.response?.data?.error?.message || t('auth.forgot.error_generic')
      );
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
        {!isSubmitted ? (
          <>
            <div className="text-center mb-6">
              <h2 className="text-xl font-bold text-gray-900">{t('auth.forgot.title')}</h2>
              <p className="text-xs text-gray-500 mt-1">
                {t('auth.forgot.subtitle')}
              </p>
            </div>

            {errorMessage && (
              <div className="mb-4 p-3 rounded-lg bg-red-50 border border-red-200 text-xs text-red-700">
                {errorMessage}
              </div>
            )}

            <form className="space-y-4" onSubmit={handleSubmit(onSubmit)}>
              <Input
                label={t('auth.forgot.email_label')}
                type="email"
                placeholder="name@archidiocesekigali.org"
                {...emailField}
                error={errors.email?.message}
              />
              <Button type="submit" className="w-full" isLoading={isSubmitting}>
                {t('auth.forgot.send_link')}
              </Button>
              <div className="text-center text-xs pt-2">
                <Link to="/login" className="text-brand-500 hover:text-brand-600 font-medium">
                  {t('auth.forgot.back_to_sign_in')}
                </Link>
              </div>
            </form>
          </>
        ) : (
          <div className="text-center py-4 space-y-4">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-green-100 text-green-600 text-2xl">
              &#10003;
            </div>
            <h3 className="text-lg font-semibold text-gray-900">
              {t('auth.forgot.success_title')}
            </h3>
            <p className="text-xs text-gray-500">
              {t('auth.forgot.success_message')}
            </p>
            <div className="pt-2">
              <Link
                to="/login"
                className="inline-block text-xs text-brand-500 hover:text-brand-600 font-medium"
              >
                {t('auth.forgot.back_to_sign_in')}
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
