import React, { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useTranslation } from 'react-i18next';
import { apiClient } from '../../core/api/client';
import { API_ENDPOINTS } from '../../core/api/endpoints';
import { Input } from '../../components/common/Input';
import { Button } from '../../components/common/Button';

type ResetPasswordFormData = {
  token: string;
  new_password: string;
  confirm_password: string;
};

export const ResetPasswordPage: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [isSuccess, setIsSuccess] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const token = searchParams.get('token') || '';

  const resetSchema = z.object({
    token: z.string().min(1),
    new_password: z
      .string()
      .min(10, t('auth.reset.password_min_length')),
    confirm_password: z.string(),
  }).refine((data) => data.new_password === data.confirm_password, {
    message: t('auth.reset.passwords_must_match'),
    path: ['confirm_password'],
  });

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ResetPasswordFormData>({
    resolver: zodResolver(resetSchema),
    defaultValues: { token: token },
  });

  const passwordField = register('new_password');
  const confirmPasswordField = register('confirm_password');
  const tokenField = register('token');

  const onSubmit = async (data: ResetPasswordFormData) => {
    setErrorMessage(null);
    try {
      await apiClient.post(API_ENDPOINTS.auth.resetPassword, {
        token: data.token,
        new_password: data.new_password,
      });
      setIsSuccess(true);
      setTimeout(() => navigate('/login'), 3000);
    } catch (err: unknown) {
      const error = err as {
        response?: {
          data?: {
            error?: { message?: string };
          };
        };
      };
      setErrorMessage(
        error.response?.data?.error?.message || t('auth.reset.error_generic')
      );
    }
  };

  if (isSuccess) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-xl border border-gray-100 p-8 text-center space-y-4">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-green-100 text-green-600 text-2xl">
            &#10003;
          </div>
          <h3 className="text-lg font-semibold text-gray-900">
            {t('auth.reset.success_title')}
          </h3>
          <p className="text-xs text-gray-500">
            {t('auth.reset.success_message')}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
        <div className="text-center mb-6">
          <h2 className="text-xl font-bold text-gray-900">{t('auth.reset.title')}</h2>
          <p className="text-xs text-gray-500 mt-1">
            {t('auth.reset.subtitle')}
          </p>
        </div>

        {errorMessage && (
          <div className="mb-4 p-3 rounded-lg bg-red-50 border border-red-200 text-xs text-red-700">
            {errorMessage}
          </div>
        )}

        {!token && (
          <div className="mb-4 p-3 rounded-lg bg-yellow-50 border border-yellow-200 text-xs text-yellow-700">
            {t('auth.reset.no_token')}
          </div>
        )}

        <form className="space-y-4" onSubmit={handleSubmit(onSubmit)}>
          <input type="hidden" {...tokenField} />
          <Input
            label={t('auth.reset.password_label')}
            type="password"
            placeholder="••••••••"
            {...passwordField}
            error={errors.new_password?.message}
          />
          <Input
            label={t('auth.reset.confirm_password_label')}
            type="password"
            placeholder="••••••••"
            {...confirmPasswordField}
            error={errors.confirm_password?.message}
          />
          <Button
            type="submit"
            className="w-full"
            isLoading={isSubmitting}
            disabled={!token}
          >
            {t('auth.reset.submit')}
          </Button>
          <div className="text-center text-xs pt-2">
            <a
              href="/login"
              className="text-brand-500 hover:text-brand-600 font-medium"
            >
              {t('auth.reset.back_to_sign_in')}
            </a>
          </div>
        </form>
      </div>
    </div>
  );
};