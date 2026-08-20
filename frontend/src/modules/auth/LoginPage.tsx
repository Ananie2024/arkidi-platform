import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { apiClient } from '../../core/api/client';
import { API_ENDPOINTS } from '../../core/api/endpoints';
import { useAuth } from '../../core/hooks/useAuth';
import { Input } from '../../components/common/Input';
import { Button } from '../../components/common/Button';
import { LanguageSwitcher } from '../../components/common/LanguageSwitcher';

const loginSchema = z.object({
  username_or_email: z.string().min(1, 'Username or Email is required'),
  password: z.string().min(1, 'Password is required'),
});

type LoginFormData = z.infer<typeof loginSchema>;

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    setErrorMessage(null);
    try {
      const res = await apiClient.post(API_ENDPOINTS.auth.login, data);
      if (res.data?.data) {
        const { access_token, refresh_token } = res.data.data;
        await login(access_token, refresh_token);
        navigate('/dashboard');
      }
    } catch (err: unknown) {
      const error = err as {
        response?: {
          data?: {
            error?: { message?: string };
          };
        };
      };
      setErrorMessage(
        error.response?.data?.error?.message || 'Authentication failed. Please check your credentials.'
      );
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
        <div className="flex justify-end mb-4">
          <LanguageSwitcher />
        </div>

        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-brand-500 text-white text-3xl font-bold mb-4 shadow-md">
            ☩
          </div>
          <h2 className="text-2xl font-bold text-gray-900 tracking-tight">Arkidi Platform</h2>
          <p className="text-xs text-gray-500 mt-1 uppercase tracking-wider font-medium">
            Archdiocese of Kigali &bull; Archidiocèse de Kigali
          </p>
        </div>

        {errorMessage && (
          <div className="mb-6 p-3 rounded-lg bg-red-50 border border-red-200 text-xs text-red-700">
            {errorMessage}
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="Username or Email"
            placeholder="admin@archidiocesekigali.org"
            {...register('username_or_email')}
            error={errors.username_or_email?.message}
          />

          <Input
            label="Password"
            type="password"
            placeholder="••••••••"
            {...register('password')}
            error={errors.password?.message}
          />

          <div className="flex items-center justify-between text-xs pt-1">
            <label className="flex items-center gap-1.5 text-gray-600 cursor-pointer">
              <input type="checkbox" className="rounded text-brand-500 focus:ring-brand-500" />
              Remember me
            </label>
            <a href="/forgot-password" className="text-brand-500 hover:text-brand-600 font-medium">
              Forgot password?
            </a>
          </div>

          <Button type="submit" className="w-full mt-4" size="lg" isLoading={isSubmitting}>
            Sign In to Arkidi
          </Button>
        </form>

        <div className="mt-8 text-center text-xs text-gray-400">
          Archdiocese of Kigali Ecclesiastical Management System
        </div>
      </div>
    </div>
  );
};
