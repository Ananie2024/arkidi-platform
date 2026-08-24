import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { Plus } from 'lucide-react';
import { Ministry, domainApi } from '../../core/api/domain';

export const MinistriesPage: React.FC = () => {
  const ministriesQuery = useQuery({
    queryKey: ['ministries'],
    queryFn: domainApi.listMinistries,
  });

  const columns: Column<Ministry>[] = [
    { header: 'Ministry / Commission', accessor: 'name' },
    { header: 'Category', accessor: 'category' },
    { header: 'Leader', accessor: (row) => row.leader_name || '-' },
    { header: 'Meeting Schedule', accessor: (row) => row.meeting_schedule || '-' },
    { header: 'Status', accessor: (row) => (row.is_active ? <Badge variant="success">Active</Badge> : <Badge variant="neutral">Inactive</Badge>) },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Pastoral Ministries & Lay Apostolate</h1>
          <p className="text-xs text-gray-500 mt-0.5">Pastoral councils, commissions, choirs and Catholic Action movements</p>
        </div>
        <Button size="sm">
          <Plus className="w-4 h-4 mr-1.5" /> New Ministry
        </Button>
      </div>

      <Card>
        <Table
          columns={columns}
          data={ministriesQuery.data || []}
          isLoading={ministriesQuery.isLoading}
          emptyMessage={ministriesQuery.isError ? 'Unable to load ministries from the API.' : 'No ministries found.'}
        />
      </Card>
    </div>
  );
};
