import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { PlusCircle } from 'lucide-react';
import { Donation, domainApi } from '../../core/api/domain';
import { useActiveParish } from '../../core/hooks/useActiveParish';

export const FinancePage: React.FC = () => {
  const { t } = useTranslation();
  const { activeParishId, isLoading: parishesLoading, isError: parishesError } = useActiveParish();
  const donationsQuery = useQuery({
    queryKey: ['donations', activeParishId],
    queryFn: () => domainApi.listDonations(activeParishId as string),
    enabled: Boolean(activeParishId),
  });

  const columns: Column<Donation>[] = [
    { header: t('finance.col_receipt'), accessor: 'receipt_number' },
    { header: t('finance.col_type'), accessor: 'donation_type' },
    { header: t('finance.col_donor'), accessor: (row) => row.donor_name_override || '-' },
    { header: t('finance.col_amount'), accessor: (row) => `${row.amount.toLocaleString()} ${row.currency}` },
    { header: t('finance.col_payment_method'), accessor: 'payment_method' },
    { header: t('finance.col_date'), accessor: 'donation_date' },
    { header: t('finance.col_status'), accessor: () => <Badge variant="success">{t('finance.status_recorded')}</Badge> },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">{t('finance.title')}</h1>
          <p className="text-xs text-gray-500 mt-0.5">{t('finance.subtitle')}</p>
        </div>
        <Button size="sm">
          <PlusCircle className="w-4 h-4 mr-1.5" /> {t('finance.record')}
        </Button>
      </div>

      <Card>
        <Table
          columns={columns}
          data={donationsQuery.data || []}
          isLoading={parishesLoading || donationsQuery.isLoading}
          emptyMessage={parishesError || donationsQuery.isError ? t('finance.empty_error') : t('finance.empty_none')}
        />
      </Card>
    </div>
  );
};
