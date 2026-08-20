import React from 'react';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { Plus } from 'lucide-react';

interface MatrimonyItem {
  id: string;
  act_number: string;
  celebration_date: string;
  groom_name: string;
  bride_name: string;
  priest_celebrant: string;
}

export const MatrimonyRegisterPage: React.FC = () => {
  const dummyMatrimonies: MatrimonyItem[] = [
    {
      id: '1',
      act_number: 'Act 014',
      celebration_date: '2026-01-10',
      groom_name: 'Jean-Baptiste Mugisha',
      bride_name: 'Marie-Claire Uwase',
      priest_celebrant: 'Abbé Curé',
    },
  ];

  const columns: Column<MatrimonyItem>[] = [
    { header: 'Act #', accessor: 'act_number' },
    { header: 'Date of Marriage', accessor: 'celebration_date' },
    { header: 'Groom (Umugabo)', accessor: 'groom_name' },
    { header: 'Bride (Umugore)', accessor: 'bride_name' },
    { header: 'Celebrant Priest', accessor: 'priest_celebrant' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Canonical Marriage Register (Registre des Mariages)</h1>
          <p className="text-xs text-gray-500 mt-0.5">Catholic marriage ceremonies, banns publication, and canonical witnesses</p>
        </div>
        <Button size="sm">
          <Plus className="w-4 h-4 mr-1.5" /> Record Marriage
        </Button>
      </div>

      <Card>
        <Table columns={columns} data={dummyMatrimonies} />
      </Card>
    </div>
  );
};
