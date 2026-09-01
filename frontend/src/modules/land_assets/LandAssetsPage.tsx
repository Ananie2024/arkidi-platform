import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { GisMapViewer } from '../../components/map/GisMapViewer';
import { Plus } from 'lucide-react';
import { LandParcel } from '../../core/types/land.types';
import { domainApi } from '../../core/api/domain';

export const LandAssetsPage: React.FC = () => {
  const { t } = useTranslation();
  const parcelsQuery = useQuery({
    queryKey: ['land-parcels'],
    queryFn: domainApi.listParcels,
  });

  const columns: Column<LandParcel>[] = [
    { header: t('land_assets.col_upi'), accessor: 'upi' },
    { header: t('land_assets.col_parcel_name'), accessor: 'parcel_name' },
    { header: t('land_assets.col_land_use'), accessor: 'land_use' },
    { header: t('land_assets.col_location'), accessor: (row) => `${row.district || '-'} / ${row.sector || '-'}` },
    { header: t('land_assets.col_area'), accessor: (row) => row.area_sqm.toLocaleString() },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">{t('land_assets.title')}</h1>
          <p className="text-xs text-gray-500 mt-0.5">{t('land_assets.subtitle')}</p>
        </div>
        <Button size="sm">
          <Plus className="w-4 h-4 mr-1.5" /> {t('land_assets.register')}
        </Button>
      </div>

      <Card title={t('land_assets.map_title')}>
        <GisMapViewer height="300px" />
      </Card>

      <Card>
        <Table
          columns={columns}
          data={parcelsQuery.data || []}
          isLoading={parcelsQuery.isLoading}
          emptyMessage={parcelsQuery.isError ? t('land_assets.empty_error') : t('land_assets.empty_none')}
        />
      </Card>
    </div>
  );
};
