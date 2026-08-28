import React from 'react';
import { Users, Scroll, MapPin, Church } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { StatCard } from './components/StatCard';
import { Card } from '../../components/common/Card';
import { GisMapViewer } from '../../components/map/GisMapViewer';
import { domainApi } from '../../core/api/domain';

export const DashboardPage: React.FC = () => {
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
            <h1 className="text-2xl font-bold">Arkidi Platform</h1>
            <p className="text-brand-100 text-xs mt-1">
              Consolidated Parish Administration, Sacramental Registers & GIS Land Intelligence
            </p>
          </div>
          <div className="bg-white/10 backdrop-blur-md px-4 py-2 rounded-xl text-xs border border-white/20">
            Current Year: <span className="font-bold">{currentYear}</span> &bull;{' '}
            {formatNumber(annuario?.total_parishes)} Parishes
          </div>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Faithful"
          value={formatNumber(annuario?.total_catholics)}
          subtitle="Catholic population (reported)"
          icon={Users}
          color="brand"
        />
        <StatCard
          title="Baptisms Recorded"
          value={formatNumber(annuario?.total_baptisms)}
          subtitle="Reported for the year"
          icon={Scroll}
          color="blue"
        />
        <StatCard
          title="Active Priests"
          value={formatNumber(annuario?.total_priests)}
          subtitle="In the Archdiocese"
          icon={Church}
          color="amber"
        />
        <StatCard
          title="Parish Land Parcels"
          value={formatNumber(parcels.length)}
          subtitle="Registered in the cadastre"
          icon={MapPin}
          color="emerald"
        />
      </div>

      {/* Main Grid: GIS Map & Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card
            title="Archdiocesan GIS Parish & Property Map"
            subtitle="Geospatial distribution of parishes in the Archdiocese"
          >
            {parishesQuery.isLoading ? (
              <div className="text-xs text-gray-500 py-20 text-center">Loading parish locations…</div>
            ) : (
              <GisMapViewer markers={parishMarkers} height="380px" />
            )}
          </Card>
        </div>

        <div>
          <Card title="Quick Canonical Actions" subtitle="Frequently used secretary workflows">
            <div className="space-y-3">
              <a
                href="/sacraments"
                className="block p-3 rounded-lg border border-gray-100 hover:border-brand-200 hover:bg-brand-50 transition-colors"
              >
                <div className="text-xs font-semibold text-gray-900">Record New Baptism</div>
                <div className="text-[11px] text-gray-500 mt-0.5">Enter canonical register page and act number</div>
              </a>
              <a
                href="/faithful"
                className="block p-3 rounded-lg border border-gray-100 hover:border-brand-200 hover:bg-brand-50 transition-colors"
              >
                <div className="text-xs font-semibold text-gray-900">Register Parishioner / Family</div>
                <div className="text-[11px] text-gray-500 mt-0.5">Assign to Small Christian Community (Umuryango-remezo)</div>
              </a>
              <a
                href="/land-assets"
                className="block p-3 rounded-lg border border-gray-100 hover:border-brand-200 hover:bg-brand-50 transition-colors"
              >
                <div className="text-xs font-semibold text-gray-900">Cadastral UPI Parcel Registry</div>
                <div className="text-[11px] text-gray-500 mt-0.5">View title deeds and parcel polygons</div>
              </a>
              <a
                href="/statistics"
                className="block p-3 rounded-lg border border-gray-100 hover:border-brand-200 hover:bg-brand-50 transition-colors"
              >
                <div className="text-xs font-semibold text-gray-900">Annuario Pontificio Extracts</div>
                <div className="text-[11px] text-gray-500 mt-0.5">Generate Holy See statistical returns</div>
              </a>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};