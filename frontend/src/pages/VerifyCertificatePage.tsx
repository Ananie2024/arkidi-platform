import React from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { BadgeCheck, ShieldAlert } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { domainApi } from '../core/api/domain';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

export const VerifyCertificatePage: React.FC = () => {
  const { token = '' } = useParams();
  const { t } = useTranslation();
  const query = useQuery({
    queryKey: ['verify-certificate', token],
    queryFn: () => domainApi.verifyCertificate(token),
    enabled: Boolean(token),
    retry: false,
  });

  if (query.isLoading) return <LoadingSpinner className="min-h-screen" />;
  const valid = query.isSuccess;
  const type = query.data?.sacrament_type?.replace(/_/g, ' ').toLowerCase();

  return (
    <main className="flex min-h-screen items-center justify-center bg-gray-50 px-4 py-10">
      <section className="w-full max-w-md rounded-2xl border border-gray-200 bg-white p-8 text-center shadow-sm">
        {valid ? <BadgeCheck className="mx-auto mb-4 h-12 w-12 text-green-600" /> : <ShieldAlert className="mx-auto mb-4 h-12 w-12 text-red-600" />}
        <h1 className="text-xl font-bold text-gray-900">{valid ? t('sacraments.verify_valid', 'Certificate verified') : t('sacraments.verify_invalid', 'Certificate not valid')}</h1>
        <p className="mt-2 text-sm text-gray-600">
          {valid ? t('sacraments.verify_valid_body', 'This certificate is registered in the Arkidi system.') : t('sacraments.verify_invalid_body', 'The certificate could not be verified. Contact the issuing parish office.')}
        </p>
        {valid && query.data && (
          <dl className="mt-6 space-y-3 rounded-lg bg-gray-50 p-4 text-left text-sm">
            <div className="flex justify-between gap-3"><dt className="text-gray-500">{t('sacraments.cert_serial', 'Certificate number')}</dt><dd className="font-mono font-semibold text-gray-900">{query.data.certificate_number}</dd></div>
            <div className="flex justify-between gap-3"><dt className="text-gray-500">{t('sacraments.cert_sacrament_type', 'Sacrament')}</dt><dd className="font-semibold capitalize text-gray-900">{type}</dd></div>
            <div className="flex justify-between gap-3"><dt className="text-gray-500">{t('common.date', 'Issued')}</dt><dd className="text-gray-900">{new Date(query.data.created_at).toLocaleDateString()}</dd></div>
          </dl>
        )}
      </section>
    </main>
  );
};
