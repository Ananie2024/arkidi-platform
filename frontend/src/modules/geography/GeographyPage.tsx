import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { Plus } from 'lucide-react';
import { Deanery, domainApi } from '../../core/api/domain';

export const GeographyPage: React.FC = () => {
  const { t } = useTranslation();
  const deaneriesQuery = useQuery({
    queryKey: ['deaneries'],
    queryFn: domainApi.listDeaneries,
  });

  const columns: Column<Deanery>[] = [
    { header: t('geography.col_deanery_code'), accessor: 'code' },
    { header: t('geography.col_deanery_name'), accessor: 'name' },
    { header: t('geography.col_vicar'), accessor: (row) => row.vicar_forane_name || '-' },
    {
      header: t('common.actions'),
      accessor: (row) => (
        <a href={`/geography/parishes?deanery=${row.id}`} className="text-brand-500 hover:text-brand-600 font-medium text-xs">
          {t('geography.view_parishes')}
        </a>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">{t('geography.deaneries_title')}</h1>
          <p className="text-xs text-gray-500 mt-0.5">{t('geography.deaneries_subtitle')}</p>
        </div>
        <Button size="sm">
          <Plus className="w-4 h-4 mr-1.5" /> {t('geography.add_deanery')}
        </Button>
      </div>

      <Card>
        <Table
          columns={columns}
          data={deaneriesQuery.data || []}
          isLoading={deaneriesQuery.isLoading}
          emptyMessage={deaneriesQuery.isError ? t('geography.deaneries_empty_error') : t('geography.deaneries_empty_none')}
        />
      </Card>
    </div>
  );
};
