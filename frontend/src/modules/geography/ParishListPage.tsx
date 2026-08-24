import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useSearchParams } from 'react-router-dom';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { Plus } from 'lucide-react';
import { Parish, domainApi } from '../../core/api/domain';

export const ParishListPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const deaneryId = searchParams.get('deanery');

  const parishesQuery = useQuery({
    queryKey: ['parishes', deaneryId],
    queryFn: () => domainApi.listParishes(deaneryId),
  });

  const columns: Column<Parish>[] = [
    { header: 'Parish Code', accessor: 'code' },
    { header: 'Parish Name', accessor: 'name' },
    { header: 'Patron Saint', accessor: (row) => row.patron_saint || '-' },
    { header: 'District', accessor: (row) => row.district || '-' },
    { header: 'Sector', accessor: (row) => row.sector || '-' },
    {
      header: 'Actions',
      accessor: (row) => (
        <a href={`/geography/parishes/${row.id}`} className="text-brand-500 hover:text-brand-600 font-medium text-xs">
          Open Parish Details
        </a>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Parishes of the Archdiocese</h1>
          <p className="text-xs text-gray-500 mt-0.5">Official Catholic parish directory in Kigali and surrounding vicariates</p>
        </div>
        <Button size="sm">
          <Plus className="w-4 h-4 mr-1.5" /> Register New Parish
        </Button>
      </div>

      <Card>
        <Table
          columns={columns}
          data={parishesQuery.data || []}
          isLoading={parishesQuery.isLoading}
          emptyMessage={parishesQuery.isError ? 'Unable to load parishes from the API.' : 'No parishes found.'}
        />
      </Card>
    </div>
  );
};
