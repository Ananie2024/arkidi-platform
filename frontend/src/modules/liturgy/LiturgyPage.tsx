import React from 'react';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { CalendarPlus } from 'lucide-react';

interface MassScheduleItem {
  id: string;
  date: string;
  start_time: string;
  language: string;
  celebrant_name: string;
  liturgical_feast: string;
}

export const LiturgyPage: React.FC = () => {
  const dummyMasses: MassScheduleItem[] = [
    {
      id: '1',
      date: '2026-08-23',
      start_time: '09:00',
      language: 'Kinyarwanda',
      celebrant_name: 'Abbé Curé Jean',
      liturgical_feast: '21st Sunday in Ordinary Time',
    },
    {
      id: '2',
      date: '2026-08-23',
      start_time: '11:00',
      language: 'French',
      celebrant_name: 'Abbé Vicaire Paul',
      liturgical_feast: '21st Sunday in Ordinary Time',
    },
  ];

  const columns: Column<MassScheduleItem>[] = [
    { header: 'Mass Date', accessor: 'date' },
    { header: 'Start Time', accessor: 'start_time' },
    { header: 'Language', accessor: 'language' },
    { header: 'Celebrant', accessor: 'celebrant_name' },
    { header: 'Liturgical Feast', accessor: 'liturgical_feast' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Mass Schedules & Intentions</h1>
          <p className="text-xs text-gray-500 mt-0.5">
            Mass scheduling across centrales and the parish mass intentions ledger (Ibitambo bya Misa)
          </p>
        </div>
        <Button size="sm">
          <CalendarPlus className="w-4 h-4 mr-1.5" /> Schedule Mass
        </Button>
      </div>

      <Card>
        <Table columns={columns} data={dummyMasses} />
      </Card>
    </div>
  );
};
