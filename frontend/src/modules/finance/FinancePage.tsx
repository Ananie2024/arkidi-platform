import React, { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { Input } from '../../components/common/Input';
import { PlusCircle } from 'lucide-react';
import { Donation, domainApi } from '../../core/api/domain';
import { useActiveParish } from '../../core/hooks/useActiveParish';

const today = new Date().toISOString().slice(0, 10);
const monthStart = `${today.slice(0, 8)}01`;

export const FinancePage: React.FC = () => {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const { activeParishId, isLoading: parishesLoading, isError: parishesError } = useActiveParish();
  const [startDate, setStartDate] = useState(monthStart);
  const [endDate, setEndDate] = useState(today);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({ donation_type: 'TITHE', payment_method: 'CASH', amount: '', donation_date: today, donor_name_override: '', reference_transaction_id: '', notes: '' });
  const dateRangeInvalid = startDate > endDate;
  const queryKey = ['donations', activeParishId, startDate, endDate];
  const donationsQuery = useQuery({
    queryKey,
    queryFn: () => domainApi.listDonations(activeParishId as string, startDate, endDate),
    enabled: Boolean(activeParishId && !dateRangeInvalid),
  });
  const summaryQuery = useQuery({
    queryKey: ['finance-summary', activeParishId, startDate, endDate],
    queryFn: () => domainApi.getFinancialSummary(activeParishId as string, startDate, endDate),
    enabled: Boolean(activeParishId && !dateRangeInvalid),
  });
  const reconciliationQuery = useQuery({
    queryKey: ['finance-reconciliation', activeParishId, startDate, endDate],
    queryFn: () => domainApi.getFinanceReconciliation(activeParishId as string, startDate, endDate),
    enabled: Boolean(activeParishId && !dateRangeInvalid),
  });
  const recordMutation = useMutation({
    mutationFn: () => domainApi.createDonation({ ...form, amount: Number(form.amount), currency: 'RWF', parish_id: activeParishId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['donations', activeParishId] });
      queryClient.invalidateQueries({ queryKey: ['finance-summary', activeParishId] });
      queryClient.invalidateQueries({ queryKey: ['finance-reconciliation', activeParishId] });
      setShowForm(false);
      setError(null);
      setForm({ donation_type: 'TITHE', payment_method: 'CASH', amount: '', donation_date: today, donor_name_override: '', reference_transaction_id: '', notes: '' });
    },
    onError: (err: any) => setError(err?.response?.data?.detail || err?.response?.data?.message || err.message || 'Unable to record receipt.'),
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

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!activeParishId || Number(form.amount) <= 0) {
      setError('Select an active parish and enter an amount greater than zero.');
      return;
    }
    recordMutation.mutate();
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold text-gray-900">{t('finance.title')}</h1>
          <p className="text-xs text-gray-500 mt-0.5">{t('finance.subtitle')}</p>
        </div>
        <Button size="sm" onClick={() => setShowForm(!showForm)}>
          <PlusCircle className="w-4 h-4 mr-1.5" /> {showForm ? 'Close' : t('finance.record')}
        </Button>
      </div>

      {showForm && <Card><form onSubmit={submit} className="space-y-4">
        <h2 className="font-semibold text-gray-900">Record donation and issue receipt</h2>
        {error && <p role="alert" className="rounded border border-red-200 bg-red-50 p-2 text-sm text-red-700">{error}</p>}
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          <label className="text-sm">Donation type<select className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2" value={form.donation_type} onChange={(e) => setForm({ ...form, donation_type: e.target.value })}>{['TITHE', 'OFFERTORY', 'CONSTRUCTION_FUND', 'CARITAS_POOR', 'SPECIAL_COLLECTION', 'MASS_STIPEND'].map((x) => <option key={x}>{x}</option>)}</select></label>
          <label className="text-sm">Payment method<select className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2" value={form.payment_method} onChange={(e) => setForm({ ...form, payment_method: e.target.value })}>{['CASH', 'MOMO', 'BANK_TRANSFER', 'CHECK'].map((x) => <option key={x}>{x}</option>)}</select></label>
          <Input label="Amount (RWF)" type="number" min="0.01" step="0.01" required value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} />
          <Input label="Received on" type="date" required value={form.donation_date} onChange={(e) => setForm({ ...form, donation_date: e.target.value })} />
          <Input label="Donor name (optional)" value={form.donor_name_override} onChange={(e) => setForm({ ...form, donor_name_override: e.target.value })} />
          <Input label="External transaction reference" value={form.reference_transaction_id} onChange={(e) => setForm({ ...form, reference_transaction_id: e.target.value })} />
        </div>
        <Input label="Notes (optional)" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
        <div className="flex justify-end"><Button type="submit" size="sm" disabled={recordMutation.isPending}>{recordMutation.isPending ? 'Saving…' : 'Record and issue receipt'}</Button></div>
      </form></Card>}

      <Card>
        <div className="mb-4 flex flex-wrap items-end gap-3">
          <Input label="From" type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
          <Input label="Through" type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
          {dateRangeInvalid && <p className="pb-2 text-sm text-red-600">Start date must be on or before end date.</p>}
        </div>
        <div className="mb-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {[
            ['Tithes', summaryQuery.data?.total_tithes], ['Offertory', summaryQuery.data?.total_offertory],
            ['Construction fund', summaryQuery.data?.total_construction], ['Total receipts', summaryQuery.data?.grand_total],
          ].map(([label, value]) => <div key={String(label)} className="rounded-lg border border-gray-200 p-3"><p className="text-xs text-gray-500">{label}</p><p className="mt-1 font-semibold">{Number(value || 0).toLocaleString()} RWF</p></div>)}
        </div>
        <h2 className="mb-2 text-sm font-semibold text-gray-800">Reconciliation by payment method</h2>
        <div className="mb-5 grid gap-2 sm:grid-cols-2 lg:grid-cols-4">{reconciliationQuery.data?.map((row) => <div key={row.payment_method} className="rounded-lg bg-gray-50 p-3 text-sm"><div className="font-medium">{row.payment_method}</div><div>{row.transaction_count} receipts · {row.total_amount.toLocaleString()} RWF</div></div>)}</div>
        <Table columns={columns} data={donationsQuery.data || []} isLoading={parishesLoading || donationsQuery.isLoading} emptyMessage={parishesError || donationsQuery.isError ? t('finance.empty_error') : t('finance.empty_none')} />
      </Card>
    </div>
  );
};
