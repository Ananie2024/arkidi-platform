import React from 'react';
import { useParams } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { useState } from 'react';
import { Card } from '../../components/common/Card';
import { Badge } from '../../components/common/Badge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { Input } from '../../components/common/Input';
import { Button } from '../../components/common/Button';
import { domainApi } from '../../core/api/domain';
import { useActiveParish } from '../../core/hooks/useActiveParish';
import { useAuthStore } from '../../core/store/authStore';

export const ClergyDetailPage: React.FC = () => {
  const { t } = useTranslation();
  const { clergyId } = useParams<{ clergyId: string }>();
  const queryClient = useQueryClient();
  const { activeParishId } = useActiveParish();
  const role = useAuthStore((state) => state.user?.role || '');
  const canAppoint = ['SUPER_ADMIN', 'ARCHBISHOP', 'VICAR_GENERAL', 'CHANCELLOR'].includes(role);
  const [form, setForm] = useState({ role_title: '', start_date: new Date().toISOString().slice(0, 10), end_date: '', decree_reference_number: '' });
  const [assignmentError, setAssignmentError] = useState<string | null>(null);

  const priestQuery = useQuery({
    queryKey: ['priest', clergyId],
    queryFn: () => domainApi.getPriest(clergyId as string),
    enabled: !!clergyId,
  });
  const assignmentsQuery = useQuery({ queryKey: ['priest-assignments', clergyId], queryFn: () => domainApi.listPriestAssignments(clergyId as string), enabled: Boolean(clergyId) });
  const assignmentMutation = useMutation({
    mutationFn: () => domainApi.createPriestAssignment({ ...form, priest_id: clergyId, parish_id: activeParishId, end_date: form.end_date || null, decree_reference_number: form.decree_reference_number || null, is_current: !form.end_date }),
    onSuccess: () => { setAssignmentError(null); setForm({ role_title: '', start_date: new Date().toISOString().slice(0, 10), end_date: '', decree_reference_number: '' }); queryClient.invalidateQueries({ queryKey: ['priest-assignments', clergyId] }); },
    onError: (err: any) => setAssignmentError(err?.response?.data?.detail || err?.response?.data?.message || 'Unable to record appointment.'),
  });

  if (priestQuery.isLoading) {
    return <LoadingSpinner className="py-20" />;
  }

  if (priestQuery.isError || !priestQuery.data) {
    return (
      <div className="text-sm text-gray-500 py-20 text-center">
        {t('clergy.detail_load_error')}
      </div>
    );
  }

  const priest = priestQuery.data;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{priest.title} {priest.last_name} {priest.first_name}</h1>
          <p className="text-xs text-gray-500 mt-0.5">{priest.current_role || priest.clergy_type}</p>
        </div>
        <Badge variant={priest.status === 'ACTIVE_DUTY' ? 'success' : 'neutral'}>{priest.status}</Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card title={t('clergy.bio_title')}>
          <div className="space-y-3 text-xs">
            <div><span className="font-semibold text-gray-700">{t('clergy.bio_clergy_type')}</span> {priest.clergy_type}</div>
            <div><span className="font-semibold text-gray-700">{t('clergy.bio_ordination_date')}</span> {priest.ordination_date || '-'}</div>
            <div><span className="font-semibold text-gray-700">{t('clergy.bio_ordaining_bishop')}</span> {priest.ordaining_bishop || '-'}</div>
            <div><span className="font-semibold text-gray-700">{t('clergy.bio_congregation')}</span> {priest.congregation || '-'}</div>
            <div><span className="font-semibold text-gray-700">{t('clergy.bio_phone')}</span> {priest.phone_number || '-'}</div>
            <div><span className="font-semibold text-gray-700">{t('clergy.bio_email')}</span> {priest.email || '-'}</div>
          </div>
        </Card>

        <Card title={t('clergy.assignment_title')}>
          <div className="space-y-2 text-xs">
            <div className="p-2.5 bg-gray-50 rounded border border-gray-100">
              <div className="font-semibold text-gray-800">{priest.current_role || '-'}</div>
              <div className="text-gray-500">{t('clergy.assignment_parish')} {priest.current_parish_id || '-'}</div>
            </div>
            {priest.biography && (
              <div className="p-2.5 bg-gray-50 rounded border border-gray-100">
                <div className="font-semibold text-gray-800">{t('clergy.assignment_biography')}</div>
                <div className="text-gray-500 mt-1">{priest.biography}</div>
              </div>
            )}
          </div>
        </Card>
      </div>

      <Card title="Appointment and assignment history">
        {canAppoint && <form className="mb-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4" onSubmit={(e) => { e.preventDefault(); setAssignmentError(null); assignmentMutation.mutate(); }}>
          {assignmentError && <p role="alert" className="sm:col-span-2 lg:col-span-4 text-sm text-red-600">{assignmentError}</p>}
          <Input label="Role / appointment" required value={form.role_title} onChange={(e) => setForm({ ...form, role_title: e.target.value })} />
          <Input label="Start date" type="date" required value={form.start_date} onChange={(e) => setForm({ ...form, start_date: e.target.value })} />
          <Input label="End date (leave empty for current)" type="date" value={form.end_date} onChange={(e) => setForm({ ...form, end_date: e.target.value })} />
          <Input label="Decree reference" value={form.decree_reference_number} onChange={(e) => setForm({ ...form, decree_reference_number: e.target.value })} />
          <div className="sm:col-span-2 lg:col-span-4"><Button size="sm" type="submit" disabled={!activeParishId || assignmentMutation.isPending}>Record appointment</Button></div>
        </form>}
        {assignmentsQuery.isLoading ? <p className="text-sm text-gray-500">Loading appointments…</p> : assignmentsQuery.isError ? <p className="text-sm text-red-600">Unable to load assignment history.</p> : <div className="space-y-2">{assignmentsQuery.data?.map((assignment) => <div key={assignment.id} className="flex flex-wrap items-center justify-between gap-2 rounded border p-3 text-sm"><div><strong>{assignment.role_title}</strong><p className="text-xs text-gray-500">{assignment.start_date} – {assignment.end_date || 'Present'}{assignment.decree_reference_number ? ` · Decree ${assignment.decree_reference_number}` : ''}</p></div><Badge variant={assignment.is_current ? 'success' : 'neutral'}>{assignment.is_current ? 'Current' : 'Past'}</Badge></div>)}{!assignmentsQuery.data?.length && <p className="text-sm text-gray-500">No appointment history recorded.</p>}</div>}
      </Card>
    </div>
  );
};
