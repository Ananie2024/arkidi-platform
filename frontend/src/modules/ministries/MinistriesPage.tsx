import React from 'react';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { Plus } from 'lucide-react';

interface MinistryItem {
  id: string;
  name: string;
  category: string;
  leader_name: string;
  meeting_schedule: string;
  is_active: boolean;
}

export const MinistriesPage: React.FC = () => {
  const dummyMinistries: MinistryItem[] = [
    {
      id: '1',
      name: 'Commission Catéchèse',
      category: 'COMMISSION',
      leader_name: 'Diot. Emmanuel Nkusi',
      meeting_schedule: 'Every Sunday 16:00',
      is_active: true,
    },
    {
      id: '2',
      name: 'Légion de Marie',
      category: 'ECCLESIAL_MOVEMENT',
      leader_name: 'Sr. Marie Goretti',
      meeting_schedule: 'Every Saturday 15:00',
      is_active: true,
    },
  ];

  const columns: Column<MinistryItem>[] = [
    { header: 'Ministry / Commission', accessor: 'name' },
    { header: 'Category', accessor: 'category' },
    { header: 'Leader', accessor: 'leader_name' },
    { header: 'Meeting Schedule', accessor: 'meeting_schedule' },
    { header: 'Status', accessor: (row) => (row.is_active ? <Badge variant="success">Active</Badge> : <Badge variant="neutral">Inactive</Badge>) },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Pastoral Ministries & Lay Apostolate</h1>
          <p className="text-xs text-gray-500 mt-0.5">
            Pastoral councils, commissions, choirs and Catholic Action movements
          </p>
        </div>
        <Button size="sm">
          <Plus className="w-4 h-4 mr-1.5" /> New Ministry
        </Button>
      </div>

      <Card>
        <Table columns={columns} data={dummyMinistries} />
      </Card>
    </div>
  );
};
