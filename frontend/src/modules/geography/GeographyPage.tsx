import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { Plus } from 'lucide-react';
import { Deanery, domainApi } from '../../core/api/domain';

export const GeographyPage: React.FC = () => {
  const deaneriesQuery = useQuery({
    queryKey: ['deaneries'],
    queryFn: domainApi.listDeaneries,
  });

  const columns: Column<Deanery>[] = [
    { header: 'Deanery Code', accessor: 'code' },
    { header: 'Deanery Name', accessor: 'name' },
    { header: 'Vicar Forane', accessor: (row) => row.vicar_forane_name || '-' },
    {
      header: 'Actions',
      accessor: (row) => (
        <a href={`/geography/parishes?deanery=${row.id}`} className="text-brand-500 hover:text-brand-600 font-medium text-xs">
          View Parishes &rarr;
        </a>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Ecclesiastical Hierarchy & Deaneries</h1>
          <p className="text-xs text-gray-500 mt-0.5">Archdiocese of Kigali territorial jurisdiction and deanery zones</p>
        </div>
        <Button size="sm">
          <Plus className="w-4 h-4 mr-1.5" /> Add Deanery
        </Button>
      </div>

      <Card>
        <Table
          columns={columns}
          data={deaneriesQuery.data || []}
          isLoading={deaneriesQuery.isLoading}
          emptyMessage={deaneriesQuery.isError ? 'Unable to load deaneries from the API.' : 'No deaneries found.'}
        />
      </Card>
    </div>
  );
};
