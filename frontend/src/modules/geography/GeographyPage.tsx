import React from 'react';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { Plus } from 'lucide-react';

interface DeaneryItem {
  id: string;
  name: string;
  code: string;
  vicar_forane_name: string;
  parishes_count: number;
}

export const GeographyPage: React.FC = () => {
  const dummyDeaneries: DeaneryItem[] = [
    { id: '1', name: 'Doyenné Saint Michel', code: 'DOY-STM', vicar_forane_name: 'Mgr. Vicaire Épiscopal', parishes_count: 8 },
    { id: '2', name: 'Doyenné Sainte Famille', code: 'DOY-STF', vicar_forane_name: 'Abbé Curé Doyen', parishes_count: 9 },
    { id: '3', name: 'Doyenné Kicukiro', code: 'DOY-KCK', vicar_forane_name: 'Abbé Curé Doyen', parishes_count: 9 },
    { id: '4', name: 'Doyenné Nyamata', code: 'DOY-NYM', vicar_forane_name: 'Abbé Curé Doyen', parishes_count: 8 },
  ];

  const columns: Column<DeaneryItem>[] = [
    { header: 'Deanery Code', accessor: 'code' },
    { header: 'Deanery Name (Doyenné)', accessor: 'name' },
    { header: 'Vicar Forane (Doyen)', accessor: 'vicar_forane_name' },
    { header: 'Parishes Count', accessor: 'parishes_count' },
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
        <Table columns={columns} data={dummyDeaneries} />
      </Card>
    </div>
  );
};
