import { apiClient } from './client';
import { API_ENDPOINTS } from './endpoints';
import { ApiResponse, PaginatedResult } from '../types/common.types';
import { Faithful } from '../types/faithful.types';
import { BaptismRecord } from '../types/sacrament.types';
import { LandParcel, BuildingAsset, BuildingAssetCreate } from '../types/land.types';

export interface Deanery {
  id: string;
  archdiocese_id: string;
  name: string;
  code: string;
  vicar_forane_name?: string | null;
  created_at: string;
}

export interface Parish {
  id: string;
  deanery_id: string;
  name: string;
  code: string;
  patron_saint?: string | null;
  establishment_date?: string | null;
  phone?: string | null;
  email?: string | null;
  address?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  district?: string | null;
  sector?: string | null;
  created_at: string;
}

export interface Priest {
  id: string;
  first_name: string;
  last_name: string;
  title: string;
  clergy_type: string;
  date_of_birth?: string | null;
  ordaining_bishop?: string | null;
  congregation?: string | null;
  phone_number?: string | null;
  email?: string | null;
  biography?: string | null;
  status: string;
  ordination_date?: string | null;
  current_parish_id?: string | null;
  current_role?: string | null;
}

export interface Donation {
  id: string;
  receipt_number: string;
  parish_id?: string;
  faithful_id?: string | null;
  family_id?: string | null;
  donation_type: string;
  donor_name_override?: string | null;
  amount: number;
  currency: string;
  payment_method: string;
  donation_date: string;
  reference_transaction_id?: string | null;
  notes?: string | null;
  created_at?: string;
}

export interface FinancialSummary {
  total_tithes: number;
  total_offertory: number;
  total_construction: number;
  grand_total: number;
  currency: string;
}

export interface MassSchedule {
  id: string;
  parish_id?: string;
  centrale_id?: string | null;
  mass_date: string;
  start_time: string;
  language: string;
  celebrant_name?: string | null;
  liturgical_feast?: string | null;
  created_at?: string;
}

export interface MassIntention {
  id: string;
  parish_id: string;
  mass_schedule_id?: string | null;
  requested_by_name: string;
  requested_by_phone?: string | null;
  intention_type: string;
  intention_text: string;
  stipend_amount: number;
  scheduled_date: string;
  is_paid: boolean;
  created_at?: string;
}

export interface Ministry {
  id: string;
  parish_id?: string;
  name: string;
  category: string;
  patron_saint?: string | null;
  description?: string | null;
  leader_name?: string | null;
  leader_phone?: string | null;
  meeting_schedule?: string | null;
  is_active: boolean;
  created_at?: string;
}

export interface ArchiveBook {
  id: string;
  parish_id?: string;
  book_title: string;
  sacrament_type: string;
  volume_number: string;
  start_year: number;
  end_year: number;
  shelf_location?: string | null;
  total_scanned_pages?: number;
  created_at?: string;
}

export interface ScannedPage {
  id: string;
  ledger_book_id: string;
  page_number: number;
  image_file_path?: string;
  review_status: 'PENDING' | 'REVIEWED' | 'NEEDS_RESCAN';
  reviewed_at?: string | null;
  review_notes?: string | null;
  ocr_raw_text?: string | null;
  ocr_metadata?: {
    engine?: string;
    language?: string;
    image_dpi?: number;
    mean_confidence?: number | null;
    duration_ms?: number;
    status?: string;
    indexed?: boolean;
    word_count?: number;
    text_length?: number;
    error?: string;
    ocr_engine?: string;
  } | null;
  created_at: string;
}

export interface AnnualReport {
  id: string;
  parish_id: string;
  report_year: number;
  total_catholic_population: number;
  total_catechumens: number;
  total_families: number;
  infant_baptisms: number;
  adult_baptisms: number;
  first_communions: number;
  confirmations: number;
  marriages_both_catholic: number;
  marriages_mixed_religion: number;
  christian_funerals: number;
  catholic_schools_count: number;
  students_count: number;
  health_centers_count: number;
  created_at: string;
}

export interface ConfirmationRecord {
  id: string;
  parish_id: string;
  faithful_id: string;
  registry_year: number;
  volume_number: string;
  page_number: string;
  act_number: string;
  celebration_date: string;
  administering_bishop_or_vicar: string;
  sponsor_name?: string | null;
  created_at: string;
}

export interface MatrimonyRecord {
  id: string;
  parish_id: string;
  groom_faithful_id: string;
  bride_faithful_id: string;
  registry_year: number;
  volume_number: string;
  page_number: string;
  act_number: string;
  celebration_date: string;
  priest_celebrant: string;
  witness_1_name: string;
  witness_2_name: string;
  created_at: string;
}

export interface AnnuarioPontificioReport {
  year: number;
  total_parishes: number;
  total_priests: number;
  total_catholics: number;
  total_baptisms: number;
  total_confirmations: number;
  total_marriages: number;
}

export interface IndicatorConfigView {
  key: string;
  title: string;
  description: string;
  source_model: string;
  aggregation: 'count' | 'sum' | 'avg' | 'rate';
  metric_field?: string | null;
  group_by: string;
  trend_bucket?: string | null;
  date_field?: string | null;
  period_field?: string | null;
  inclusion_rules: string;
  filters: Array<Record<string, unknown>>;
  unit?: string | null;
  scope_mode: string;
}

export interface PublicOverview {
  statistics: {
    deaneries: number;
    parishes: number;
    active_priests: number;
    registered_faithful: number;
  };
  organigram: {
    name: string;
    deaneries: Array<{
      name: string;
      parishes: string[];
    }>;
  };
}

export interface IndicatorResult {
  key: string;
  title: string;
  description: string;
  aggregation: string;
  group_by: string;
  trend_bucket?: string | null;
  period_field?: string | null;
  inclusion_rules: string;
  generated_at: string;
  rows: Array<{ group_id: string | null; group_name: string; period: string | null; value: number }>;
  scope: { archdiocese_id?: string | null; deanery_id?: string | null; start_date?: string | null; end_date?: string | null; report_year?: number | null };
}

export interface ParishReportReconciliation {
  parish_id: string;
  report_year: number;
  field: string;
  submitted_count: number | null;
  register_count: number;
  difference: number | null;
  status: 'MATCH' | 'MISMATCH' | 'NO_RETURN';
}

export interface CertificateIssuance {
  id: string;
  certificate_number: string;
  verification_token: string;
  qr_code_base64: string;
  source_record_id?: string | null;
  sacrament_type?: string;
  parish_id?: string;
  created_at: string;
}

export interface ArchiveDocument {
  id: string;
  title: string;
  classification: string;
  parish_id?: string | null;
  disposition_status?: string | null;
  retention_flagged_at?: string | null;
  file_size_bytes?: number | null;
  mime_type?: string | null;
  created_at: string;
}

export interface ParcelDocument {
  id: string;
  title: string;
  document_type_id?: string | null;
  classification: string;
  parcel_id?: string | null;
  file_size_bytes?: number | null;
  mime_type?: string | null;
  created_at: string;
}

export interface Family {
  id: string;
  family_code: string;
  family_name: string;
  parish_id: string;
  centrale_id?: string | null;
  scc_id?: string | null;
  residence_address?: string | null;
  phone?: string | null;
  created_at: string;
  updated_at: string;
}

export interface SacramentalAmendment {
  id: string;
  sacrament_type: string;
  record_id: string;
  amendment_type: string;
  reason: string;
  field_changes: Record<string, { old: string; new: string }>;
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
  created_at: string;
}

export interface CertificateVerification {
  certificate_number: string;
  sacrament_type: string;
  valid: boolean;
  created_at: string;
}

async function getData<T>(url: string, params?: Record<string, unknown>): Promise<T> {
  const response = await apiClient.get<ApiResponse<T>>(url, { params });
  return response.data.data;
}

export const domainApi = {
  // Public diocesan overview
  getPublicOverview: () => getData<PublicOverview>(API_ENDPOINTS.public.overview),

  // Geography
  listDeaneries: () => getData<Deanery[]>(API_ENDPOINTS.geography.deaneries),
  listParishes: (deaneryId?: string | null) => getData<Parish[]>(API_ENDPOINTS.geography.parishes, deaneryId ? { deanery_id: deaneryId } : undefined),
  getParish: (id: string) => getData<Parish>(API_ENDPOINTS.geography.parishDetail(id)),

  // Faithful & Clergy
  getFaithful: (id: string) => getData<Faithful>(API_ENDPOINTS.faithful.detail(id)),
  listFaithful: (search?: string, parishId?: string) => getData<PaginatedResult<Faithful>>(
    API_ENDPOINTS.faithful.list,
    search || parishId ? { ...(search ? { search } : {}), ...(parishId ? { parish_id: parishId } : {}) } : undefined,
  ),
  createFaithful: async (data: Record<string, unknown>): Promise<Faithful> => {
    const res = await apiClient.post<ApiResponse<Faithful>>(API_ENDPOINTS.faithful.create, data);
    return res.data.data;
  },
  updateFaithful: async (id: string, data: Record<string, unknown>): Promise<Faithful> => {
    const res = await apiClient.patch<ApiResponse<Faithful>>(API_ENDPOINTS.faithful.detail(id), data);
    return res.data.data;
  },
  listFamilies: (parishId: string) => getData<Family[]>(API_ENDPOINTS.faithful.families, { parish_id: parishId }),
  createFamily: async (data: Record<string, unknown>): Promise<Family> => {
    const res = await apiClient.post<ApiResponse<Family>>(API_ENDPOINTS.faithful.families, data);
    return res.data.data;
  },
  updateFamily: async (id: string, data: Record<string, unknown>): Promise<Family> => {
    const res = await apiClient.patch<ApiResponse<Family>>(API_ENDPOINTS.faithful.familyDetail(id), data);
    return res.data.data;
  },
  listFamilyMembers: (id: string) => getData<Faithful[]>(API_ENDPOINTS.faithful.familyMembers(id)),
  getPriest: (id: string) => getData<Priest>(API_ENDPOINTS.clergy.detail(id)),
  listPriests: (parishId?: string | null) => getData<Priest[]>(API_ENDPOINTS.clergy.list, parishId ? { parish_id: parishId } : undefined),
  createPriest: async (data: Record<string, unknown>) => {
    const res = await apiClient.post<ApiResponse<Priest>>(API_ENDPOINTS.clergy.create, data);
    return res.data.data;
  },
  listPriestAssignments: (id: string) => getData<Array<Record<string, any>>>(API_ENDPOINTS.clergy.priestAssignments(id)),
  createPriestAssignment: async (data: Record<string, unknown>) => {
    const res = await apiClient.post<ApiResponse<Record<string, any>>>(API_ENDPOINTS.clergy.assignments, data);
    return res.data.data;
  },

  // Finance
  listDonations: (parishId: string, startDate?: string, endDate?: string) => getData<Donation[]>(API_ENDPOINTS.finance.donations, { parish_id: parishId, ...(startDate ? { start_date: startDate } : {}), ...(endDate ? { end_date: endDate } : {}) }),
  getDonation: (id: string) => getData<Donation>(API_ENDPOINTS.finance.donationDetail(id)),
  getFinancialSummary: (parishId: string, startDate?: string, endDate?: string) => getData<FinancialSummary>(API_ENDPOINTS.finance.summary, { parish_id: parishId, ...(startDate ? { start_date: startDate } : {}), ...(endDate ? { end_date: endDate } : {}) }),
  getFinanceReconciliation: (parishId: string, startDate: string, endDate: string) => getData<Array<{ payment_method: string; transaction_count: number; total_amount: number }>>(API_ENDPOINTS.finance.reconciliation, { parish_id: parishId, start_date: startDate, end_date: endDate }),
  createDonation: async (data: Record<string, unknown>): Promise<Donation> => {
    const res = await apiClient.post<ApiResponse<Donation>>(API_ENDPOINTS.finance.donations, data);
    return res.data.data;
  },

  // Land Assets
  listParcels: (parishId?: string | null) => getData<LandParcel[]>(API_ENDPOINTS.landAssets.parcels, parishId ? { parish_id: parishId } : undefined),
  getParcel: (id: string) => getData<LandParcel>(API_ENDPOINTS.landAssets.parcelDetail(id)),
  createParcel: async (data: Record<string, unknown>): Promise<LandParcel> => {
    const res = await apiClient.post<ApiResponse<LandParcel>>(API_ENDPOINTS.landAssets.parcels, data);
    return res.data.data;
  },
  updateParcel: async (id: string, data: Record<string, unknown>): Promise<LandParcel> => {
    const res = await apiClient.put<ApiResponse<LandParcel>>(API_ENDPOINTS.landAssets.parcelDetail(id), data);
    return res.data.data;
  },
  listParcelBuildings: (parcelId: string) => getData<BuildingAsset[]>(API_ENDPOINTS.landAssets.parcelBuildings(parcelId)),
  createBuildingAsset: async (data: BuildingAssetCreate): Promise<BuildingAsset> => {
    const res = await apiClient.post<ApiResponse<BuildingAsset>>(API_ENDPOINTS.landAssets.buildings, data);
    return res.data.data;
  },

  // Liturgy
  listMassSchedules: (parishId: string, forDate?: string) =>
    getData<MassSchedule[]>(API_ENDPOINTS.liturgy.masses, { parish_id: parishId, ...(forDate ? { for_date: forDate } : {}) }),
  createMassSchedule: async (data: Record<string, unknown>): Promise<MassSchedule> => {
    const res = await apiClient.post<ApiResponse<MassSchedule>>(API_ENDPOINTS.liturgy.masses, data);
    return res.data.data;
  },
  listIntentions: (parishId: string, targetDate?: string) =>
    getData<MassIntention[]>(API_ENDPOINTS.liturgy.intentions, { parish_id: parishId, ...(targetDate ? { target_date: targetDate } : {}) }),
  getIntention: (id: string) => getData<MassIntention>(API_ENDPOINTS.liturgy.intentionDetail(id)),
  createIntention: async (data: Record<string, unknown>): Promise<MassIntention> => {
    const res = await apiClient.post<ApiResponse<MassIntention>>(API_ENDPOINTS.liturgy.intentions, data);
    return res.data.data;
  },

  // Ministries
  listMinistries: (parishId?: string | null) => getData<Ministry[]>(API_ENDPOINTS.ministries.list, parishId ? { parish_id: parishId } : undefined),
  createMinistry: async (data: Record<string, unknown>): Promise<Ministry> => {
    const res = await apiClient.post<ApiResponse<Ministry>>(API_ENDPOINTS.ministries.create, data);
    return res.data.data;
  },

  // Archive & OCR
  listArchiveBooks: (parishId: string) => getData<ArchiveBook[]>(API_ENDPOINTS.archive.books, { parish_id: parishId }),
  createArchiveBook: async (data: Record<string, unknown>): Promise<ArchiveBook> => {
    const res = await apiClient.post<ApiResponse<ArchiveBook>>(API_ENDPOINTS.archive.books, data);
    return res.data.data;
  },
  listArchivePages: (bookId: string) => getData<ScannedPage[]>(API_ENDPOINTS.archive.pages(bookId)),
  getArchivePage: (pageId: string) => getData<ScannedPage>(API_ENDPOINTS.archive.pageDetail(pageId)),
  addArchivePage: async (data: Record<string, unknown>): Promise<ScannedPage> => {
    const res = await apiClient.post<ApiResponse<ScannedPage>>(API_ENDPOINTS.archive.createPage, data);
    return res.data.data;
  },

  // Governance: consultative bodies, meeting lifecycle, and approved minutes.
  listCommissions: (parishId: string) => getData<Array<Record<string, any>>>(API_ENDPOINTS.governance.commissions, { parish_id: parishId }),
  createCommission: async (data: Record<string, unknown>) => {
    const res = await apiClient.post<ApiResponse<Record<string, any>>>(API_ENDPOINTS.governance.commissions, data);
    return res.data.data;
  },
  listCouncils: (parishId: string) => getData<Array<Record<string, any>>>(API_ENDPOINTS.governance.councils, { parish_id: parishId }),
  createCouncil: async (data: Record<string, unknown>) => {
    const res = await apiClient.post<ApiResponse<Record<string, any>>>(API_ENDPOINTS.governance.councils, data);
    return res.data.data;
  },
  listGovernanceMeetings: (parishId: string) => getData<Array<Record<string, any>>>(API_ENDPOINTS.governance.meetings, { parish_id: parishId }),
  createGovernanceMeeting: async (data: Record<string, unknown>) => {
    const res = await apiClient.post<ApiResponse<Record<string, any>>>(API_ENDPOINTS.governance.meetings, data);
    return res.data.data;
  },
  updateGovernanceMeeting: async (id: string, data: Record<string, unknown>) => {
    const res = await apiClient.put<ApiResponse<Record<string, any>>>(`/governance/meetings/${id}`, data);
    return res.data.data;
  },
  listMeetingMinutes: (id: string) => getData<Array<Record<string, any>>>(API_ENDPOINTS.governance.meetingMinutes(id)),
  addMeetingMinutes: async (id: string, data: Record<string, unknown>) => {
    const res = await apiClient.post<ApiResponse<Record<string, any>>>(API_ENDPOINTS.governance.meetingMinutes(id), data);
    return res.data.data;
  },

  // Surveys: managed questionnaires, parish returns, and aggregated response review.
  listSurveys: (parishId: string) => getData<Array<Record<string, any>>>(API_ENDPOINTS.surveys.list, { parish_id: parishId }),
  createSurvey: async (data: Record<string, unknown>) => {
    const res = await apiClient.post<ApiResponse<Record<string, any>>>(API_ENDPOINTS.surveys.create, data);
    return res.data.data;
  },
  updateSurvey: async (id: string, data: Record<string, unknown>) => {
    const res = await apiClient.put<ApiResponse<Record<string, any>>>(API_ENDPOINTS.surveys.detail(id), data);
    return res.data.data;
  },
  submitSurveyResponse: async (id: string, data: Record<string, unknown>) => {
    const res = await apiClient.post<ApiResponse<Record<string, any>>>(API_ENDPOINTS.surveys.responses(id), data);
    return res.data.data;
  },
  listSurveyResponses: (id: string) => getData<Array<Record<string, any>>>(API_ENDPOINTS.surveys.responses(id)),
  getSurveySummary: (id: string) => getData<Record<string, any>>(API_ENDPOINTS.surveys.summary(id)),
  listParcelLeases: (parcelId: string) => getData<Array<Record<string, any>>>(API_ENDPOINTS.landAssets.parcelLeases(parcelId)),
  createLease: async (data: Record<string, unknown>) => {
    const res = await apiClient.post<ApiResponse<Record<string, any>>>(API_ENDPOINTS.landAssets.leases, data);
    return res.data.data;
  },
  listLeaseInstallments: (leaseId: string) => getData<Array<Record<string, any>>>(API_ENDPOINTS.landAssets.leaseInstallments(leaseId)),
  createLeaseInstallment: async (leaseId: string, data: Record<string, unknown>) => {
    const res = await apiClient.post<ApiResponse<Record<string, any>>>(API_ENDPOINTS.landAssets.leaseInstallments(leaseId), data);
    return res.data.data;
  },
  markLeaseInstallmentPaid: async (id: string, data: Record<string, unknown>) => {
    const res = await apiClient.post<ApiResponse<Record<string, any>>>(API_ENDPOINTS.landAssets.leasePayment(id), data);
    return res.data.data;
  },
  listParcelTaxAssessments: (parcelId: string) => getData<Array<Record<string, any>>>(API_ENDPOINTS.landAssets.parcelTaxAssessments(parcelId)),
  createTaxAssessment: async (parcelId: string, data: Record<string, unknown>) => {
    const res = await apiClient.post<ApiResponse<Record<string, any>>>(API_ENDPOINTS.landAssets.parcelTaxAssessments(parcelId), data);
    return res.data.data;
  },
  createTaxPayment: async (id: string, data: Record<string, unknown>) => {
    const res = await apiClient.post<ApiResponse<Record<string, any>>>(API_ENDPOINTS.landAssets.taxPayments(id), data);
    return res.data.data;
  },
  listParcelDocuments: (parcelId: string) => getData<ParcelDocument[]>(API_ENDPOINTS.documents.list, { parcel_id: parcelId }),
  uploadParcelDocument: async (parcelId: string, parishId: string, title: string, file: File): Promise<ParcelDocument> => {
    const body = new FormData();
    body.append('parcel_id', parcelId);
    body.append('parish_id', parishId);
    body.append('title', title);
    body.append('classification', 'CONFIDENTIAL');
    body.append('file', file);
    const res = await apiClient.post<ApiResponse<ParcelDocument>>(API_ENDPOINTS.documents.upload, body);
    return res.data.data;
  },
  downloadParcelDocument: (id: string) => apiClient.get<Blob>(API_ENDPOINTS.documents.download(id), { responseType: 'blob' }).then((res) => res.data),
  uploadArchivePage: async (ledgerBookId: string, pageNumber: number, file: File): Promise<ScannedPage> => {
    const body = new FormData();
    body.append('ledger_book_id', ledgerBookId);
    body.append('page_number', String(pageNumber));
    body.append('file', file);
    const res = await apiClient.post<ApiResponse<ScannedPage>>(API_ENDPOINTS.archive.uploadPage, body);
    return res.data.data;
  },
  reviewArchivePage: async (id: string, data: { status: 'REVIEWED' | 'NEEDS_RESCAN'; notes: string }) => {
    const res = await apiClient.post<ApiResponse<ScannedPage>>(API_ENDPOINTS.archive.reviewPage(id), data);
    return res.data.data;
  },
  replaceArchivePageScan: async (id: string, file: File): Promise<ScannedPage> => {
    const body = new FormData();
    body.append('file', file);
    const res = await apiClient.post<ApiResponse<ScannedPage>>(API_ENDPOINTS.archive.rescanPage(id), body);
    return res.data.data;
  },
  downloadArchivePage: (id: string) => apiClient.get<Blob>(API_ENDPOINTS.archive.downloadPage(id), { responseType: 'blob' }).then((res) => res.data),
  triggerPageOcr: async (pageId: string): Promise<{ scanned_page_id: string; status: string }> => {
    const res = await apiClient.post<ApiResponse<{ scanned_page_id: string; status: string }>>(
      API_ENDPOINTS.archive.triggerOcr(pageId)
    );
    return res.data.data;
  },
  searchArchivePages: (query: string, parishId?: string) =>
    getData<ScannedPage[]>(API_ENDPOINTS.archive.searchPages, { query, ...(parishId ? { parish_id: parishId } : {}) }),
  listArchiveDocuments: (parishId: string, dispositionStatus?: string) =>
    getData<ArchiveDocument[]>(API_ENDPOINTS.documents.list, { parish_id: parishId, ...(dispositionStatus ? { disposition_status: dispositionStatus } : {}) }),
  downloadArchiveDocument: (id: string) => apiClient.get<Blob>(API_ENDPOINTS.documents.download(id), { responseType: 'blob' }).then((res) => res.data),
  reviewDocumentDisposition: async (id: string, action: 'DISPOSE' | 'PRESERVE' | 'REOPEN', reason: string) => {
    const res = await apiClient.post<ApiResponse<ArchiveDocument>>(API_ENDPOINTS.documents.disposition(id), { action, reason });
    return res.data.data;
  },

  // Sacraments
  listBaptisms: (parishId?: string) => getData<BaptismRecord[]>(API_ENDPOINTS.sacraments.baptism, parishId ? { parish_id: parishId } : undefined),
  listConfirmations: (parishId?: string) => getData<ConfirmationRecord[]>(API_ENDPOINTS.sacraments.confirmation, parishId ? { parish_id: parishId } : undefined),
  listMatrimonies: (parishId?: string) => getData<MatrimonyRecord[]>(API_ENDPOINTS.sacraments.matrimony, parishId ? { parish_id: parishId } : undefined),
  getSacramentalRecord: (type: string, id: string) => getData<Record<string, unknown>>(API_ENDPOINTS.sacraments.recordDetail(type, id)),
  createBaptism: async (data: Record<string, unknown>): Promise<BaptismRecord> => {
    const res = await apiClient.post<ApiResponse<BaptismRecord>>(API_ENDPOINTS.sacraments.baptism, data);
    return res.data.data;
  },
  createConfirmation: async (data: Record<string, unknown>): Promise<ConfirmationRecord> => {
    const res = await apiClient.post<ApiResponse<ConfirmationRecord>>(API_ENDPOINTS.sacraments.confirmation, data);
    return res.data.data;
  },
  createMatrimony: async (data: Record<string, unknown>): Promise<MatrimonyRecord> => {
    const res = await apiClient.post<ApiResponse<MatrimonyRecord>>(API_ENDPOINTS.sacraments.matrimony, data);
    return res.data.data;
  },
  issueCertificate: async (data: { sacrament_type: string; faithful_id: string; parish_id: string; source_record_id: string }): Promise<CertificateIssuance> => {
    const res = await apiClient.post<ApiResponse<CertificateIssuance>>(API_ENDPOINTS.sacraments.issueCertificate, data);
    return res.data.data;
  },
  downloadCertificate: async (certificateId: string): Promise<void> => {
    const response = await apiClient.get(`/sacraments/certificates/${certificateId}/pdf`, {
      responseType: 'blob',
    });
    const url = URL.createObjectURL(response.data);
    const link = document.createElement('a');
    link.href = url;
    link.download = `certificate-${certificateId}.pdf`;
    link.click();
    URL.revokeObjectURL(url);
  },
  verifyCertificate: (token: string) => getData<CertificateVerification>(API_ENDPOINTS.sacraments.verifyCertificate(token)),
  requestAmendment: async (data: Record<string, unknown>): Promise<SacramentalAmendment> => {
    const res = await apiClient.post<ApiResponse<SacramentalAmendment>>(API_ENDPOINTS.sacraments.amendments, data);
    return res.data.data;
  },
  listAmendments: (status?: string) => getData<SacramentalAmendment[]>(API_ENDPOINTS.sacraments.amendments, status ? { status } : undefined),
  reviewAmendment: async (id: string, action: 'APPROVE' | 'REJECT', reviewNotes: string): Promise<SacramentalAmendment> => {
    const res = await apiClient.post<ApiResponse<SacramentalAmendment>>(API_ENDPOINTS.sacraments.reviewAmendment(id), {
      action,
      review_notes: reviewNotes,
    });
    return res.data.data;
  },

  // Statistics & Indicators
  listAnnualReports: (year?: number) => getData<AnnualReport[]>(API_ENDPOINTS.statistics.parishReports, year ? { year } : undefined),
  reconcileAnnualReport: (parishId: string, year: number) => getData<ParishReportReconciliation[]>(API_ENDPOINTS.statistics.reconcileParishReport(parishId, year)),
  submitParishReport: async (data: Record<string, unknown>): Promise<AnnualReport> => {
    const res = await apiClient.post<ApiResponse<AnnualReport>>(API_ENDPOINTS.statistics.submitReport, data);
    return res.data.data;
  },
  getAnnuarioPontificio: (year: number) => getData<AnnuarioPontificioReport>(API_ENDPOINTS.statistics.annuarioPontificio, { year }),
  listIndicators: () => getData<IndicatorConfigView[]>(API_ENDPOINTS.statistics.indicators),
  computeIndicator: (key: string, params?: { year?: number; deanery_id?: string; archdiocese_id?: string }) =>
    getData<IndicatorResult>(API_ENDPOINTS.statistics.computeIndicator(key), params as Record<string, unknown> | undefined),
};



