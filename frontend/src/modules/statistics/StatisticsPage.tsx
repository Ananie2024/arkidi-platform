import React, { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { Input } from '../../components/common/Input';
import { BarChart3 } from 'lucide-react';
import { AnnualReport, domainApi, IndicatorConfigView } from '../../core/api/domain';
import { useActiveParish } from '../../core/hooks/useActiveParish';
import { useAuthStore } from '../../core/store/authStore';

export const StatisticsPage: React.FC = () => {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const currentYear = new Date().getFullYear();
  const [selectedYear, setSelectedYear] = useState(currentYear);
  const [selectedReport, setSelectedReport] = useState<AnnualReport | null>(null);
  const { activeParishId } = useActiveParish();
  const user = useAuthStore((state) => state.user);
  const canViewAnnuario = !user?.parish_id && !user?.deanery_id;
  const [showReportForm, setShowReportForm] = useState(false);
  const [reportError, setReportError] = useState<string | null>(null);
  const [form, setForm] = useState({
    report_year: String(currentYear), total_catholic_population: '', total_catechumens: '', total_families: '',
    infant_baptisms: '', adult_baptisms: '', first_communions: '', confirmations: '',
    marriages_both_catholic: '', marriages_mixed_religion: '', christian_funerals: '',
    catholic_schools_count: '', students_count: '', health_centers_count: '',
  });
  const reportsQuery = useQuery({
    queryKey: ['annual-reports', selectedYear],
    queryFn: () => domainApi.listAnnualReports(selectedYear),
  });
  const annuarioQuery = useQuery({
    queryKey: ['annuario-pontificio', selectedYear],
    queryFn: () => domainApi.getAnnuarioPontificio(selectedYear),
    enabled: canViewAnnuario,
  });
  const reconciliationQuery = useQuery({
    queryKey: ['annual-report-reconciliation', selectedReport?.parish_id, selectedReport?.report_year],
    queryFn: () => domainApi.reconcileAnnualReport(selectedReport!.parish_id, selectedReport!.report_year),
    enabled: Boolean(selectedReport),
  });
  const indicatorsQuery = useQuery({ queryKey: ['indicator-registry'], queryFn: () => domainApi.listIndicators() });
  const submitMutation = useMutation({
    mutationFn: () => domainApi.submitParishReport({
      parish_id: activeParishId,
      report_year: Number(form.report_year),
      ...Object.fromEntries(Object.entries(form).filter(([key]) => key !== 'report_year').map(([key, value]) => [key, Number(value || 0)])),
    }),
    onSuccess: () => {
      setReportError(null);
      setShowReportForm(false);
      queryClient.invalidateQueries({ queryKey: ['annual-reports'] });
      queryClient.invalidateQueries({ queryKey: ['annuario-pontificio'] });
    },
    onError: (err: any) => setReportError(err?.response?.data?.detail || err?.response?.data?.message || err.message || 'Unable to submit parish return.'),
  });

  const columns: Column<AnnualReport>[] = [
    { header: t('statistics.col_parish_id'), accessor: 'parish_id' },
    { header: t('statistics.col_year'), accessor: 'report_year' },
    { header: t('statistics.col_catholic_population'), accessor: 'total_catholic_population' },
    { header: t('statistics.col_baptisms'), accessor: (row) => row.infant_baptisms + row.adult_baptisms },
    { header: t('statistics.col_confirmations'), accessor: 'confirmations' },
    { header: t('statistics.col_marriages'), accessor: (row) => row.marriages_both_catholic + row.marriages_mixed_religion },
    { header: 'Register check', accessor: (row) => <Button size="sm" variant="outline" onClick={() => setSelectedReport(row)}>Compare</Button> },
  ];
  const numberFields = [
    ['total_catholic_population', 'Catholic population'], ['total_catechumens', 'Catechumens'],
    ['total_families', 'Families'], ['infant_baptisms', 'Infant baptisms'], ['adult_baptisms', 'Adult baptisms'],
    ['first_communions', 'First communions'], ['confirmations', 'Confirmations'],
    ['marriages_both_catholic', 'Marriages, both Catholic'], ['marriages_mixed_religion', 'Mixed religion marriages'],
    ['christian_funerals', 'Christian funerals'], ['catholic_schools_count', 'Catholic schools'],
    ['students_count', 'Students'], ['health_centers_count', 'Health centers'],
  ] as const;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold text-gray-900">{t('statistics.title')}</h1>
          <p className="text-xs text-gray-500 mt-0.5">{t('statistics.subtitle')}</p>
        </div>
        <Button size="sm" onClick={() => setShowReportForm(!showReportForm)}>
          <BarChart3 className="mr-1.5 h-4 w-4" /> {showReportForm ? 'Close' : 'Submit or correct annual return'}
        </Button>
      </div>

      {showReportForm && <Card title="Parish annual statistical return">
        <form className="space-y-4" onSubmit={(event) => { event.preventDefault(); setReportError(null); submitMutation.mutate(); }}>
          <p className="text-xs text-gray-600">Submitting again for the same parish and year updates the existing return. Corrections are recorded in the audit log with changed values.</p>
          {reportError && <p role="alert" className="rounded border border-red-200 bg-red-50 p-2 text-sm text-red-700">{reportError}</p>}
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <Input label="Reporting year" type="number" min="1900" max="2200" required value={form.report_year} onChange={(e) => setForm({ ...form, report_year: e.target.value })} />
            {numberFields.map(([key, label]) => <Input key={key} label={label} type="number" min="0" step="1" value={form[key]} onChange={(e) => setForm({ ...form, [key]: e.target.value })} />)}
          </div>
          <div className="flex justify-end"><Button size="sm" type="submit" disabled={!activeParishId || submitMutation.isPending}>{submitMutation.isPending ? 'Saving…' : 'Save annual return'}</Button></div>
        </form>
      </Card>}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        {canViewAnnuario ? <>
          <Card title={t('statistics.card_parishes')}><div className="text-2xl font-bold text-gray-900">{annuarioQuery.data?.total_parishes ?? '-'}</div></Card>
          <Card title={t('statistics.card_priests')}><div className="text-2xl font-bold text-gray-900">{annuarioQuery.data?.total_priests ?? '-'}</div><p className="mt-1 text-xs text-gray-500">Active duty diocesan and religious priests</p></Card>
          <Card title={t('statistics.card_catholics')}><div className="text-2xl font-bold text-gray-900">{annuarioQuery.data?.total_catholics?.toLocaleString() ?? '-'}</div></Card>
        </> : <Card><p className="text-sm text-gray-600">Annuario Pontificio totals are available to archdiocesan accounts. Parish returns and register reconciliation remain available for your scope.</p></Card>}
      </div>

      <Card title="Indicator definitions">
        <p className="mb-3 text-xs text-gray-600">Definitions show each indicator’s source, reporting period, inclusion rules and aggregation scope.</p>
        {indicatorsQuery.data?.length ? <div className="space-y-2">{indicatorsQuery.data.map((indicator: IndicatorConfigView) => <details key={indicator.key} className="rounded border border-gray-200 p-3">
          <summary className="cursor-pointer text-sm font-semibold text-gray-800">{indicator.title} <span className="ml-1 text-xs font-normal text-gray-500">({indicator.key})</span></summary>
          <div className="mt-2 grid gap-2 text-xs text-gray-600 md:grid-cols-2">
            <p><strong>Definition:</strong> {indicator.description}</p><p><strong>Source:</strong> {indicator.source_model}{indicator.metric_field ? ` · ${indicator.metric_field}` : ''} · {indicator.aggregation}</p>
            <p><strong>Reporting period:</strong> {indicator.period_field || indicator.date_field || 'No fixed period; current records'}</p><p><strong>Aggregation scope:</strong> grouped by {indicator.group_by} · {indicator.scope_mode} scope</p>
            <p className="md:col-span-2"><strong>Inclusion rules:</strong> {indicator.inclusion_rules}</p>
          </div>
        </details>)}</div> : <p className="text-sm text-gray-500">{indicatorsQuery.isLoading ? 'Loading indicator definitions…' : 'Indicator definitions are unavailable.'}</p>}
      </Card>

      {selectedReport && <Card title={`Register reconciliation · ${selectedReport.report_year}`}>
        <div className="mb-3 flex items-center justify-between"><p className="text-xs text-gray-600">Submitted totals are compared with non-deleted register entries dated within the calendar year.</p><Button size="sm" variant="ghost" onClick={() => setSelectedReport(null)}>Close</Button></div>
        {reconciliationQuery.isLoading ? <p className="text-sm text-gray-500">Comparing reported totals…</p> : reconciliationQuery.isError ? <p role="alert" className="text-sm text-red-600">Unable to compare this annual return.</p> : <div className="space-y-2">{reconciliationQuery.data?.map((item) => <div key={item.field} className="flex flex-wrap items-center justify-between gap-2 rounded border border-gray-200 p-3 text-sm"><span className="font-medium capitalize">{item.field.replace(/_/g, ' ')}</span><span>Submitted: {item.submitted_count ?? 'No return'} · Register: {item.register_count} · Difference: {item.difference ?? '—'}</span><strong className={item.status === 'MATCH' ? 'text-green-700' : 'text-amber-700'}>{item.status}</strong></div>)}</div>}
      </Card>}

      <Card title={`Annual parish returns · ${selectedYear}`}>
        <p className="mb-3 text-xs text-gray-600">One current return is shown per parish and year. The latest correction replaces the prior values for reporting.</p>
        <div className="mb-3 max-w-xs"><Input label="Reporting year" type="number" min="1900" max="2200" value={selectedYear} onChange={(e) => setSelectedYear(Number(e.target.value))} /></div>
        <Table columns={columns} data={reportsQuery.data || []} isLoading={reportsQuery.isLoading} emptyMessage={reportsQuery.isError ? t('statistics.empty_error') : t('statistics.empty_none', { year: currentYear })} />
      </Card>
    </div>
  );
};
