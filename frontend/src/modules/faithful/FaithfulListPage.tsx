import React, { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { Search, UserPlus } from 'lucide-react';
import { Faithful, CanonicalStatus } from '../../core/types/faithful.types';
import { domainApi } from '../../core/api/domain';
import { FaithfulCreateModal } from './FaithfulCreateModal';
import { useActiveParish } from '../../core/hooks/useActiveParish';

export const FaithfulListPage: React.FC = () => {
  const { t } = useTranslation();
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isFamilyOpen, setIsFamilyOpen] = useState(false);
  const [selectedFamilyId, setSelectedFamilyId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const { activeParishId } = useActiveParish();
  const queryClient = useQueryClient();
  const familyMutation = useMutation({
    mutationFn: domainApi.createFamily,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['families', activeParishId] });
      setIsFamilyOpen(false);
    },
  });

  const faithfulQuery = useQuery({
    queryKey: ['faithful', activeParishId, searchQuery],
    queryFn: () => domainApi.listFaithful(searchQuery || undefined, activeParishId || undefined),
    enabled: Boolean(activeParishId),
  });
  const familiesQuery = useQuery({
    queryKey: ['families', activeParishId],
    queryFn: () => domainApi.listFamilies(activeParishId as string),
    enabled: Boolean(activeParishId),
  });
  const familyMembersQuery = useQuery({
    queryKey: ['family-members', selectedFamilyId],
    queryFn: () => domainApi.listFamilyMembers(selectedFamilyId as string),
    enabled: Boolean(selectedFamilyId),
  });

  const getStatusBadge = (status: CanonicalStatus) => {
    switch (status) {
      case 'CANONICAL_MARRIAGE':
        return <Badge variant="success">{t('faithful.status_canonical_marriage')}</Badge>;
      case 'CONFIRMED':
        return <Badge variant="info">{t('faithful.status_confirmed')}</Badge>;
      case 'BAPTIZED':
        return <Badge variant="neutral">{t('faithful.status_baptized')}</Badge>;
      default:
        return <Badge>{status}</Badge>;
    }
  };

  const columns: Column<Faithful>[] = [
    { header: t('faithful.col_reg_number'), accessor: 'registration_number' },
    {
      header: t('faithful.col_full_name'),
      accessor: (row) => (
        <div>
          <div className="font-semibold text-gray-900">{row.last_name} {row.first_name}</div>
          <div className="text-[11px] text-gray-500">{t('faithful.col_christian')} {row.christian_name}</div>
        </div>
      ),
    },
    { header: t('faithful.col_gender'), accessor: 'gender' },
    { header: t('faithful.col_phone'), accessor: (row) => row.phone_number || '-' },
    { header: t('faithful.col_canonical_status'), accessor: (row) => getStatusBadge(row.canonical_status) },
    {
      header: t('common.actions'),
      accessor: (row) => (
        <a href={`/faithful/${row.id}`} className="text-brand-500 hover:text-brand-600 font-medium text-xs">
          {t('faithful.view_profile')}
        </a>
      ),
    },
  ];

  const emptyMessage = faithfulQuery.isError
    ? t('faithful.empty_error')
    : t('faithful.empty_none');

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-gray-900">{t('faithful.title')}</h1>
          <p className="text-xs text-gray-500 mt-0.5">{t('faithful.subtitle')}</p>
        </div>
        <div className="flex gap-2">
          <Button size="sm" variant="outline" onClick={() => setIsFamilyOpen((value) => !value)} disabled={!activeParishId}>{t('faithful.family_create', 'New family')}</Button>
          <Button size="sm" onClick={() => setIsCreateOpen(true)} disabled={!activeParishId}>
            <UserPlus className="w-4 h-4 mr-1.5" /> {t('faithful.register')}
          </Button>
        </div>
      </div>

      {isFamilyOpen && <Card title={t('faithful.family_create', 'Register family')}>
        <form className="grid gap-3 sm:grid-cols-3" onSubmit={(event) => {
          event.preventDefault();
          if (!activeParishId) return;
          const values = new FormData(event.currentTarget);
          familyMutation.mutate({ parish_id: activeParishId, family_code: values.get('family_code'), family_name: values.get('family_name'), residence_address: values.get('residence_address') || null, phone: values.get('phone') || null });
        }}>
          <input name="family_code" required placeholder={t('faithful.family_code', 'Family code')} className="rounded border px-3 py-2 text-sm" />
          <input name="family_name" required placeholder={t('faithful.family_name', 'Family name')} className="rounded border px-3 py-2 text-sm" />
          <input name="phone" placeholder={t('faithful.phone', 'Phone')} className="rounded border px-3 py-2 text-sm" />
          <input name="residence_address" placeholder={t('faithful.residence_address', 'Residence address')} className="rounded border px-3 py-2 text-sm sm:col-span-2" />
          {familyMutation.isError && <p role="alert" className="text-sm text-red-700">{t('faithful.family_create_error', 'Unable to register family. Check that the family code is unique.')}</p>}
          <div className="flex justify-end"><Button type="submit" disabled={familyMutation.isPending}>{familyMutation.isPending ? t('common.saving', 'Saving...') : t('faithful.family_create', 'Save family')}</Button></div>
        </form>
      </Card>}

      <Card title={t('faithful.families_title', 'Parish households')}>
        {familiesQuery.isError && <p role="alert" className="text-sm text-red-700">{t('faithful.families_load_error', 'Unable to load parish families.')}</p>}
        {familiesQuery.data?.length === 0 && <p className="text-sm text-gray-500">{t('faithful.families_empty', 'No households registered yet.')}</p>}
        <div className="flex flex-wrap gap-2">
          {(familiesQuery.data || []).map((family) => <button key={family.id} type="button" onClick={() => setSelectedFamilyId(selectedFamilyId === family.id ? null : family.id)} className={`rounded border px-3 py-2 text-left text-sm ${selectedFamilyId === family.id ? 'border-brand-500 bg-brand-50' : 'border-gray-200'}`}>
            <span className="font-medium">{family.family_code}</span><span className="ml-2 text-gray-600">{family.family_name}</span>
          </button>)}
        </div>
        {selectedFamilyId && <div className="mt-4 border-t pt-3">
          <h3 className="mb-2 text-sm font-semibold">{t('faithful.family_members', 'Household members')}</h3>
          {familyMembersQuery.isLoading && <p className="text-sm text-gray-500">{t('common.loading', 'Loading...')}</p>}
          {familyMembersQuery.isError && <p role="alert" className="text-sm text-red-700">{t('faithful.family_members_error', 'Unable to load household members.')}</p>}
          {familyMembersQuery.data?.length === 0 && <p className="text-sm text-gray-500">{t('faithful.family_members_empty', 'No parishioners assigned to this household.')}</p>}
          <ul className="divide-y">
            {(familyMembersQuery.data || []).map((member) => <li key={member.id} className="py-2"><a className="text-sm text-brand-700 hover:underline" href={`/faithful/${member.id}`}>{member.last_name} {member.first_name} · {member.registration_number}</a></li>)}
          </ul>
        </div>}
      </Card>

      <div className="flex items-center gap-3 bg-white p-3 rounded-xl border border-gray-200 shadow-sm">
        <Search className="w-4 h-4 text-gray-400 ml-1" />
        <input
          type="text"
          placeholder={t('faithful.search_placeholder')}
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full text-xs text-gray-800 bg-transparent focus:outline-none placeholder-gray-400"
        />
      </div>

      <Card>
        <Table
          columns={columns}
          data={faithfulQuery.data?.items || []}
          isLoading={faithfulQuery.isLoading}
          emptyMessage={emptyMessage}
        />
      </Card>

      <FaithfulCreateModal isOpen={isCreateOpen} onClose={() => setIsCreateOpen(false)} parishId={activeParishId} />
    </div>
  );
};
