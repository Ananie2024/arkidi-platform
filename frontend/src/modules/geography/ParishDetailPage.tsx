import React from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Card } from '../../components/common/Card';
import { Badge } from '../../components/common/Badge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { domainApi } from '../../core/api/domain';

export const ParishDetailPage: React.FC = () => {
  const { parishId } = useParams<{ parishId: string }>();

  const parishQuery = useQuery({
    queryKey: ['parish', parishId],
    queryFn: () => domainApi.getParish(parishId as string),
    enabled: !!parishId,
  });

  if (parishQuery.isLoading) {
    return <LoadingSpinner className="py-20" />;
  }

  if (parishQuery.isError || !parishQuery.data) {
    return (
      <div className="text-sm text-gray-500 py-20 text-center">
        Unable to load parish details from the API.
      </div>
    );
  }

  const parish = parishQuery.data;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{parish.name}</h1>
          <p className="text-xs text-gray-500 mt-1">Code: {parish.code}</p>
        </div>
        <Badge variant="success">Active Parish</Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card title="Parish Information">
          <div className="space-y-3 text-xs">
            <div><span className="font-semibold text-gray-700">Patron Saint:</span> {parish.patron_saint || '-'}</div>
            <div><span className="font-semibold text-gray-700">Establishment Date:</span> {parish.establishment_date || '-'}</div>
            <div><span className="font-semibold text-gray-700">Phone:</span> {parish.phone || '-'}</div>
            <div><span className="font-semibold text-gray-700">Email:</span> {parish.email || '-'}</div>
            <div><span className="font-semibold text-gray-700">Address:</span> {parish.address || '-'}</div>
            <div><span className="font-semibold text-gray-700">District / Sector:</span> {[parish.district, parish.sector].filter(Boolean).join(' / ') || '-'}</div>
          </div>
        </Card>

        <Card title="Geolocation">
          <div className="space-y-2 text-xs">
            <div><span className="font-semibold">Latitude:</span> {parish.latitude ?? '-'}</div>
            <div><span className="font-semibold">Longitude:</span> {parish.longitude ?? '-'}</div>
            <div><span className="font-semibold">Deanery ID:</span> {parish.deanery_id}</div>
          </div>
        </Card>

        <Card title="Registration">
          <div className="space-y-2 text-xs">
            <div><span className="font-semibold">Created:</span> {parish.created_at ? new Date(parish.created_at).toLocaleDateString() : '-'}</div>
          </div>
        </Card>
      </div>
    </div>
  );
};