import React from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Card } from '../../components/common/Card';
import { Badge } from '../../components/common/Badge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { domainApi } from '../../core/api/domain';

export const FaithfulDetailPage: React.FC = () => {
  const { faithfulId } = useParams<{ faithfulId: string }>();

  const faithfulQuery = useQuery({
    queryKey: ['faithful', faithfulId],
    queryFn: () => domainApi.getFaithful(faithfulId as string),
    enabled: !!faithfulId,
  });

  if (faithfulQuery.isLoading) {
    return <LoadingSpinner className="py-20" />;
  }

  if (faithfulQuery.isError || !faithfulQuery.data) {
    return (
      <div className="text-sm text-gray-500 py-20 text-center">
        Unable to load the faithful record from the API.
      </div>
    );
  }

  const f = faithfulQuery.data;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{f.last_name} {f.first_name}</h1>
          <p className="text-xs text-gray-500 mt-0.5">Registration Number: {f.registration_number}</p>
        </div>
        <Badge variant="success">{f.canonical_status}</Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card title="Personal & Contact Details">
          <div className="space-y-3 text-xs">
            <div><span className="font-semibold text-gray-700">Christian Name:</span> {f.christian_name || '-'}</div>
            <div><span className="font-semibold text-gray-700">Gender:</span> {f.gender}</div>
            <div><span className="font-semibold text-gray-700">Date of Birth:</span> {f.date_of_birth || '-'}</div>
            <div><span className="font-semibold text-gray-700">Place of Birth:</span> {f.place_of_birth || '-'}</div>
            <div><span className="font-semibold text-gray-700">Phone:</span> {f.phone_number || '-'}</div>
            <div><span className="font-semibold text-gray-700">Email:</span> {f.email || '-'}</div>
          </div>
        </Card>

        <Card title="Parish Registration">
          <div className="space-y-3 text-xs">
            <div><span className="font-semibold text-gray-700">Parish ID:</span> {f.parish_id}</div>
            <div><span className="font-semibold text-gray-700">Family ID:</span> {f.family_id || '-'}</div>
            <div><span className="font-semibold text-gray-700">SCC ID:</span> {f.scc_id || '-'}</div>
            <div><span className="font-semibold text-gray-700">Registered:</span> {f.created_at ? new Date(f.created_at).toLocaleDateString() : '-'}</div>
          </div>
        </Card>

        <Card title="Canonical Status">
          <div className="space-y-2 text-xs">
            <div className="flex items-center gap-2 p-2 bg-emerald-50 text-emerald-800 rounded">
              Status: {f.canonical_status}
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};