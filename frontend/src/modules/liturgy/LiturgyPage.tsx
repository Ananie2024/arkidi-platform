import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { CalendarPlus } from 'lucide-react';
import { MassSchedule, domainApi } from '../../core/api/domain';

export const LiturgyPage: React.FC = () => {
  const parishesQuery = useQuery({ queryKey: ['parishes'], queryFn: () => domainApi.listParishes() });
  const parishId = parishesQuery.data?.[0]?.id;
  const massesQuery = useQuery({
    queryKey: ['mass-schedules', parishId],
    queryFn: () => domainApi.listMassSchedules(parishId as string),
    enabled: Boolean(parishId),
  });

  const columns: Column<MassSchedule>[] = [
    { header: 'Mass Date', accessor: 'mass_date' },
    { header: 'Start Time', accessor: 'start_time' },
    { header: 'Language', accessor: 'language' },
    { header: 'Celebrant', accessor: (row) => row.celebrant_name || '-' },
    { header: 'Liturgical Feast', accessor: (row) => row.liturgical_feast || '-' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Mass Schedules & Intentions</h1>
          <p className="text-xs text-gray-500 mt-0.5">Mass scheduling across centrales and the parish mass intentions ledger</p>
        </div>
        <Button size="sm">
          <CalendarPlus className="w-4 h-4 mr-1.5" /> Schedule Mass
        </Button>
      </div>

      <Card>
        <Table
          columns={columns}
          data={massesQuery.data || []}
          isLoading={parishesQuery.isLoading || massesQuery.isLoading}
          emptyMessage={parishesQuery.isError || massesQuery.isError ? 'Unable to load mass schedules from the API.' : 'No mass schedules found for the current parish.'}
        />
      </Card>
    </div>
  );
};
