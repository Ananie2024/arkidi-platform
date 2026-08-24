import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { BarChart3 } from 'lucide-react';
import { AnnualReport, domainApi } from '../../core/api/domain';

export const StatisticsPage: React.FC = () => {
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
    { header: 'Parish ID', accessor: 'parish_id' },
    { header: 'Year', accessor: 'report_year' },
    { header: 'Catholic Population', accessor: 'total_catholic_population' },
    { header: 'Baptisms', accessor: (row) => row.infant_baptisms + row.adult_baptisms },
    { header: 'Confirmations', accessor: 'confirmations' },
    { header: 'Marriages', accessor: (row) => row.marriages_both_catholic + row.marriages_mixed_religion },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Pontifical Statistics & Reporting</h1>
          <p className="text-xs text-gray-500 mt-0.5">Annual parish returns and Annuario Pontificio extracts for the Holy See</p>
        </div>
        <Button size="sm">
          <BarChart3 className="w-4 h-4 mr-1.5" /> Generate Report
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card title="Parishes">
          <div className="text-2xl font-bold text-gray-900">{annuarioQuery.data?.total_parishes ?? '-'}</div>
        </Card>
        <Card title="Priests">
          <div className="text-2xl font-bold text-gray-900">{annuarioQuery.data?.total_priests ?? '-'}</div>
        </Card>
        <Card title="Catholics">
          <div className="text-2xl font-bold text-gray-900">{annuarioQuery.data?.total_catholics?.toLocaleString() ?? '-'}</div>
        </Card>
      </div>

      <Card>
        <Table
          columns={columns}
          data={reportsQuery.data || []}
          isLoading={reportsQuery.isLoading || annuarioQuery.isLoading}
          emptyMessage={reportsQuery.isError || annuarioQuery.isError ? 'Unable to load statistics from the API.' : `No parish reports found for ${currentYear}.`}
        />
      </Card>
    </div>
  );
};
