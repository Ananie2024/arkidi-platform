import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { PlusCircle } from 'lucide-react';
import { Donation, domainApi } from '../../core/api/domain';

export const FinancePage: React.FC = () => {
  const parishesQuery = useQuery({ queryKey: ['parishes'], queryFn: () => domainApi.listParishes() });
  const parishId = parishesQuery.data?.[0]?.id;
  const donationsQuery = useQuery({
    queryKey: ['donations', parishId],
    queryFn: () => domainApi.listDonations(parishId as string),
    enabled: Boolean(parishId),
  });

  const columns: Column<Donation>[] = [
    { header: 'Receipt #', accessor: 'receipt_number' },
    { header: 'Donation Type', accessor: 'donation_type' },
    { header: 'Donor', accessor: (row) => row.donor_name_override || '-' },
    { header: 'Amount', accessor: (row) => `${row.amount.toLocaleString()} ${row.currency}` },
    { header: 'Payment Method', accessor: 'payment_method' },
    { header: 'Date', accessor: 'donation_date' },
    { header: 'Status', accessor: () => <Badge variant="success">Recorded</Badge> },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Parish & Archdiocesan Finance</h1>
          <p className="text-xs text-gray-500 mt-0.5">Tithes, campaign pledges, receipts and auditable contribution ledger</p>
        </div>
        <Button size="sm">
          <PlusCircle className="w-4 h-4 mr-1.5" /> Record Donation
        </Button>
      </div>

      <Card>
        <Table
          columns={columns}
          data={donationsQuery.data || []}
          isLoading={parishesQuery.isLoading || donationsQuery.isLoading}
          emptyMessage={parishesQuery.isError || donationsQuery.isError ? 'Unable to load donations from the API.' : 'No donations found for the current parish.'}
        />
      </Card>
    </div>
  );
};
