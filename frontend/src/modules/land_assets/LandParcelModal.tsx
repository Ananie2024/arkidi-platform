import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Modal } from '../../components/common/Modal';
import { Input } from '../../components/common/Input';
import { Button } from '../../components/common/Button';
import { ParcelDrawer } from '../../components/map/ParcelDrawer';
import { domainApi } from '../../core/api/domain';
import { LandParcel, LandUseType, TenureStatus } from '../../core/types/land.types';

interface LandParcelModalProps {
  isOpen: boolean;
  onClose: () => void;
  parcel?: LandParcel | null;
  defaultParishId?: string;
}

const LAND_USES: { value: LandUseType; label: string }[] = [
  { value: 'CHURCH_COMPOUND', label: 'Church Compound / Kiriziya n\'ibiro' },
  { value: 'CENTRALE_CHAPEL', label: 'Centrale Chapel / Isakramentu' },
  { value: 'HEALTH_FACILITY', label: 'Health Facility / Ibitaro / Centre de Santé' },
  { value: 'EDUCATIONAL', label: 'Educational / Amashuri' },
  { value: 'AGRICULTURAL', label: 'Agricultural / Ubuhinzi n\'Ubworozi' },
  { value: 'COMMERCIAL_RENTAL', label: 'Commercial Rental / Inzu zikodeshwa' },
  { value: 'CONVENT_MONASTERY', label: 'Convent / Monastery / Abihayimana' },
  { value: 'CEMETERY', label: 'Cemetery / Irimbi' },
  { value: 'VACANT_RESERVE', label: 'Vacant Reserve / Ubutaka bw\'umutungo' },
];

const TENURE_STATUSES: { value: TenureStatus; label: string }[] = [
  { value: 'FREEHOLD', label: 'Freehold (Ubutaka burambye)' },
  { value: 'EMPHYTEUTIC_LEASE', label: 'Emphyteutic Lease (Ubukode burambye)' },
  { value: 'DISPUTED', label: 'Disputed (Harimo amakimbirane)' },
  { value: 'IN_REGISTRATION', label: 'In Registration (Mu kwandikisha)' },
];

export const LandParcelModal: React.FC<LandParcelModalProps> = ({
  isOpen,
  onClose,
  parcel,
  defaultParishId,
}) => {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const isEdit = Boolean(parcel);

  const parishesQuery = useQuery({
    queryKey: ['parishes'],
    queryFn: () => domainApi.listParishes(),
  });

  const [upi, setUpi] = useState(parcel?.upi || '');
  const [parcelName, setParcelName] = useState(parcel?.parcel_name || '');
  const [titleDeedNumber, setTitleDeedNumber] = useState(parcel?.title_deed_number || '');
  const [parishId, setParishId] = useState(parcel?.parish_id || defaultParishId || '');
  const [landUse, setLandUse] = useState<LandUseType>(parcel?.land_use || 'CHURCH_COMPOUND');
  const [tenureStatus, setTenureStatus] = useState<TenureStatus>(parcel?.tenure_status || 'FREEHOLD');
  const [areaSqm, setAreaSqm] = useState(parcel?.area_sqm ? String(parcel.area_sqm) : '');
  const [acquisitionDate, setAcquisitionDate] = useState(parcel?.acquisition_date || '');
  const [estimatedValueRwf, setEstimatedValueRwf] = useState(
    parcel?.estimated_value_rwf ? String(parcel.estimated_value_rwf) : ''
  );
  const [province, setProvince] = useState(parcel?.province || 'Kigali City');
  const [district, setDistrict] = useState(parcel?.district || 'Nyarugenge');
  const [sector, setSector] = useState(parcel?.sector || '');
  const [cell, setCell] = useState(parcel?.cell || '');
  const [village, setVillage] = useState(parcel?.village || '');
  const [geometry, setGeometry] = useState<{ type: string; coordinates: any } | null>(
    parcel?.geojson_geometry || null
  );
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Sync state if parcel prop changes
  React.useEffect(() => {
    if (parcel) {
      setUpi(parcel.upi);
      setParcelName(parcel.parcel_name);
      setTitleDeedNumber(parcel.title_deed_number || '');
      setParishId(parcel.parish_id);
      setLandUse(parcel.land_use);
      setTenureStatus(parcel.tenure_status);
      setAreaSqm(String(parcel.area_sqm));
      setAcquisitionDate(parcel.acquisition_date || '');
      setEstimatedValueRwf(parcel.estimated_value_rwf ? String(parcel.estimated_value_rwf) : '');
      setProvince(parcel.province || 'Kigali City');
      setDistrict(parcel.district || '');
      setSector(parcel.sector || '');
      setCell(parcel.cell || '');
      setVillage(parcel.village || '');
      setGeometry(parcel.geojson_geometry || null);
    } else {
      setUpi('');
      setParcelName('');
      setTitleDeedNumber('');
      setParishId(defaultParishId || '');
      setLandUse('CHURCH_COMPOUND');
      setTenureStatus('FREEHOLD');
      setAreaSqm('');
      setAcquisitionDate('');
      setEstimatedValueRwf('');
      setProvince('Kigali City');
      setDistrict('Nyarugenge');
      setSector('');
      setCell('');
      setVillage('');
      setGeometry(null);
    }
  }, [parcel, defaultParishId]);

  const mutation = useMutation({
    mutationFn: async (payload: Record<string, unknown>) => {
      if (isEdit && parcel) {
        return domainApi.updateParcel(parcel.id, payload);
      }
      return domainApi.createParcel(payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['land-parcels'] });
      onClose();
    },
    onError: (err: any) => {
      setErrorMsg(err?.response?.data?.message || err.message || 'Operation failed');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);

    const effectiveParishId = parishId || parishesQuery.data?.[0]?.id;
    if (!effectiveParishId) {
      setErrorMsg('Please select a parish.');
      return;
    }

    const payload: Record<string, unknown> = {
      upi: upi.trim(),
      parcel_name: parcelName.trim(),
      title_deed_number: titleDeedNumber.trim() || null,
      parish_id: effectiveParishId,
      land_use: landUse,
      tenure_status: tenureStatus,
      area_sqm: parseFloat(areaSqm) || 0,
      acquisition_date: acquisitionDate || null,
      estimated_value_rwf: estimatedValueRwf ? parseFloat(estimatedValueRwf) : null,
      province: province.trim(),
      district: district.trim() || null,
      sector: sector.trim() || null,
      cell: cell.trim() || null,
      village: village.trim() || null,
      geojson_geometry: geometry,
    };

    mutation.mutate(payload);
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEdit ? `Edit Parcel: ${parcel?.parcel_name}` : t('land_assets.register')}
      maxWidth="2xl"
    >
      <form className="space-y-4" onSubmit={handleSubmit}>
        {errorMsg && (
          <div className="p-2.5 bg-red-50 border border-red-200 rounded text-xs text-red-600">
            {errorMsg}
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <Input
            label={t('land_assets.col_upi', 'UPI (Cadastral Number)')}
            placeholder="1/02/07/02/1234"
            value={upi}
            onChange={(e) => setUpi(e.target.value)}
            required
          />
          <Input
            label={t('land_assets.col_parcel_name', 'Parcel Name')}
            placeholder="Paroisse Sainte Famille Compound"
            value={parcelName}
            onChange={(e) => setParcelName(e.target.value)}
            required
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <Input
            label="Title Deed #"
            placeholder="TD-2021-556677"
            value={titleDeedNumber}
            onChange={(e) => setTitleDeedNumber(e.target.value)}
          />
          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">Parish</label>
            <select
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-xs focus:outline-none focus:ring-1 focus:ring-brand-500"
              value={parishId}
              onChange={(e) => setParishId(e.target.value)}
              required
            >
              <option value="">Select Parish...</option>
              {parishesQuery.data?.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">Land Use</label>
            <select
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-xs focus:outline-none focus:ring-1 focus:ring-brand-500"
              value={landUse}
              onChange={(e) => setLandUse(e.target.value as LandUseType)}
              required
            >
              {LAND_USES.map((u) => (
                <option key={u.value} value={u.value}>
                  {u.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">Tenure Status</label>
            <select
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-xs focus:outline-none focus:ring-1 focus:ring-brand-500"
              value={tenureStatus}
              onChange={(e) => setTenureStatus(e.target.value as TenureStatus)}
              required
            >
              {TENURE_STATUSES.map((s) => (
                <option key={s.value} value={s.value}>
                  {s.label}
                </option>
              ))}
            </select>
          </div>
          <Input
            label={t('land_assets.col_area', 'Area (sqm)')}
            type="number"
            step="0.01"
            placeholder="12450.5"
            value={areaSqm}
            onChange={(e) => setAreaSqm(e.target.value)}
            required
          />
          <Input
            label="Estimated Value (RWF)"
            type="number"
            placeholder="450000000"
            value={estimatedValueRwf}
            onChange={(e) => setEstimatedValueRwf(e.target.value)}
          />
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <Input
            label="Province"
            value={province}
            onChange={(e) => setProvince(e.target.value)}
          />
          <Input
            label="District"
            value={district}
            onChange={(e) => setDistrict(e.target.value)}
          />
          <Input
            label="Sector"
            value={sector}
            onChange={(e) => setSector(e.target.value)}
          />
          <Input
            label="Acquisition Date"
            type="date"
            value={acquisitionDate}
            onChange={(e) => setAcquisitionDate(e.target.value)}
          />
        </div>

        {/* Boundary Polygon Drawer */}
        <div className="pt-2">
          <ParcelDrawer
            initialGeometry={geometry}
            onSave={(geom) => setGeometry(geom)}
          />
        </div>

        <div className="flex justify-end gap-2 pt-4 border-t border-gray-100">
          <Button variant="outline" type="button" onClick={onClose} disabled={mutation.isPending}>
            {t('common.cancel')}
          </Button>
          <Button type="submit" disabled={mutation.isPending}>
            {mutation.isPending ? t('common.loading') : isEdit ? t('common.save') : t('land_assets.register')}
          </Button>
        </div>
      </form>
    </Modal>
  );
};
