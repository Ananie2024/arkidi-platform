import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { Search, UserPlus } from 'lucide-react';
import { Faithful, CanonicalStatus } from '../../core/types/faithful.types';
import { domainApi } from '../../core/api/domain';
import { FaithfulCreateModal } from './FaithfulCreateModal';

export const FaithfulListPage: React.FC = () => {
  const { t } = useTranslation();
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const faithfulQuery = useQuery({
    queryKey: ['faithful', searchQuery],
    queryFn: () => domainApi.listFaithful(searchQuery || undefined),
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
        <Button size="sm" onClick={() => setIsCreateOpen(true)}>
          <UserPlus className="w-4 h-4 mr-1.5" /> {t('faithful.register')}
        </Button>
      </div>

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

      <FaithfulCreateModal isOpen={isCreateOpen} onClose={() => setIsCreateOpen(false)} />
    </div>
  );
};
