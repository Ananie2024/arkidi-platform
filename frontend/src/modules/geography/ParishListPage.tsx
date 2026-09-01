import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { Plus } from 'lucide-react';
import { Parish, domainApi } from '../../core/api/domain';

export const ParishListPage: React.FC = () => {
  const { t } = useTranslation();
  const [searchParams] = useSearchParams();
  const deaneryId = searchParams.get('deanery');

  const parishesQuery = useQuery({
    queryKey: ['parishes', deaneryId],
    queryFn: () => domainApi.listParishes(deaneryId),
  });

  const columns: Column<Parish>[] = [
    { header: t('geography.col_parish_code'), accessor: 'code' },
    { header: t('geography.col_parish_name'), accessor: 'name' },
    { header: t('geography.col_patron_saint'), accessor: (row) => row.patron_saint || '-' },
    { header: t('geography.col_district'), accessor: (row) => row.district || '-' },
    { header: t('geography.col_sector'), accessor: (row) => row.sector || '-' },
    {
      header: t('common.actions'),
      accessor: (row) => (
        <a href={`/geography/parishes/${row.id}`} className="text-brand-500 hover:text-brand-600 font-medium text-xs">
          {t('geography.open_parish')}
        </a>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">{t('geography.parish_title')}</h1>
          <p className="text-xs text-gray-500 mt-0.5">{t('geography.parish_subtitle')}</p>
        </div>
        <Button size="sm">
          <Plus className="w-4 h-4 mr-1.5" /> {t('geography.register_new_parish')}
        </Button>
      </div>

      <Card>
        <Table
          columns={columns}
          data={parishesQuery.data || []}
          isLoading={parishesQuery.isLoading}
          emptyMessage={parishesQuery.isError ? t('geography.parishes_empty_error') : t('geography.parishes_empty_none')}
        />
      </Card>
    </div>
  );
};
