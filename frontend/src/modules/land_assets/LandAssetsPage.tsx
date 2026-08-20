import React from 'react';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { GisMapViewer } from '../../components/map/GisMapViewer';
import { Plus } from 'lucide-react';

interface LandParcelItem {
  id: string;
  upi: string;
  parcel_name: string;
  land_use: string;
  district: string;
  sector: string;
  area_sqm: string;
}

export const LandAssetsPage: React.FC = () => {
  const dummyParcels: LandParcelItem[] = [
    {
      id: '1',
      upi: '1/01/01/101',
      parcel_name: 'Cathédrale Saint Michel Compound',
      land_use: 'CHURCH_COMPOUND',
      district: 'Nyarugenge',
      sector: 'Kiyovu',
      area_sqm: '12,500',
    },
    {
      id: '2',
      upi: '1/02/03/205',
      parcel_name: 'Sainte Famille Rectory & School',
      land_use: 'EDUCATIONAL',
      district: 'Nyarugenge',
      sector: 'Muhima',
      area_sqm: '8,400',
    },
  ];

  const columns: Column<LandParcelItem>[] = [
    { header: 'UPI (Cadastre)', accessor: 'upi' },
    { header: 'Parcel Name', accessor: 'parcel_name' },
    { header: 'Land Use', accessor: 'land_use' },
    { header: 'Location', accessor: (row) => `${row.district} / ${row.sector}` },
    { header: 'Area (m²)', accessor: 'area_sqm' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Land Intelligence & Real Estate GIS</h1>
          <p className="text-xs text-gray-500 mt-0.5">
            PostGIS parcel registry with cadastral UPI numbers, title deeds and boundary polygons
          </p>
        </div>
        <Button size="sm">
          <Plus className="w-4 h-4 mr-1.5" /> Register Parcel
        </Button>
      </div>

      <Card title="Archdiocesan Land Parcels (Spatial View)">
        <GisMapViewer height="300px" />
      </Card>

      <Card>
        <Table columns={columns} data={dummyParcels} />
      </Card>
    </div>
  );
};
