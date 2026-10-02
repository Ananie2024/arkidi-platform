import React, { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { Input } from '../../components/common/Input';
import { Plus } from 'lucide-react';
import { Ministry, domainApi } from '../../core/api/domain';
import { useActiveParish } from '../../core/hooks/useActiveParish';
import { useAuthStore } from '../../core/store/authStore';

const emptyForm = { name: '', category: 'COMMISSION', patron_saint: '', description: '', leader_name: '', leader_phone: '', meeting_schedule: '' };

export const MinistriesPage: React.FC = () => {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const { activeParishId, isLoading: parishLoading } = useActiveParish();
  const user = useAuthStore((state) => state.user);
  const canManage = ['SUPER_ADMIN', 'ARCHBISHOP', 'VICAR_GENERAL', 'CHANCELLOR', 'PARISH_PRIEST'].includes(user?.role || '');
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState(emptyForm);
  const ministriesQuery = useQuery({
    queryKey: ['ministries', activeParishId],
    queryFn: () => domainApi.listMinistries(activeParishId),
    enabled: Boolean(activeParishId),
  });
  const createMutation = useMutation({
    mutationFn: () => domainApi.createMinistry({ ...form, parish_id: activeParishId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ministries', activeParishId] });
      setForm(emptyForm);
      setError(null);
      setShowForm(false);
    },
    onError: (err: any) => setError(err?.response?.data?.detail || err?.response?.data?.message || err.message || 'Unable to create ministry.'),
  });

  const columns: Column<Ministry>[] = [
    { header: t('ministries.col_ministry'), accessor: 'name' },
    { header: t('ministries.col_category'), accessor: 'category' },
    { header: t('ministries.col_leader'), accessor: (row) => row.leader_name || '-' },
    { header: t('ministries.col_schedule'), accessor: (row) => row.meeting_schedule || '-' },
    { header: t('ministries.col_status'), accessor: (row) => (row.is_active ? <Badge variant="success">{t('ministries.active')}</Badge> : <Badge variant="neutral">{t('ministries.inactive')}</Badge>) },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div><h1 className="text-xl font-bold text-gray-900">{t('ministries.title')}</h1><p className="mt-0.5 text-xs text-gray-500">{t('ministries.subtitle')}</p></div>
        {canManage && <Button size="sm" onClick={() => setShowForm(!showForm)}><Plus className="mr-1 h-4 w-4" />{showForm ? 'Close' : t('ministries.new')}</Button>}
      </div>
      {showForm && <Card title="Register a parish ministry">
        <form className="space-y-4" onSubmit={(e) => { e.preventDefault(); setError(null); createMutation.mutate(); }}>
          {error && <p role="alert" className="rounded border border-red-200 bg-red-50 p-2 text-sm text-red-700">{error}</p>}
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            <Input label="Ministry name" required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
            <label className="text-sm">Category<select className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>{['COMMISSION', 'CHOIR', 'ECCLESIAL_MOVEMENT', 'COUNCIL', 'YOUTH_GUILD'].map((category) => <option key={category}>{category}</option>)}</select></label>
            <Input label="Patron saint" value={form.patron_saint} onChange={(e) => setForm({ ...form, patron_saint: e.target.value })} />
            <Input label="Leader" value={form.leader_name} onChange={(e) => setForm({ ...form, leader_name: e.target.value })} />
            <Input label="Leader phone" value={form.leader_phone} onChange={(e) => setForm({ ...form, leader_phone: e.target.value })} />
            <Input label="Meeting schedule" placeholder="First Saturday, 09:00" value={form.meeting_schedule} onChange={(e) => setForm({ ...form, meeting_schedule: e.target.value })} />
          </div>
          <Input label="Description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          <div className="flex justify-end"><Button type="submit" size="sm" disabled={!activeParishId || createMutation.isPending}>{createMutation.isPending ? 'Saving…' : 'Save ministry'}</Button></div>
        </form>
      </Card>}
      <Card><Table columns={columns} data={Array.isArray(ministriesQuery.data) ? ministriesQuery.data : []} isLoading={parishLoading || ministriesQuery.isLoading} emptyMessage={ministriesQuery.isError ? t('ministries.empty_error') : t('ministries.empty_none')} /></Card>
    </div>
  );
};
