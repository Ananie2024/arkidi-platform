import React from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Card } from '../../components/common/Card';
import { Badge } from '../../components/common/Badge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { domainApi } from '../../core/api/domain';

export const ParishDetailPage: React.FC = () => {
  const { t } = useTranslation();
  const { parishId } = useParams<{ parishId: string }>();

  const parishQuery = useQuery({
    queryKey: ['parish', parishId],
    queryFn: () => domainApi.getParish(parishId as string),
    enabled: !!parishId,
  });

  if (parishQuery.isLoading) {
    return <LoadingSpinner className="py-20" />;
  }

  if (parishQuery.isError || !parishQuery.data) {
    return (
      <div className="text-sm text-gray-500 py-20 text-center">
        {t('geography.detail_load_error')}
      </div>
    );
  }

  const parish = parishQuery.data;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{parish.name}</h1>
          <p className="text-xs text-gray-500 mt-1">{t('geography.code')} {parish.code}</p>
        </div>
        <Badge variant="success">{t('geography.active_parish')}</Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card title={t('geography.info_title')}>
          <div className="space-y-3 text-xs">
            <div><span className="font-semibold text-gray-700">{t('geography.patron_saint')}</span> {parish.patron_saint || '-'}</div>
            <div><span className="font-semibold text-gray-700">{t('geography.establishment_date')}</span> {parish.establishment_date || '-'}</div>
            <div><span className="font-semibold text-gray-700">{t('geography.phone')}</span> {parish.phone || '-'}</div>
            <div><span className="font-semibold text-gray-700">{t('geography.email')}</span> {parish.email || '-'}</div>
            <div><span className="font-semibold text-gray-700">{t('geography.address')}</span> {parish.address || '-'}</div>
            <div><span className="font-semibold text-gray-700">{t('geography.district_sector')}</span> {[parish.district, parish.sector].filter(Boolean).join(' / ') || '-'}</div>
          </div>
        </Card>

        <Card title={t('geography.geo_title')}>
          <div className="space-y-2 text-xs">
            <div><span className="font-semibold">{t('geography.latitude')}</span> {parish.latitude ?? '-'}</div>
            <div><span className="font-semibold">{t('geography.longitude')}</span> {parish.longitude ?? '-'}</div>
            <div><span className="font-semibold">{t('geography.deanery_id')}</span> {parish.deanery_id}</div>
          </div>
        </Card>

        <Card title={t('geography.registration_title')}>
          <div className="space-y-2 text-xs">
            <div><span className="font-semibold">{t('geography.created')}</span> {parish.created_at ? new Date(parish.created_at).toLocaleDateString() : '-'}</div>
          </div>
        </Card>
      </div>
    </div>
  );
};
