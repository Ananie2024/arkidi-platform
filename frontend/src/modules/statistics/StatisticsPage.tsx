import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { BarChart3 } from 'lucide-react';
import { AnnualReport, domainApi } from '../../core/api/domain';

export const StatisticsPage: React.FC = () => {
  const { t } = useTranslation();
  const currentYear = new Date().getFullYear();
  const reportsQuery = useQuery({
    queryKey: ['annual-reports', currentYear],
    queryFn: () => domainApi.listAnnualReports(currentYear),
  });
  const annuarioQuery = useQuery({
    queryKey: ['annuario-pontificio', currentYear],
    queryFn: () => domainApi.getAnnuarioPontificio(currentYear),
  });

  const columns: Column<AnnualReport>[] = [
    { header: t('statistics.col_parish_id'), accessor: 'parish_id' },
    { header: t('statistics.col_year'), accessor: 'report_year' },
    { header: t('statistics.col_catholic_population'), accessor: 'total_catholic_population' },
    { header: t('statistics.col_baptisms'), accessor: (row) => row.infant_baptisms + row.adult_baptisms },
    { header: t('statistics.col_confirmations'), accessor: 'confirmations' },
    { header: t('statistics.col_marriages'), accessor: (row) => row.marriages_both_catholic + row.marriages_mixed_religion },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">{t('statistics.title')}</h1>
          <p className="text-xs text-gray-500 mt-0.5">{t('statistics.subtitle')}</p>
        </div>
        <Button size="sm">
          <BarChart3 className="w-4 h-4 mr-1.5" /> {t('statistics.generate')}
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card title={t('statistics.card_parishes')}>
          <div className="text-2xl font-bold text-gray-900">{annuarioQuery.data?.total_parishes ?? '-'}</div>
        </Card>
        <Card title={t('statistics.card_priests')}>
          <div className="text-2xl font-bold text-gray-900">{annuarioQuery.data?.total_priests ?? '-'}</div>
        </Card>
        <Card title={t('statistics.card_catholics')}>
          <div className="text-2xl font-bold text-gray-900">{annuarioQuery.data?.total_catholics?.toLocaleString() ?? '-'}</div>
        </Card>
      </div>

      <Card>
        <Table
          columns={columns}
          data={reportsQuery.data || []}
          isLoading={reportsQuery.isLoading || annuarioQuery.isLoading}
          emptyMessage={reportsQuery.isError || annuarioQuery.isError ? t('statistics.empty_error') : t('statistics.empty_none', { year: currentYear })}
        />
      </Card>
    </div>
  );
};
