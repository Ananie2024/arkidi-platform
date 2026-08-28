import React from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Card } from '../../components/common/Card';
import { Badge } from '../../components/common/Badge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { domainApi } from '../../core/api/domain';

export const ClergyDetailPage: React.FC = () => {
  const { clergyId } = useParams<{ clergyId: string }>();

  const priestQuery = useQuery({
    queryKey: ['priest', clergyId],
    queryFn: () => domainApi.getPriest(clergyId as string),
    enabled: !!clergyId,
  });

  if (priestQuery.isLoading) {
    return <LoadingSpinner className="py-20" />;
  }

  if (priestQuery.isError || !priestQuery.data) {
    return (
      <div className="text-sm text-gray-500 py-20 text-center">
        Unable to load the clergy record from the API.
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
        <Card title="Biographical & Ordination Data">
          <div className="space-y-3 text-xs">
            <div><span className="font-semibold text-gray-700">Clergy Type:</span> {priest.clergy_type}</div>
            <div><span className="font-semibold text-gray-700">Date of Ordination:</span> {priest.ordination_date || '-'}</div>
            <div><span className="font-semibold text-gray-700">Ordaining Bishop:</span> {priest.ordaining_bishop || '-'}</div>
            <div><span className="font-semibold text-gray-700">Congregation / Incardination:</span> {priest.congregation || '-'}</div>
            <div><span className="font-semibold text-gray-700">Phone:</span> {priest.phone_number || '-'}</div>
            <div><span className="font-semibold text-gray-700">Email:</span> {priest.email || '-'}</div>
          </div>
        </Card>

        <Card title="Current Assignment">
          <div className="space-y-2 text-xs">
            <div className="p-2.5 bg-gray-50 rounded border border-gray-100">
              <div className="font-semibold text-gray-800">{priest.current_role || '-'}</div>
              <div className="text-gray-500">Parish ID: {priest.current_parish_id || '-'}</div>
            </div>
            {priest.biography && (
              <div className="p-2.5 bg-gray-50 rounded border border-gray-100">
                <div className="font-semibold text-gray-800">Biography</div>
                <div className="text-gray-500 mt-1">{priest.biography}</div>
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
};