import React from 'react';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { Plus } from 'lucide-react';

interface ConfirmationItem {
  id: string;
  act_number: string;
  volume_page: string;
  celebration_date: string;
  administering_bishop: string;
  sponsor_name: string;
}

export const ConfirmationRegisterPage: React.FC = () => {
  const dummyConfirmations: ConfirmationItem[] = [
    {
      id: '1',
      act_number: 'Act 108',
      volume_page: 'Vol 15, P. 40',
      celebration_date: '2025-11-23',
      administering_bishop: 'S.E. Mgr. Antoine Kambanda',
      sponsor_name: 'Claude Ndayisaba',
    },
  ];

  const columns: Column<ConfirmationItem>[] = [
    { header: 'Act #', accessor: 'act_number' },
    { header: 'Registry Location', accessor: 'volume_page' },
    { header: 'Date', accessor: 'celebration_date' },
    { header: 'Administering Bishop / Vicar', accessor: 'administering_bishop' },
    { header: 'Sponsor (Parrain/Marraine)', accessor: 'sponsor_name' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Confirmation Register (Registre des Confirmations)</h1>
          <p className="text-xs text-gray-500 mt-0.5">Records of the sacrament of Confirmation / Gukomezwa</p>
        </div>
        <Button size="sm">
          <Plus className="w-4 h-4 mr-1.5" /> Record Confirmation
        </Button>
      </div>

      <Card>
        <Table columns={columns} data={dummyConfirmations} />
      </Card>
    </div>
  );
};
