import React from 'react';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { Plus } from 'lucide-react';

interface ClergyItem {
  id: string;
  name: string;
  title: string;
  role: string;
  parish: string;
  ordination_date: string;
  status: string;
}

export const ClergyListPage: React.FC = () => {
  const dummyClergy: ClergyItem[] = [
    {
      id: '1',
      name: 'Antoine Cardinal Kambanda',
      title: 'Son Éminence',
      role: 'Archevêque de Kigali',
      parish: 'Archevêché de Kigali',
      ordination_date: '1990-09-08',
      status: 'ACTIVE_DUTY',
    },
    {
      id: '2',
      name: 'Abbé Jean-Marie Vianney',
      title: 'Padiri',
      role: 'Curé de Paroisse',
      parish: 'Sainte Famille',
      ordination_date: '2005-07-16',
      status: 'ACTIVE_DUTY',
    },
  ];

  const columns: Column<ClergyItem>[] = [
    {
      header: 'Clergy Name & Title',
      accessor: (row) => (
        <div>
          <span className="text-xs text-brand-600 font-semibold">{row.title} </span>
          <span className="text-sm font-medium text-gray-900">{row.name}</span>
        </div>
      ),
    },
    { header: 'Current Role', accessor: 'role' },
    { header: 'Current Assignment / Parish', accessor: 'parish' },
    { header: 'Ordination Date', accessor: 'ordination_date' },
    { header: 'Status', accessor: () => <Badge variant="success">Active Duty</Badge> },
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
        <Table columns={columns} data={dummyClergy} />
      </Card>
    </div>
  );
};
