import React from 'react';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { Plus } from 'lucide-react';

interface ParishItem {
  id: string;
  code: string;
  name: string;
  patron_saint: string;
  district: string;
  sector: string;
}

export const ParishListPage: React.FC = () => {
  const dummyParishes: ParishItem[] = [
    { id: '1', code: 'PAR-STM', name: 'Cathédrale Saint Michel', patron_saint: 'Saint Michel Archange', district: 'Nyarugenge', sector: 'Kiyovu' },
    { id: '2', code: 'PAR-STF', name: 'Paroisse Sainte Famille', patron_saint: 'Sainte Famille', district: 'Nyarugenge', sector: 'Muhima' },
    { id: '3', code: 'PAR-RGP', name: 'Paroisse Regina Pacis', patron_saint: 'Regina Pacis', district: 'Gasabo', sector: 'Remera' },
    { id: '4', code: 'PAR-KCK', name: 'Paroisse Saint Joseph', patron_saint: 'Saint Joseph', district: 'Kicukiro', sector: 'Kicukiro' },
  ];

  const columns: Column<ParishItem>[] = [
    { header: 'Parish Code', accessor: 'code' },
    { header: 'Parish Name', accessor: 'name' },
    { header: 'Patron Saint', accessor: 'patron_saint' },
    { header: 'District', accessor: 'district' },
    { header: 'Sector', accessor: 'sector' },
    {
      header: 'Actions',
      accessor: (row) => (
        <a href={`/geography/parishes/${row.id}`} className="text-brand-500 hover:text-brand-600 font-medium text-xs">
          Open Parish Details
        </a>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Parishes of the Archdiocese</h1>
          <p className="text-xs text-gray-500 mt-0.5">Official Catholic parish directory in Kigali and surrounding vicariates</p>
        </div>
        <Button size="sm">
          <Plus className="w-4 h-4 mr-1.5" /> Register New Parish
        </Button>
      </div>

      <Card>
        <Table columns={columns} data={dummyParishes} />
      </Card>
    </div>
  );
};
