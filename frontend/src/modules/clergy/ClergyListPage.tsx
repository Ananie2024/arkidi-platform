import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { Plus } from 'lucide-react';
import { Priest, domainApi } from '../../core/api/domain';

export const ClergyListPage: React.FC = () => {
  const clergyQuery = useQuery({
    queryKey: ['priests'],
    queryFn: domainApi.listPriests,
  });

  const columns: Column<Priest>[] = [
    {
      header: 'Clergy Name & Title',
      accessor: (row) => (
        <div>
          <span className="text-xs text-brand-600 font-semibold">{row.title} </span>
          <span className="text-sm font-medium text-gray-900">{row.last_name} {row.first_name}</span>
        </div>
      ),
    },
    { header: 'Current Role', accessor: (row) => row.current_role || '-' },
    { header: 'Current Assignment / Parish', accessor: (row) => row.current_parish_id || '-' },
    { header: 'Ordination Date', accessor: (row) => row.ordination_date || '-' },
    { header: 'Status', accessor: (row) => <Badge variant={row.status === 'ACTIVE_DUTY' ? 'success' : 'neutral'}>{row.status}</Badge> },
    {
      header: 'Actions',
      accessor: (row) => (
        <a href={`/clergy/${row.id}`} className="text-brand-500 hover:text-brand-600 font-medium text-xs">
          View Dossier &rarr;
        </a>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Clergy & Religious Roster</h1>
          <p className="text-xs text-gray-500 mt-0.5">Priests, Deacons, and Religious personnel assigned in the Archdiocese of Kigali</p>
        </div>
        <Button size="sm">
          <Plus className="w-4 h-4 mr-1.5" /> Register Clergy
        </Button>
      </div>

      <Card>
        <Table
          columns={columns}
          data={clergyQuery.data || []}
          isLoading={clergyQuery.isLoading}
          emptyMessage={clergyQuery.isError ? 'Unable to load clergy records from the API.' : 'No clergy records found.'}
        />
      </Card>
    </div>
  );
};
