import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Modal } from '../../components/common/Modal';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { Input } from '../../components/common/Input';
import { GisMapViewer, LAND_USE_COLORS } from '../../components/map/GisMapViewer';
import { domainApi } from '../../core/api/domain';
import { LandParcel, BuildingAsset } from '../../core/types/land.types';
import { Edit2, Plus, Building2, MapPin, FileText, CheckCircle2 } from 'lucide-react';

interface LandParcelDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  parcel: LandParcel | null;
  onEdit: (parcel: LandParcel) => void;
}

export const LandParcelDetailModal: React.FC<LandParcelDetailModalProps> = ({
  isOpen,
  onClose,
  parcel,
  onEdit,
}) => {
  const queryClient = useQueryClient();
  const [showAddBuilding, setShowAddBuilding] = useState(false);
  const [buildingName, setBuildingName] = useState('');
  const [buildingType, setBuildingType] = useState('Church Building');
  const [constructionYear, setConstructionYear] = useState('');
  const [floorsCount, setFloorsCount] = useState('1');
  const [condition, setCondition] = useState('Good');
  const [buildingError, setBuildingError] = useState<string | null>(null);

  const buildingsQuery = useQuery({
    queryKey: ['parcel-buildings', parcel?.id],
    queryFn: () => domainApi.listParcelBuildings(parcel!.id),
    enabled: Boolean(parcel?.id && isOpen),
  });

  const addBuildingMutation = useMutation({
    mutationFn: (payload: { parcel_id: string; name: string; building_type: string; construction_year?: number | null; floors_count: number; condition: string }) =>
      domainApi.createBuildingAsset(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['parcel-buildings', parcel?.id] });
      setShowAddBuilding(false);
      setBuildingName('');
      setConstructionYear('');
      setFloorsCount('1');
    },
    onError: (err: any) => {
      setBuildingError(err?.response?.data?.message || err.message || 'Failed to add building asset');
    },
  });

  if (!parcel) return null;

  const handleAddBuildingSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setBuildingError(null);
    if (!buildingName.trim()) {
      setBuildingError('Building name is required.');
      return;
    }
    addBuildingMutation.mutate({
      parcel_id: parcel.id,
      name: buildingName.trim(),
      building_type: buildingType,
      construction_year: constructionYear ? parseInt(constructionYear, 10) : null,
      floors_count: parseInt(floorsCount, 10) || 1,
      condition,
    });
  };

  const hasPolygon = Boolean(parcel.geojson_geometry?.coordinates);
  const landUseColor = LAND_USE_COLORS[parcel.land_use] || '#3b82f6';

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`Parcel Dossier: ${parcel.parcel_name}`}
      maxWidth="3xl"
    >
      <div className="space-y-6">
        {/* Header summary strip */}
        <div className="flex flex-wrap items-start justify-between gap-4 p-4 bg-gray-50 rounded-xl border border-gray-100">
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-sm font-bold text-gray-900 bg-white px-2 py-0.5 rounded border border-gray-200">
                {parcel.upi}
              </span>
              <span
                className="text-xs px-2.5 py-0.5 rounded-full font-semibold text-white"
                style={{ backgroundColor: landUseColor }}
              >
                {parcel.land_use}
              </span>
              <Badge variant="neutral">{parcel.tenure_status}</Badge>
            </div>
            <h2 className="text-lg font-bold text-gray-900 mt-2">{parcel.parcel_name}</h2>
            {parcel.title_deed_number && (
              <p className="text-xs text-gray-500 mt-0.5 flex items-center gap-1">
                <FileText className="w-3.5 h-3.5" /> Deed: {parcel.title_deed_number}
              </p>
            )}
          </div>
          <Button
            size="sm"
            variant="outline"
            onClick={() => {
              onClose();
              onEdit(parcel);
            }}
          >
            <Edit2 className="w-3.5 h-3.5 mr-1" /> Edit Parcel
          </Button>
        </div>

        {/* Spatial Map View */}
        <div>
          <h3 className="text-xs font-bold text-gray-700 uppercase tracking-wider mb-2 flex items-center gap-1.5">
            <MapPin className="w-3.5 h-3.5 text-brand-600" />
            Geospatial Boundary (SRID 4326 PostGIS)
          </h3>
          {hasPolygon ? (
            <GisMapViewer
              parcels={[parcel]}
              selectedParcelId={parcel.id}
              height="280px"
              zoom={15}
            />
          ) : (
            <div className="p-8 text-center bg-gray-50 rounded-xl border border-dashed border-gray-300 text-xs text-gray-500">
              No boundary polygon attached to this parcel yet. Click "Edit Parcel" to draw or upload GeoJSON coordinates.
            </div>
          )}
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="p-3 bg-white border border-gray-200 rounded-lg shadow-2xs">
            <span className="text-[11px] text-gray-500 uppercase font-semibold">Total Area</span>
            <p className="text-base font-bold text-gray-900 mt-0.5">{parcel.area_sqm.toLocaleString()} m²</p>
          </div>
          <div className="p-3 bg-white border border-gray-200 rounded-lg shadow-2xs">
            <span className="text-[11px] text-gray-500 uppercase font-semibold">Estimated Value</span>
            <p className="text-base font-bold text-gray-900 mt-0.5">
              {parcel.estimated_value_rwf ? `${parcel.estimated_value_rwf.toLocaleString()} RWF` : '-'}
            </p>
          </div>
          <div className="p-3 bg-white border border-gray-200 rounded-lg shadow-2xs">
            <span className="text-[11px] text-gray-500 uppercase font-semibold">Acquisition Date</span>
            <p className="text-sm font-semibold text-gray-900 mt-0.5">{parcel.acquisition_date || '-'}</p>
          </div>
          <div className="p-3 bg-white border border-gray-200 rounded-lg shadow-2xs">
            <span className="text-[11px] text-gray-500 uppercase font-semibold">Location</span>
            <p className="text-xs font-semibold text-gray-900 mt-0.5">
              {parcel.district || '-'}{parcel.sector ? ` / ${parcel.sector}` : ''}
            </p>
          </div>
        </div>

        {/* Building Assets on Parcel */}
        <div className="border-t border-gray-100 pt-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-xs font-bold text-gray-700 uppercase tracking-wider flex items-center gap-1.5">
              <Building2 className="w-3.5 h-3.5 text-brand-600" />
              Building Assets on Parcel ({buildingsQuery.data?.length || 0})
            </h3>
            <Button
              size="sm"
              variant="outline"
              onClick={() => setShowAddBuilding(!showAddBuilding)}
            >
              <Plus className="w-3.5 h-3.5 mr-1" />
              {showAddBuilding ? 'Cancel' : 'Add Building'}
            </Button>
          </div>

          {/* Add Building Sub-form */}
          {showAddBuilding && (
            <form onSubmit={handleAddBuildingSubmit} className="p-4 bg-gray-50 rounded-lg border border-gray-200 mb-4 space-y-3">
              <h4 className="text-xs font-bold text-gray-800">Register New Building Asset</h4>
              {buildingError && (
                <div className="p-2 bg-red-50 text-red-600 text-xs rounded border border-red-200">
                  {buildingError}
                </div>
              )}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <Input
                  label="Building Name"
                  placeholder="Main Church Sanctuary"
                  value={buildingName}
                  onChange={(e) => setBuildingName(e.target.value)}
                  required
                />
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Building Type</label>
                  <select
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-xs"
                    value={buildingType}
                    onChange={(e) => setBuildingType(e.target.value)}
                  >
                    <option value="Church Building">Church Building / Kiriziya</option>
                    <option value="Priest House (Presbytery)">Presbytery / Ibiro n'inzu y'abapadiri</option>
                    <option value="Parish Hall">Parish Hall / Salle paroissiale</option>
                    <option value="School Classrooms">School Classrooms / Amashuri</option>
                    <option value="Health Center Clinic">Clinic / Centre de Santé</option>
                    <option value="Convent Quarters">Convent Quarters / Irugo rw'ababikira</option>
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-3">
                <Input
                  label="Construction Year"
                  type="number"
                  placeholder="1985"
                  value={constructionYear}
                  onChange={(e) => setConstructionYear(e.target.value)}
                />
                <Input
                  label="Floors Count"
                  type="number"
                  value={floorsCount}
                  onChange={(e) => setFloorsCount(e.target.value)}
                />
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Condition</label>
                  <select
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-xs"
                    value={condition}
                    onChange={(e) => setCondition(e.target.value)}
                  >
                    <option value="Good">Good</option>
                    <option value="Fair">Fair</option>
                    <option value="Needs Renovation">Needs Renovation</option>
                    <option value="Dilapidated">Dilapidated</option>
                  </select>
                </div>
              </div>
              <div className="flex justify-end gap-2">
                <Button size="sm" type="submit" disabled={addBuildingMutation.isPending}>
                  {addBuildingMutation.isPending ? 'Saving...' : 'Save Building'}
                </Button>
              </div>
            </form>
          )}

          {/* Building assets list */}
          {buildingsQuery.isLoading ? (
            <p className="text-xs text-gray-500 py-2">Loading buildings...</p>
          ) : buildingsQuery.data && buildingsQuery.data.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {buildingsQuery.data.map((b: BuildingAsset) => (
                <div key={b.id} className="p-3 bg-white border border-gray-200 rounded-lg shadow-2xs">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-xs font-bold text-gray-900">{b.name}</p>
                      <p className="text-[11px] text-gray-500">{b.building_type}</p>
                    </div>
                    <Badge variant={b.condition === 'Good' ? 'success' : 'neutral'}>{b.condition}</Badge>
                  </div>
                  <div className="mt-2 text-[11px] text-gray-600 flex items-center gap-3">
                    <span>Floors: {b.floors_count}</span>
                    {b.construction_year && <span>Built: {b.construction_year}</span>}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-gray-400 italic py-2">No physical buildings registered on this parcel.</p>
          )}
        </div>

        <div className="flex justify-end pt-4 border-t border-gray-100">
          <Button variant="outline" onClick={onClose}>
            Close
          </Button>
        </div>
      </div>
    </Modal>
  );
};
