import React from 'react';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { PlusCircle } from 'lucide-react';

interface DonationItem {
  id: string;
  receipt_number: string;
  donation_type: string;
  donor_name: string;
  amount: string;
  payment_method: string;
  donation_date: string;
}

export const FinancePage: React.FC = () => {
  const dummyDonations: DonationItem[] = [
    {
      id: '1',
      receipt_number: 'RCP-2026-00123',
      donation_type: 'TITHE',
      donor_name: 'Family Mugisha',
      amount: '50,000 RWF',
      payment_method: 'MoMo',
      donation_date: '2026-08-16',
    },
    {
      id: '2',
      receipt_number: 'RCP-2026-00124',
      donation_type: 'CONSTRUCTION_FUND',
      donor_name: 'Caritas Kigali',
      amount: '250,000 RWF',
      payment_method: 'Bank Transfer',
      donation_date: '2026-08-17',
    },
  ];

  const columns: Column<DonationItem>[] = [
    { header: 'Receipt #', accessor: 'receipt_number' },
    { header: 'Donation Type', accessor: 'donation_type' },
    { header: 'Donor', accessor: 'donor_name' },
    { header: 'Amount', accessor: 'amount' },
    { header: 'Payment Method', accessor: 'payment_method' },
    { header: 'Date', accessor: 'donation_date' },
    { header: 'Status', accessor: () => <Badge variant="success">Recorded</Badge> },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Parish & Archdiocesan Finance</h1>
          <p className="text-xs text-gray-500 mt-0.5">
            Tithes (Amaturo), campaign pledges, receipts and auditable contribution ledger
          </p>
        </div>
        <Button size="sm">
          <PlusCircle className="w-4 h-4 mr-1.5" /> Record Donation
        </Button>
      </div>

      <Card>
        <Table columns={columns} data={dummyDonations} />
      </Card>
    </div>
  );
};
