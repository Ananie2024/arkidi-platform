import React from 'react';
import { Users, Scroll, MapPin, Church } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { StatCard } from './components/StatCard';
import { Card } from '../../components/common/Card';
import { GisMapViewer } from '../../components/map/GisMapViewer';
import { domainApi } from '../../core/api/domain';

export const DashboardPage: React.FC = () => {
  const { t } = useTranslation();
  const currentYear = new Date().getFullYear();

  const annuarioQuery = useQuery({
    queryKey: ['annuario', currentYear],
    queryFn: () => domainApi.getAnnuarioPontificio(currentYear),
  });

  const parishesQuery = useQuery({
    queryKey: ['parishes'],
    queryFn: () => domainApi.listParishes(),
  });

  const parcelsQuery = useQuery({
    queryKey: ['parcels'],
    queryFn: domainApi.listParcels,
  });

  const annuario = annuarioQuery.data;
  const parishes = parishesQuery.data || [];
  const parcels = parcelsQuery.data || [];

  const parishMarkers = parishes
    .filter((p) => p.latitude != null && p.longitude != null)
    .map((p) => ({
      id: p.id,
      position: [p.latitude as number, p.longitude as number] as [number, number],
      title: p.name,
      description: p.code,
    }));

  const formatNumber = (value?: number) =>
    value == null ? '—' : value.toLocaleString('en-US');

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div className="bg-gradient-to-r from-brand-700 via-brand-600 to-brand-500 rounded-2xl p-6 text-white shadow-md">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold">{t('dashboard.title')}</h1>
            <p className="text-brand-100 text-xs mt-1">
              {t('dashboard.subtitle')}
            </p>
          </div>
          <div className="bg-white/10 backdrop-blur-md px-4 py-2 rounded-xl text-xs border border-white/20">
            {t('dashboard.current_year')} <span className="font-bold">{currentYear}</span> &bull;{' '}
            {formatNumber(annuario?.total_parishes)} {t('dashboard.parishes')}
          </div>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title={t('dashboard.total_faithful')}
          value={formatNumber(annuario?.total_catholics)}
          subtitle={t('dashboard.faithful_subtitle')}
          icon={Users}
          color="brand"
        />
        <StatCard
          title={t('dashboard.baptisms_recorded')}
          value={formatNumber(annuario?.total_baptisms)}
          subtitle={t('dashboard.baptisms_subtitle')}
          icon={Scroll}
          color="blue"
        />
        <StatCard
          title={t('dashboard.active_priests')}
          value={formatNumber(annuario?.total_priests)}
          subtitle={t('dashboard.priests_subtitle')}
          icon={Church}
          color="amber"
        />
        <StatCard
          title={t('dashboard.parcel_count')}
          value={formatNumber(parcels.length)}
          subtitle={t('dashboard.parcel_subtitle')}
          icon={MapPin}
          color="emerald"
        />
      </div>

      {/* Main Grid: GIS Map & Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card
            title={t('dashboard.gis_title')}
            subtitle={t('dashboard.gis_subtitle')}
          >
            {parishesQuery.isLoading ? (
              <div className="text-xs text-gray-500 py-20 text-center">{t('dashboard.gis_loading')}</div>
            ) : (
              <GisMapViewer markers={parishMarkers} height="380px" />
            )}
          </Card>
        </div>

        <div>
          <Card title={t('dashboard.quick_actions_title')} subtitle={t('dashboard.quick_actions_subtitle')}>
            <div className="space-y-3">
              <a
                href="/sacraments"
                className="block p-3 rounded-lg border border-gray-100 hover:border-brand-200 hover:bg-brand-50 transition-colors"
              >
                <div className="text-xs font-semibold text-gray-900">{t('dashboard.action_baptism')}</div>
                <div className="text-[11px] text-gray-500 mt-0.5">{t('dashboard.action_baptism_desc')}</div>
              </a>
              <a
                href="/faithful"
                className="block p-3 rounded-lg border border-gray-100 hover:border-brand-200 hover:bg-brand-50 transition-colors"
              >
                <div className="text-xs font-semibold text-gray-900">{t('dashboard.action_faithful')}</div>
                <div className="text-[11px] text-gray-500 mt-0.5">{t('dashboard.action_faithful_desc')}</div>
              </a>
              <a
                href="/land-assets"
                className="block p-3 rounded-lg border border-gray-100 hover:border-brand-200 hover:bg-brand-50 transition-colors"
              >
                <div className="text-xs font-semibold text-gray-900">{t('dashboard.action_parcel')}</div>
                <div className="text-[11px] text-gray-500 mt-0.5">{t('dashboard.action_parcel_desc')}</div>
              </a>
              <a
                href="/statistics"
                className="block p-3 rounded-lg border border-gray-100 hover:border-brand-200 hover:bg-brand-50 transition-colors"
              >
                <div className="text-xs font-semibold text-gray-900">{t('dashboard.action_statistics')}</div>
                <div className="text-[11px] text-gray-500 mt-0.5">{t('dashboard.action_statistics_desc')}</div>
              </a>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};