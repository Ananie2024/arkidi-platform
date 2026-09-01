import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { Plus } from 'lucide-react';
import { Ministry, domainApi } from '../../core/api/domain';

export const MinistriesPage: React.FC = () => {
  const { t } = useTranslation();
  const ministriesQuery = useQuery({
    queryKey: ['ministries'],
    queryFn: domainApi.listMinistries,
  });

  const columns: Column<Ministry>[] = [
    { header: t('ministries.col_ministry'), accessor: 'name' },
    { header: t('ministries.col_category'), accessor: 'category' },
    { header: t('ministries.col_leader'), accessor: (row) => row.leader_name || '-' },
    { header: t('ministries.col_schedule'), accessor: (row) => row.meeting_schedule || '-' },
    { header: t('ministries.col_status'), accessor: (row) => (row.is_active ? <Badge variant="success">{t('ministries.active')}</Badge> : <Badge variant="neutral">{t('ministries.inactive')}</Badge>) },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">{t('ministries.title')}</h1>
          <p className="text-xs text-gray-500 mt-0.5">{t('ministries.subtitle')}</p>
        </div>
        <Button size="sm">
          <Plus className="w-4 h-4 mr-1.5" /> {t('ministries.new')}
        </Button>
      </div>

      <Card>
        <Table
          columns={columns}
          data={ministriesQuery.data || []}
          isLoading={ministriesQuery.isLoading}
          emptyMessage={ministriesQuery.isError ? t('ministries.empty_error') : t('ministries.empty_none')}
        />
      </Card>
    </div>
  );
};
