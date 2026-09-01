import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { CalendarPlus } from 'lucide-react';
import { MassSchedule, domainApi } from '../../core/api/domain';

export const LiturgyPage: React.FC = () => {
  const { t } = useTranslation();
  const parishesQuery = useQuery({ queryKey: ['parishes'], queryFn: () => domainApi.listParishes() });
  const parishId = parishesQuery.data?.[0]?.id;
  const massesQuery = useQuery({
    queryKey: ['mass-schedules', parishId],
    queryFn: () => domainApi.listMassSchedules(parishId as string),
    enabled: Boolean(parishId),
  });

  const columns: Column<MassSchedule>[] = [
    { header: t('liturgy.col_mass_date'), accessor: 'mass_date' },
    { header: t('liturgy.col_start_time'), accessor: 'start_time' },
    { header: t('liturgy.col_language'), accessor: 'language' },
    { header: t('liturgy.col_celebrant'), accessor: (row) => row.celebrant_name || '-' },
    { header: t('liturgy.col_feast'), accessor: (row) => row.liturgical_feast || '-' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">{t('liturgy.title')}</h1>
          <p className="text-xs text-gray-500 mt-0.5">{t('liturgy.subtitle')}</p>
        </div>
        <Button size="sm">
          <CalendarPlus className="w-4 h-4 mr-1.5" /> {t('liturgy.schedule')}
        </Button>
      </div>

      <Card>
        <Table
          columns={columns}
          data={massesQuery.data || []}
          isLoading={parishesQuery.isLoading || massesQuery.isLoading}
          emptyMessage={parishesQuery.isError || massesQuery.isError ? t('liturgy.empty_error') : t('liturgy.empty_none')}
        />
      </Card>
    </div>
  );
};
