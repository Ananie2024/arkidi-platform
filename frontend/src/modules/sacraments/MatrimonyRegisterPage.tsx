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
        <Table columns={columns} data={[]} emptyMessage="No register list endpoint is available yet." />
      </Card>
    </div>
  );
};

