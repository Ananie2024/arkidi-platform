import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Card } from '../../components/common/Card';
import { Badge } from '../../components/common/Badge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { domainApi } from '../../core/api/domain';
import { useAuthContext } from '../../core/auth/AuthContext';

export const FaithfulDetailPage: React.FC = () => {
  const { t } = useTranslation();
  const { faithfulId } = useParams<{ faithfulId: string }>();
  const queryClient = useQueryClient();
  const { hasRole } = useAuthContext();
  const canEdit = hasRole(['PARISH_SECRETARY']);
  const [edit, setEdit] = useState(false);
  const [form, setForm] = useState({ first_name: '', last_name: '', christian_name: '', phone_number: '', email: '', family_id: '', family_role: 'HEAD' });

  const faithfulQuery = useQuery({
    queryKey: ['faithful', faithfulId],
    queryFn: () => domainApi.getFaithful(faithfulId as string),
    enabled: !!faithfulId,
  });
  const familiesQuery = useQuery({
    queryKey: ['families', faithfulQuery.data?.parish_id],
    queryFn: () => domainApi.listFamilies(faithfulQuery.data!.parish_id),
    enabled: Boolean(faithfulQuery.data?.parish_id && canEdit),
  });
  const updateMutation = useMutation({
    mutationFn: () => domainApi.updateFaithful(faithfulId as string, {
      ...form,
      family_id: form.family_id || null,
    }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['faithful', faithfulId] });
      await queryClient.invalidateQueries({ queryKey: ['faithful'] });
      setEdit(false);
    },
  });
  useEffect(() => {
    if (faithfulQuery.data) {
      const f = faithfulQuery.data;
      setForm({ first_name: f.first_name, last_name: f.last_name, christian_name: f.christian_name, phone_number: f.phone_number || '', email: f.email || '', family_id: f.family_id || '', family_role: f.family_role || 'HEAD' });
    }
  }, [faithfulQuery.data]);

  if (faithfulQuery.isLoading) {
    return <LoadingSpinner className="py-20" />;
  }

  if (faithfulQuery.isError || !faithfulQuery.data) {
    return (
      <div className="text-sm text-gray-500 py-20 text-center">
        {t('faithful.detail_load_error')}
      </div>
    );
  }

  const f = faithfulQuery.data;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{f.last_name} {f.first_name}</h1>
          <p className="text-xs text-gray-500 mt-0.5">{t('faithful.registration_number')} {f.registration_number}</p>
        </div>
        <Badge variant="success">{f.canonical_status}</Badge>
        {canEdit && <button type="button" className="rounded border px-3 py-1 text-sm" onClick={() => setEdit((value) => !value)}>{edit ? t('common.cancel', 'Cancel') : t('common.edit', 'Edit')}</button>}
      </div>

      {edit && <Card title={t('faithful.edit_title', 'Update parishioner')}>
        <form className="grid gap-3 sm:grid-cols-2" onSubmit={(event) => { event.preventDefault(); updateMutation.mutate(); }}>
          {([['first_name', t('faithful.create_first_name', 'First name')], ['last_name', t('faithful.create_last_name', 'Last name')], ['christian_name', t('faithful.christian_name', 'Baptismal name')], ['phone_number', t('faithful.phone', 'Phone')], ['email', t('faithful.email', 'Email')]] as const).map(([key, label]) => <label key={key} className="text-sm text-gray-700">{label}<input className="mt-1 w-full rounded border px-3 py-2" value={form[key]} onChange={(event) => setForm({ ...form, [key]: event.target.value })} /></label>)}
          <label className="text-sm text-gray-700">{t('faithful.family_id', 'Family')}
            <select className="mt-1 w-full rounded border px-3 py-2" value={form.family_id} onChange={(event) => setForm({ ...form, family_id: event.target.value })}>
              <option value="">{t('faithful.no_family', 'No family assigned')}</option>
              {(familiesQuery.data || []).map((family) => <option key={family.id} value={family.id}>{family.family_code} · {family.family_name}</option>)}
            </select>
          </label>
          <label className="text-sm text-gray-700">{t('faithful.family_role', 'Household role')}
            <select className="mt-1 w-full rounded border px-3 py-2" value={form.family_role} onChange={(event) => setForm({ ...form, family_role: event.target.value })}>
              {['HEAD', 'SPOUSE', 'CHILD', 'DEPENDENT', 'OTHER'].map((role) => <option key={role} value={role}>{t(`faithful.family_role_${role.toLowerCase()}`, role.toLowerCase().replace('_', ' '))}</option>)}
            </select>
          </label>
          {familiesQuery.isError && <p role="alert" className="text-sm text-red-700">{t('faithful.families_load_error', 'Unable to load parish families.')}</p>}
          {updateMutation.isError && <p role="alert" className="text-sm text-red-700">{t('faithful.update_error', 'Unable to update parishioner.')}</p>}
          <div className="sm:col-span-2 flex justify-end"><button disabled={updateMutation.isPending} className="rounded bg-brand-600 px-4 py-2 text-sm text-white disabled:opacity-50">{updateMutation.isPending ? t('common.saving', 'Saving...') : t('common.save', 'Save changes')}</button></div>
        </form>
      </Card>}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card title={t('faithful.personal_title')}>
          <div className="space-y-3 text-xs">
            <div><span className="font-semibold text-gray-700">{t('faithful.christian_name')}</span> {f.christian_name || '-'}</div>
            <div><span className="font-semibold text-gray-700">{t('faithful.gender_label')}</span> {f.gender}</div>
            <div><span className="font-semibold text-gray-700">{t('faithful.birth_date')}</span> {f.date_of_birth || '-'}</div>
            <div><span className="font-semibold text-gray-700">{t('faithful.birth_place')}</span> {f.place_of_birth || '-'}</div>
            <div><span className="font-semibold text-gray-700">{t('faithful.phone')}</span> {f.phone_number || '-'}</div>
            <div><span className="font-semibold text-gray-700">{t('faithful.email')}</span> {f.email || '-'}</div>
          </div>
        </Card>

        <Card title={t('faithful.parish_title')}>
          <div className="space-y-3 text-xs">
            <div><span className="font-semibold text-gray-700">{t('faithful.parish_id')}</span> {f.parish_id}</div>
            <div><span className="font-semibold text-gray-700">{t('faithful.family_id')}</span> {f.family_id || '-'}</div>
            <div><span className="font-semibold text-gray-700">{t('faithful.scc_id')}</span> {f.scc_id || '-'}</div>
            <div><span className="font-semibold text-gray-700">{t('faithful.registered')}</span> {f.created_at ? new Date(f.created_at).toLocaleDateString() : '-'}</div>
          </div>
        </Card>

        <Card title={t('faithful.canonical_title')}>
          <div className="space-y-2 text-xs">
            <div className="flex items-center gap-2 p-2 bg-emerald-50 text-emerald-800 rounded">
              {t('faithful.canonical_status')} {f.canonical_status}
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};
