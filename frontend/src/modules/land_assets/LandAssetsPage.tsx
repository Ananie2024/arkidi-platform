import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { GisMapViewer } from '../../components/map/GisMapViewer';
import { Plus } from 'lucide-react';
import { LandParcel } from '../../core/types/land.types';
import { domainApi } from '../../core/api/domain';

export const LandAssetsPage: React.FC = () => {
  const parcelsQuery = useQuery({
    queryKey: ['land-parcels'],
    queryFn: domainApi.listParcels,
  });

  const columns: Column<LandParcel>[] = [
    { header: 'UPI (Cadastre)', accessor: 'upi' },
    { header: 'Parcel Name', accessor: 'parcel_name' },
    { header: 'Land Use', accessor: 'land_use' },
    { header: 'Location', accessor: (row) => `${row.district || '-'} / ${row.sector || '-'}` },
    { header: 'Area (sqm)', accessor: (row) => row.area_sqm.toLocaleString() },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Land Intelligence & Real Estate GIS</h1>
          <p className="text-xs text-gray-500 mt-0.5">PostGIS parcel registry with cadastral UPI numbers, title deeds and boundary polygons</p>
        </div>
        <Button size="sm">
          <Plus className="w-4 h-4 mr-1.5" /> Register Parcel
        </Button>
      </div>

      <Card title="Archdiocesan Land Parcels (Spatial View)">
        <GisMapViewer height="300px" />
      </Card>

      <Card>
        <Table
          columns={columns}
          data={parcelsQuery.data || []}
          isLoading={parcelsQuery.isLoading}
          emptyMessage={parcelsQuery.isError ? 'Unable to load parcels from the API.' : 'No land parcels found.'}
        />
      </Card>
    </div>
  );
};
