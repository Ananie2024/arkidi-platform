import React from 'react';
import { Link } from 'react-router-dom';
import { Input } from '../../components/common/Input';
import { Button } from '../../components/common/Button';

export const ForgotPasswordPage: React.FC = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
        <div className="text-center mb-6">
          <h2 className="text-xl font-bold text-gray-900">Reset Password</h2>
          <p className="text-xs text-gray-500 mt-1">
            Enter your official archdiocesan email to receive a password reset link.
          </p>
        </div>
        <form className="space-y-4">
          <Input label="Official Email Address" type="email" placeholder="name@archidiocesekigali.org" />
          <Button type="button" className="w-full">Send Recovery Link</Button>
          <div className="text-center text-xs pt-2">
            <Link to="/login" className="text-brand-500 hover:text-brand-600 font-medium">
              &larr; Back to Sign In
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
};
