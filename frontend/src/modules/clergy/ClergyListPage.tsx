import React, { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { Plus } from 'lucide-react';
import { Priest, domainApi } from '../../core/api/domain';
import { Input } from '../../components/common/Input';
import { useActiveParish } from '../../core/hooks/useActiveParish';
import { useAuthStore } from '../../core/store/authStore';

export const ClergyListPage: React.FC = () => {
  const { t } = useTranslation();
  const client = useQueryClient();
  const { activeParishId } = useActiveParish();
  const role = useAuthStore((state) => state.user?.role || '');
  const canRegister = ['SUPER_ADMIN', 'ARCHBISHOP', 'VICAR_GENERAL', 'CHANCELLOR'].includes(role);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({ first_name: '', last_name: '', title: 'Padiri', clergy_type: 'DIOCESAN_PRIEST', ordination_date: '', congregation: '', current_role: '' });
  const clergyQuery = useQuery({
    queryKey: ['priests', activeParishId],
    queryFn: () => domainApi.listPriests(activeParishId),
    enabled: Boolean(activeParishId),
  });
  const createMutation = useMutation({
    mutationFn: () => domainApi.createPriest({ ...form, current_parish_id: activeParishId, ordination_date: form.ordination_date || null, congregation: form.congregation || null, current_role: form.current_role || null }),
    onSuccess: () => { setError(null); setShowForm(false); setForm({ first_name: '', last_name: '', title: 'Padiri', clergy_type: 'DIOCESAN_PRIEST', ordination_date: '', congregation: '', current_role: '' }); client.invalidateQueries({ queryKey: ['priests', activeParishId] }); },
    onError: (err: any) => setError(err?.response?.data?.detail || err?.response?.data?.message || 'Unable to register clergy profile.'),
  });

  const columns: Column<Priest>[] = [
    {
      header: t('clergy.col_name_title'),
      accessor: (row) => (
        <div>
          <span className="text-xs text-brand-600 font-semibold">{row.title} </span>
          <span className="text-sm font-medium text-gray-900">{row.last_name} {row.first_name}</span>
        </div>
      ),
    },
    { header: t('clergy.col_role'), accessor: (row) => row.current_role || '-' },
    { header: t('clergy.col_assignment'), accessor: (row) => row.current_parish_id || '-' },
    { header: t('clergy.col_ordination'), accessor: (row) => row.ordination_date || '-' },
    { header: t('clergy.col_status'), accessor: (row) => <Badge variant={row.status === 'ACTIVE_DUTY' ? 'success' : 'neutral'}>{row.status}</Badge> },
    {
      header: t('common.actions'),
      accessor: (row) => (
        <a href={`/clergy/${row.id}`} className="text-brand-500 hover:text-brand-600 font-medium text-xs">
          {t('clergy.view_dossier')}
        </a>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">{t('clergy.title')}</h1>
          <p className="text-xs text-gray-500 mt-0.5">{t('clergy.subtitle')}</p>
        </div>
        {canRegister && <Button size="sm" onClick={() => setShowForm(!showForm)}>
          <Plus className="w-4 h-4 mr-1.5" /> {t('clergy.register')}
        </Button>}
      </div>

      {showForm && <Card title="Register clergy profile"><form className="space-y-3" onSubmit={(e) => { e.preventDefault(); setError(null); createMutation.mutate(); }}>
        {error && <p role="alert" className="text-sm text-red-600">{error}</p>}
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3"><Input label="First name" required value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} /><Input label="Last name" required value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} /><Input label="Title" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} /><label className="block text-sm">Clergy type<select className="mt-1 w-full rounded-lg border px-3 py-2" value={form.clergy_type} onChange={(e) => setForm({ ...form, clergy_type: e.target.value })}>{['DIOCESAN_PRIEST', 'RELIGIOUS_PRIEST', 'BISHOP', 'PERMANENT_DEACON', 'TRANSITIONAL_DEACON', 'RELIGIOUS_BROTHER', 'RELIGIOUS_SISTER', 'SEMINARIAN'].map((x) => <option key={x}>{x}</option>)}</select></label><Input label="Ordination date" type="date" value={form.ordination_date} onChange={(e) => setForm({ ...form, ordination_date: e.target.value })} /><Input label="Congregation" value={form.congregation} onChange={(e) => setForm({ ...form, congregation: e.target.value })} /><Input label="Current role" placeholder="Parish priest" value={form.current_role} onChange={(e) => setForm({ ...form, current_role: e.target.value })} /></div>
        <div className="flex justify-end"><Button size="sm" type="submit" disabled={!activeParishId || createMutation.isPending}>Save profile</Button></div>
      </form></Card>}

      <Card>
        <Table
          columns={columns}
          data={clergyQuery.data || []}
          isLoading={clergyQuery.isLoading}
          emptyMessage={clergyQuery.isError ? t('clergy.empty_error') : t('clergy.empty_none')}
        />
      </Card>
    </div>
  );
};
