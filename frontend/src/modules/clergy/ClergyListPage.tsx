import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { Plus } from 'lucide-react';
import { Priest, domainApi } from '../../core/api/domain';

export const ClergyListPage: React.FC = () => {
  const { t } = useTranslation();
  const clergyQuery = useQuery({
    queryKey: ['priests'],
    queryFn: domainApi.listPriests,
  });

  const columns: Column<Priest>[] = [
    {
      header: t('clergy.col_name_title'),
      accessor: (row) => (
        <div>
          <span className="text-xs text-brand-600 font-semibold">{row.title} </span>
          <span className="text-sm font-medium text-gray-900">{row.last_name} {row.first_name}</span>
        </div>
      ),
    },
    { header: t('clergy.col_role'), accessor: (row) => row.current_role || '-' },
    { header: t('clergy.col_assignment'), accessor: (row) => row.current_parish_id || '-' },
    { header: t('clergy.col_ordination'), accessor: (row) => row.ordination_date || '-' },
    { header: t('clergy.col_status'), accessor: (row) => <Badge variant={row.status === 'ACTIVE_DUTY' ? 'success' : 'neutral'}>{row.status}</Badge> },
    {
      header: t('common.actions'),
      accessor: (row) => (
        <a href={`/clergy/${row.id}`} className="text-brand-500 hover:text-brand-600 font-medium text-xs">
          {t('clergy.view_dossier')}
        </a>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">{t('clergy.title')}</h1>
          <p className="text-xs text-gray-500 mt-0.5">{t('clergy.subtitle')}</p>
        </div>
        <Button size="sm">
          <Plus className="w-4 h-4 mr-1.5" /> {t('clergy.register')}
        </Button>
      </div>

      <Card>
        <Table
          columns={columns}
          data={clergyQuery.data || []}
          isLoading={clergyQuery.isLoading}
          emptyMessage={clergyQuery.isError ? t('clergy.empty_error') : t('clergy.empty_none')}
        />
      </Card>
    </div>
  );
};
