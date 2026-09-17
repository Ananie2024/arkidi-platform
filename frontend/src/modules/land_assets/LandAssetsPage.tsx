import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Card } from '../../components/common/Card';
import { Table, Column } from '../../components/common/Table';
import { Button } from '../../components/common/Button';
import { GisMapViewer } from '../../components/map/GisMapViewer';
import { Plus, Eye, Edit, MapPin } from 'lucide-react';
import { LandParcel } from '../../core/types/land.types';
import { domainApi } from '../../core/api/domain';
import { LandParcelModal } from './LandParcelModal';
import { LandParcelDetailModal } from './LandParcelDetailModal';

export const LandAssetsPage: React.FC = () => {
  const { t } = useTranslation();
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [editingParcel, setEditingParcel] = useState<LandParcel | null>(null);
  const [detailParcel, setDetailParcel] = useState<LandParcel | null>(null);
  const [selectedMapParcelId, setSelectedMapParcelId] = useState<string | null>(null);

  const parcelsQuery = useQuery({
    queryKey: ['land-parcels'],
    queryFn: () => domainApi.listParcels(),
  });

  const parcels = parcelsQuery.data || [];
  const totalArea = parcels.reduce((sum, p) => sum + (Number(p.area_sqm) || 0), 0);

  const columns: Column<LandParcel>[] = [
    { header: t('land_assets.col_upi'), accessor: 'upi' },
    { header: t('land_assets.col_parcel_name'), accessor: 'parcel_name' },
    { header: t('land_assets.col_land_use'), accessor: 'land_use' },
    { header: t('land_assets.col_location'), accessor: (row) => `${row.district || '-'} / ${row.sector || '-'}` },
    { header: t('land_assets.col_area'), accessor: (row) => row.area_sqm.toLocaleString() },
    {
      header: t('common.actions'),
      accessor: (row) => (
        <div className="flex items-center gap-1.5">
          <button
            type="button"
            title="View Dossier"
            aria-label={`View ${row.parcel_name}`}
            onClick={() => setDetailParcel(row)}
            className="p-1 text-gray-500 hover:text-brand-600 hover:bg-gray-100 rounded transition"
          >
            <Eye className="w-4 h-4" />
          </button>
          <button
            type="button"
            title="Edit Parcel"
            aria-label={`Edit ${row.parcel_name}`}
            onClick={() => setEditingParcel(row)}
            className="p-1 text-gray-500 hover:text-blue-600 hover:bg-gray-100 rounded transition"
          >
            <Edit className="w-4 h-4" />
          </button>
          <button
            type="button"
            title="Locate on Map"
            aria-label={`Locate ${row.parcel_name}`}
            onClick={() => setSelectedMapParcelId(row.id)}
            className={`p-1 rounded transition ${
              selectedMapParcelId === row.id
                ? 'text-red-600 bg-red-50'
                : 'text-gray-500 hover:text-green-600 hover:bg-gray-100'
            }`}
          >
            <MapPin className="w-4 h-4" />
          </button>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">{t('land_assets.title')}</h1>
          <p className="text-xs text-gray-500 mt-0.5">{t('land_assets.subtitle')}</p>
        </div>
        <Button size="sm" onClick={() => setCreateModalOpen(true)}>
          <Plus className="w-4 h-4 mr-1.5" /> {t('land_assets.register')}
        </Button>
      </div>

      {/* Overview Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card>
          <div className="text-xs font-semibold text-gray-500 uppercase">Registered Parcels</div>
          <div className="text-2xl font-bold text-gray-900 mt-1">{parcels.length}</div>
        </Card>
        <Card>
          <div className="text-xs font-semibold text-gray-500 uppercase">Total Land Area</div>
          <div className="text-2xl font-bold text-gray-900 mt-1">
            {totalArea.toLocaleString()} <span className="text-sm font-normal text-gray-500">m²</span>
          </div>
        </Card>
        <Card>
          <div className="text-xs font-semibold text-gray-500 uppercase">Parcels with Boundary GIS</div>
          <div className="text-2xl font-bold text-brand-600 mt-1">
            {parcels.filter((p) => Boolean(p.geojson_geometry)).length}
          </div>
        </Card>
      </div>

      <Card title={t('land_assets.map_title')}>
        <GisMapViewer
          height="380px"
          parcels={parcels}
          selectedParcelId={selectedMapParcelId}
          onSelectParcel={(p) => setDetailParcel(p)}
        />
      </Card>

      <Card>
        <Table
          columns={columns}
          data={parcels}
          isLoading={parcelsQuery.isLoading}
          emptyMessage={parcelsQuery.isError ? t('land_assets.empty_error') : t('land_assets.empty_none')}
        />
      </Card>

      {/* Register New Parcel Modal */}
      {createModalOpen && (
        <LandParcelModal
          isOpen={createModalOpen}
          onClose={() => setCreateModalOpen(false)}
        />
      )}

      {/* Edit Existing Parcel Modal */}
      {editingParcel && (
        <LandParcelModal
          isOpen={Boolean(editingParcel)}
          parcel={editingParcel}
          onClose={() => setEditingParcel(null)}
        />
      )}

      {/* View Parcel Detail / Dossier Modal */}
      {detailParcel && (
        <LandParcelDetailModal
          isOpen={Boolean(detailParcel)}
          parcel={detailParcel}
          onClose={() => setDetailParcel(null)}
          onEdit={(p) => setEditingParcel(p)}
        />
      )}
    </div>
  );
};

