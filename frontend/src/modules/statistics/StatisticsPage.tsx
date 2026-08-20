import React from 'react';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { BarChart3 } from 'lucide-react';

interface AnnualReportItem {
  id: string;
  parish: string;
  report_year: number;
  total_catholic_population: number;
  baptisms: number;
  confirmations: number;
  marriages: number;
}

export const StatisticsPage: React.FC = () => {
  const dummyReports: AnnualReportItem[] = [
    {
      id: '1',
      parish: 'Paroisse Sainte Famille',
      report_year: 2025,
      total_catholic_population: 21840,
      baptisms: 420,
      confirmations: 310,
      marriages: 96,
    },
    {
      id: '2',
      parish: 'Cathédrale Saint Michel',
      report_year: 2025,
      total_catholic_population: 15620,
      baptisms: 385,
      confirmations: 275,
      marriages: 88,
    },
  ];

  const columns: Column<AnnualReportItem>[] = [
    { header: 'Parish', accessor: 'parish' },
    { header: 'Year', accessor: 'report_year' },
    { header: 'Catholic Population', accessor: 'total_catholic_population' },
    { header: 'Baptisms', accessor: 'baptisms' },
    { header: 'Confirmations', accessor: 'confirmations' },
    { header: 'Marriages', accessor: 'marriages' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Pontifical Statistics & Reporting</h1>
          <p className="text-xs text-gray-500 mt-0.5">
            Annual parish returns and Annuario Pontificio extracts for the Holy See
          </p>
        </div>
        <Button size="sm">
          <BarChart3 className="w-4 h-4 mr-1.5" /> Generate Report
        </Button>
      </div>

      <Card>
        <Table columns={columns} data={dummyReports} />
      </Card>
    </div>
  );
};
