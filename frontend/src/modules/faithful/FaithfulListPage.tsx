import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { Search, UserPlus } from 'lucide-react';
import { Faithful, CanonicalStatus } from '../../core/types/faithful.types';
import { domainApi } from '../../core/api/domain';
import { FaithfulCreateModal } from './FaithfulCreateModal';

export const FaithfulListPage: React.FC = () => {
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const faithfulQuery = useQuery({
    queryKey: ['faithful', searchQuery],
    queryFn: () => domainApi.listFaithful(searchQuery || undefined),
  });

  const getStatusBadge = (status: CanonicalStatus) => {
    switch (status) {
      case 'CANONICAL_MARRIAGE':
        return <Badge variant="success">Canonical Marriage</Badge>;
      case 'CONFIRMED':
        return <Badge variant="info">Confirmed</Badge>;
      case 'BAPTIZED':
        return <Badge variant="neutral">Baptized</Badge>;
      default:
        return <Badge>{status}</Badge>;
    }
  };

  const columns: Column<Faithful>[] = [
    { header: 'Reg Number', accessor: 'registration_number' },
    {
      header: 'Full Name',
      accessor: (row) => (
        <div>
          <div className="font-semibold text-gray-900">{row.last_name} {row.first_name}</div>
          <div className="text-[11px] text-gray-500">Christian: {row.christian_name}</div>
        </div>
      ),
    },
    { header: 'Gender', accessor: 'gender' },
    { header: 'Phone Number', accessor: (row) => row.phone_number || '-' },
    { header: 'Canonical Status', accessor: (row) => getStatusBadge(row.canonical_status) },
    {
      header: 'Actions',
      accessor: (row) => (
        <a href={`/faithful/${row.id}`} className="text-brand-500 hover:text-brand-600 font-medium text-xs">
          View Profile &rarr;
        </a>
      ),
    },
  ];

  const emptyMessage = faithfulQuery.isError
    ? 'Unable to load faithful records from the API.'
    : 'No faithful records found.';

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Faithful Directory (Abakristu)</h1>
          <p className="text-xs text-gray-500 mt-0.5">Parishioner registration records, households and canonical status</p>
        </div>
        <Button size="sm" onClick={() => setIsCreateOpen(true)}>
          <UserPlus className="w-4 h-4 mr-1.5" /> Register Faithful
        </Button>
      </div>

      <div className="flex items-center gap-3 bg-white p-3 rounded-xl border border-gray-200 shadow-sm">
        <Search className="w-4 h-4 text-gray-400 ml-1" />
        <input
          type="text"
          placeholder="Search by name, registration code, or NID..."
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
