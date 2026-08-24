import React from 'react';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { Plus } from 'lucide-react';
import { BaptismRecord } from '../../core/types/sacrament.types';

export const BaptismRegisterPage: React.FC = () => {

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
        <Table columns={columns} data={[]} emptyMessage="No register list endpoint is available yet." />
      </Card>
    </div>
  );
};

