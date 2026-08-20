import React from 'react';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { Plus } from 'lucide-react';
import { BaptismRecord } from '../../core/types/sacrament.types';

export const BaptismRegisterPage: React.FC = () => {
  const dummyBaptisms: BaptismRecord[] = [
    {
      id: '1',
      parish_id: '1',
      faithful_id: '1',
      registry_year: 2026,
      volume_number: 'Vol 24',
      page_number: 'P. 12',
      act_number: 'Act 045',
      celebration_date: '2026-02-01',
      minister_name: 'Abbé Curé Jean',
      godfather_name: 'Paul Habineza',
      godmother_name: 'Jeanne Mukamana',
      created_at: '2026-02-01',
    },
  ];

  const columns: Column<BaptismRecord>[] = [
    { header: 'Act #', accessor: 'act_number' },
    { header: 'Book / Vol', accessor: (row) => `${row.volume_number}, ${row.page_number}` },
    { header: 'Celebration Date', accessor: 'celebration_date' },
    { header: 'Minister / Priest', accessor: 'minister_name' },
    { header: 'Godfather / Godmother', accessor: (row) => `${row.godfather_name || '-'} / ${row.godmother_name || '-'}` },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Baptism Canonical Register (Registre des Baptêmes)</h1>
          <p className="text-xs text-gray-500 mt-0.5">Official Roman Catholic baptism ledger and entry verification</p>
        </div>
        <Button size="sm">
          <Plus className="w-4 h-4 mr-1.5" /> Record Baptism
        </Button>
      </div>

      <Card>
        <Table columns={columns} data={dummyBaptisms} />
      </Card>
    </div>
  );
};
