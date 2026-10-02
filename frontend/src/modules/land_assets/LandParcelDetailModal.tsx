import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Modal } from '../../components/common/Modal';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { Input } from '../../components/common/Input';
import { GisMapViewer, LAND_USE_COLORS } from '../../components/map/GisMapViewer';
import { domainApi } from '../../core/api/domain';
import { LandParcel, BuildingAsset } from '../../core/types/land.types';
import { Edit2, Plus, Building2, MapPin, FileText, Download } from 'lucide-react';

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
  const [documentTitle, setDocumentTitle] = useState('');
  const [documentFile, setDocumentFile] = useState<File | null>(null);
  const [documentError, setDocumentError] = useState<string | null>(null);
  const [leaseForm, setLeaseForm] = useState({ lease_number: '', lessee_name: '', start_date: '', end_date: '', monthly_rent_rwf: '' });
  const [installmentForm, setInstallmentForm] = useState({ due_date: '', amount_rwf: '' });
  const [selectedLeaseId, setSelectedLeaseId] = useState('');
  const [assessmentForm, setAssessmentForm] = useState({ tax_year: String(new Date().getFullYear()), assessed_value_rwf: '', tax_amount_rwf: '', assessment_date: '' });
  const [selectedTaxId, setSelectedTaxId] = useState('');
  const [taxPaymentForm, setTaxPaymentForm] = useState({ amount_paid_rwf: '', payment_date: new Date().toISOString().slice(0, 10), payment_method: 'CASH', receipt_number: '' });

  const buildingsQuery = useQuery({
    queryKey: ['parcel-buildings', parcel?.id],
    queryFn: () => domainApi.listParcelBuildings(parcel!.id),
    enabled: Boolean(parcel?.id && isOpen),
  });
  const documentsQuery = useQuery({
    queryKey: ['parcel-documents', parcel?.id],
    queryFn: () => domainApi.listParcelDocuments(parcel!.id),
    enabled: Boolean(parcel?.id && isOpen),
  });
  const leasesQuery = useQuery({ queryKey: ['parcel-leases', parcel?.id], queryFn: () => domainApi.listParcelLeases(parcel!.id), enabled: Boolean(parcel?.id && isOpen) });
  const installmentsQuery = useQuery({ queryKey: ['lease-installments', selectedLeaseId], queryFn: () => domainApi.listLeaseInstallments(selectedLeaseId), enabled: Boolean(selectedLeaseId && isOpen) });
  const taxQuery = useQuery({ queryKey: ['parcel-tax', parcel?.id], queryFn: () => domainApi.listParcelTaxAssessments(parcel!.id), enabled: Boolean(parcel?.id && isOpen) });
  const refreshLandRecords = () => {
    queryClient.invalidateQueries({ queryKey: ['parcel-leases', parcel?.id] });
    queryClient.invalidateQueries({ queryKey: ['lease-installments', selectedLeaseId] });
    queryClient.invalidateQueries({ queryKey: ['parcel-tax', parcel?.id] });
  };
  const createLeaseMutation = useMutation({ mutationFn: () => domainApi.createLease({ ...leaseForm, parcel_id: parcel!.id, monthly_rent_rwf: Number(leaseForm.monthly_rent_rwf), end_date: leaseForm.end_date || null }), onSuccess: () => { setLeaseForm({ lease_number: '', lessee_name: '', start_date: '', end_date: '', monthly_rent_rwf: '' }); refreshLandRecords(); } });
  const addInstallmentMutation = useMutation({ mutationFn: () => domainApi.createLeaseInstallment(selectedLeaseId, { ...installmentForm, amount_rwf: Number(installmentForm.amount_rwf) }), onSuccess: () => { setInstallmentForm({ due_date: '', amount_rwf: '' }); refreshLandRecords(); } });
  const payInstallmentMutation = useMutation({ mutationFn: (id: string) => { const receipt = window.prompt('Receipt number for this rent payment'); if (!receipt?.trim()) throw new Error('A receipt number is required.'); return domainApi.markLeaseInstallmentPaid(id, { paid_date: new Date().toISOString().slice(0, 10), receipt_number: receipt.trim() }); }, onSuccess: refreshLandRecords });
  const createAssessmentMutation = useMutation({ mutationFn: () => domainApi.createTaxAssessment(parcel!.id, { ...assessmentForm, tax_year: Number(assessmentForm.tax_year), assessed_value_rwf: Number(assessmentForm.assessed_value_rwf), tax_amount_rwf: Number(assessmentForm.tax_amount_rwf), assessment_date: assessmentForm.assessment_date || null }), onSuccess: () => { setAssessmentForm({ tax_year: String(new Date().getFullYear()), assessed_value_rwf: '', tax_amount_rwf: '', assessment_date: '' }); refreshLandRecords(); } });
  const payTaxMutation = useMutation({ mutationFn: () => domainApi.createTaxPayment(selectedTaxId, { ...taxPaymentForm, amount_paid_rwf: Number(taxPaymentForm.amount_paid_rwf), receipt_number: taxPaymentForm.receipt_number || null }), onSuccess: () => { setTaxPaymentForm({ amount_paid_rwf: '', payment_date: new Date().toISOString().slice(0, 10), payment_method: 'CASH', receipt_number: '' }); refreshLandRecords(); } });

  const uploadDocumentMutation = useMutation({
    mutationFn: () => domainApi.uploadParcelDocument(parcel!.id, parcel!.parish_id, documentTitle.trim(), documentFile!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['parcel-documents', parcel?.id] });
      setDocumentTitle('');
      setDocumentFile(null);
      setDocumentError(null);
    },
    onError: (err: any) => setDocumentError(err?.response?.data?.detail || err?.response?.data?.message || err.message || 'Unable to upload document.'),
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
      maxWidth="2xl"
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

        {/* Deeds, title scans and contracts use the audited document repository. */}
        <section className="border-t border-gray-100 pt-4">
          <h3 className="mb-3 flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-gray-700">
            <FileText className="h-3.5 w-3.5 text-brand-600" /> Title, deed and lease documents
          </h3>
          {documentError && <p role="alert" className="mb-2 rounded border border-red-200 bg-red-50 p-2 text-xs text-red-700">{documentError}</p>}
          <form className="mb-3 grid gap-2 rounded-lg bg-gray-50 p-3 sm:grid-cols-[1fr_1fr_auto]" onSubmit={(e) => { e.preventDefault(); if (documentTitle.trim() && documentFile) uploadDocumentMutation.mutate(); }}>
            <Input label="Document title" placeholder="Registered title deed" value={documentTitle} onChange={(e) => setDocumentTitle(e.target.value)} required />
            <Input label="Select scanned document" type="file" accept="application/pdf,image/*" onChange={(e) => setDocumentFile(e.target.files?.[0] || null)} required />
            <div className="flex items-end"><Button size="sm" type="submit" disabled={!documentFile || uploadDocumentMutation.isPending}>{uploadDocumentMutation.isPending ? 'Uploading…' : 'Upload'}</Button></div>
          </form>
          {documentsQuery.isLoading ? <p className="text-xs text-gray-500">Loading parcel documents…</p> : documentsQuery.isError ? <p className="text-xs text-red-600">Unable to load parcel documents.</p> : documentsQuery.data?.length ? (
            <ul className="divide-y divide-gray-100 rounded-lg border border-gray-200">
              {documentsQuery.data.map((doc) => <li key={doc.id} className="flex items-center justify-between gap-3 p-3">
                <div className="min-w-0"><p className="truncate text-sm font-medium text-gray-800">{doc.title}</p><p className="text-xs text-gray-500">{new Date(doc.created_at).toLocaleDateString()} · {doc.mime_type || 'Document'}</p></div>
                <Button size="sm" variant="outline" onClick={async () => { try { const blob = await domainApi.downloadParcelDocument(doc.id); const url = URL.createObjectURL(blob); const link = document.createElement('a'); link.href = url; link.download = doc.title; link.click(); URL.revokeObjectURL(url); } catch { setDocumentError('Unable to download document.'); } }}><Download className="mr-1 h-3.5 w-3.5" />Download</Button>
              </li>)}
            </ul>
          ) : <p className="text-xs italic text-gray-400">No title or contract documents uploaded for this parcel.</p>}
        </section>

        <section className="border-t border-gray-100 pt-4">
          <h3 className="mb-3 text-xs font-bold uppercase tracking-wider text-gray-700">Leases and rent schedule</h3>
          <form className="mb-3 grid gap-2 rounded-lg bg-gray-50 p-3 sm:grid-cols-2 lg:grid-cols-5" onSubmit={(e) => { e.preventDefault(); createLeaseMutation.mutate(); }}>
            <Input label="Lease number" required value={leaseForm.lease_number} onChange={(e) => setLeaseForm({ ...leaseForm, lease_number: e.target.value })} />
            <Input label="Lessee" required value={leaseForm.lessee_name} onChange={(e) => setLeaseForm({ ...leaseForm, lessee_name: e.target.value })} />
            <Input label="Start date" type="date" required value={leaseForm.start_date} onChange={(e) => setLeaseForm({ ...leaseForm, start_date: e.target.value })} />
            <Input label="End date" type="date" value={leaseForm.end_date} onChange={(e) => setLeaseForm({ ...leaseForm, end_date: e.target.value })} />
            <Input label="Monthly rent (RWF)" type="number" min="0" step="0.01" required value={leaseForm.monthly_rent_rwf} onChange={(e) => setLeaseForm({ ...leaseForm, monthly_rent_rwf: e.target.value })} />
            <div className="sm:col-span-2 lg:col-span-5"><Button size="sm" type="submit" disabled={createLeaseMutation.isPending}>Register lease</Button></div>
          </form>
          {leasesQuery.data?.length ? <div className="mb-3 flex flex-wrap gap-2">{leasesQuery.data.map((lease) => <button key={lease.id} type="button" onClick={() => setSelectedLeaseId(lease.id)} className={`rounded border px-3 py-2 text-left text-xs ${selectedLeaseId === lease.id ? 'border-brand-500 bg-brand-50' : 'border-gray-200'}`}><strong>{lease.lease_number}</strong> · {lease.lessee_name} · {Number(lease.monthly_rent_rwf).toLocaleString()} RWF/month</button>)}</div> : <p className="mb-3 text-xs text-gray-400">No leases registered.</p>}
          {selectedLeaseId && <>
            <form className="mb-3 flex flex-wrap items-end gap-2" onSubmit={(e) => { e.preventDefault(); addInstallmentMutation.mutate(); }}>
              <Input label="Rent due date" type="date" required value={installmentForm.due_date} onChange={(e) => setInstallmentForm({ ...installmentForm, due_date: e.target.value })} />
              <Input label="Amount (RWF)" type="number" min="0.01" step="0.01" required value={installmentForm.amount_rwf} onChange={(e) => setInstallmentForm({ ...installmentForm, amount_rwf: e.target.value })} />
              <Button size="sm" type="submit">Schedule installment</Button>
            </form>
            <div className="space-y-1">{installmentsQuery.data?.map((item) => <div key={item.id} className="flex items-center justify-between rounded bg-gray-50 px-3 py-2 text-xs"><span>Due {item.due_date} · {Number(item.amount_rwf).toLocaleString()} RWF {item.is_paid ? `· Paid ${item.paid_date} · ${item.receipt_number}` : '· Outstanding'}</span>{!item.is_paid && <Button size="sm" variant="outline" disabled={payInstallmentMutation.isPending} onClick={() => payInstallmentMutation.mutate(item.id)}>Record payment</Button>}</div>)}</div>
          </>}
        </section>

        <section className="border-t border-gray-100 pt-4">
          <h3 className="mb-3 text-xs font-bold uppercase tracking-wider text-gray-700">Property tax assessments and payments</h3>
          <form className="mb-3 grid gap-2 rounded-lg bg-gray-50 p-3 sm:grid-cols-2 lg:grid-cols-4" onSubmit={(e) => { e.preventDefault(); createAssessmentMutation.mutate(); }}>
            <Input label="Tax year" type="number" min="1900" required value={assessmentForm.tax_year} onChange={(e) => setAssessmentForm({ ...assessmentForm, tax_year: e.target.value })} />
            <Input label="Assessed property value (RWF)" type="number" min="0" step="0.01" required value={assessmentForm.assessed_value_rwf} onChange={(e) => setAssessmentForm({ ...assessmentForm, assessed_value_rwf: e.target.value })} />
            <Input label="Tax assessed (RWF)" type="number" min="0" step="0.01" required value={assessmentForm.tax_amount_rwf} onChange={(e) => setAssessmentForm({ ...assessmentForm, tax_amount_rwf: e.target.value })} />
            <Input label="Assessment date" type="date" value={assessmentForm.assessment_date} onChange={(e) => setAssessmentForm({ ...assessmentForm, assessment_date: e.target.value })} />
            <div className="sm:col-span-2 lg:col-span-4"><Button size="sm" type="submit" disabled={createAssessmentMutation.isPending}>Record assessment</Button></div>
          </form>
          {taxQuery.data?.length ? <div className="space-y-2">{taxQuery.data.map((tax) => <div key={tax.id} className={`rounded border p-3 ${selectedTaxId === tax.id ? 'border-brand-500' : 'border-gray-200'}`}>
            <div className="flex flex-wrap items-center justify-between gap-2 text-xs"><span><strong>{tax.tax_year}</strong> · Assessed {Number(tax.tax_amount_rwf).toLocaleString()} RWF · {tax.status}</span><Button size="sm" variant="outline" onClick={() => setSelectedTaxId(tax.id)}>{selectedTaxId === tax.id ? 'Selected' : 'Record payment'}</Button></div>
            {selectedTaxId === tax.id && <form className="mt-3 flex flex-wrap items-end gap-2" onSubmit={(e) => { e.preventDefault(); payTaxMutation.mutate(); }}><Input label="Amount paid (RWF)" type="number" min="0.01" step="0.01" required value={taxPaymentForm.amount_paid_rwf} onChange={(e) => setTaxPaymentForm({ ...taxPaymentForm, amount_paid_rwf: e.target.value })} /><Input label="Payment date" type="date" required value={taxPaymentForm.payment_date} onChange={(e) => setTaxPaymentForm({ ...taxPaymentForm, payment_date: e.target.value })} /><Input label="Receipt number" value={taxPaymentForm.receipt_number} onChange={(e) => setTaxPaymentForm({ ...taxPaymentForm, receipt_number: e.target.value })} /><Button size="sm" type="submit" disabled={payTaxMutation.isPending}>Save tax payment</Button></form>}
          </div>)}</div> : <p className="text-xs text-gray-400">No assessments registered.</p>}
        </section>

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
