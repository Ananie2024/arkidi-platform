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
  image_file_path: string;
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
  infant_baptisms: number;
  adult_baptisms: number;
  confirmations: number;
  marriages_both_catholic: number;
  marriages_mixed_religion: number;
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
  name: string;
  description: string;
  category: string;
}

export interface IndicatorResult {
  key: string;
  name: string;
  description: string;
  dimension: string;
  generated_at: string;
  rows: Array<{ label: string; value: number }>;
  metadata: Record<string, unknown>;
}

export interface CertificateIssuance {
  id: string;
  certificate_number: string;
  verification_token: string;
  qr_code_base64: string;
}

async function getData<T>(url: string, params?: Record<string, unknown>): Promise<T> {
  const response = await apiClient.get<ApiResponse<T>>(url, { params });
  return response.data.data;
}

export const domainApi = {
  // Geography
  listDeaneries: () => getData<Deanery[]>(API_ENDPOINTS.geography.deaneries),
  listParishes: (deaneryId?: string | null) => getData<Parish[]>(API_ENDPOINTS.geography.parishes, deaneryId ? { deanery_id: deaneryId } : undefined),
  getParish: (id: string) => getData<Parish>(API_ENDPOINTS.geography.parishDetail(id)),

  // Faithful & Clergy
  getFaithful: (id: string) => getData<Faithful>(API_ENDPOINTS.faithful.detail(id)),
  listFaithful: (search?: string) => getData<PaginatedResult<Faithful>>(API_ENDPOINTS.faithful.list, search ? { search } : undefined),
  getPriest: (id: string) => getData<Priest>(API_ENDPOINTS.clergy.detail(id)),
  listPriests: () => getData<Priest[]>(API_ENDPOINTS.clergy.list),

  // Finance
  listDonations: (parishId: string) => getData<Donation[]>(API_ENDPOINTS.finance.donations, { parish_id: parishId }),
  getDonation: (id: string) => getData<Donation>(API_ENDPOINTS.finance.donationDetail(id)),
  getFinancialSummary: (parishId: string) => getData<FinancialSummary>(API_ENDPOINTS.finance.summary, { parish_id: parishId }),
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
  triggerPageOcr: async (pageId: string): Promise<{ scanned_page_id: string; status: string }> => {
    const res = await apiClient.post<ApiResponse<{ scanned_page_id: string; status: string }>>(
      API_ENDPOINTS.archive.triggerOcr(pageId)
    );
    return res.data.data;
  },
  searchArchivePages: (query: string, parishId?: string) =>
    getData<ScannedPage[]>(API_ENDPOINTS.archive.searchPages, { query, ...(parishId ? { parish_id: parishId } : {}) }),

  // Sacraments
  listBaptisms: (parishId?: string) => getData<BaptismRecord[]>(API_ENDPOINTS.sacraments.baptism, parishId ? { parish_id: parishId } : undefined),
  listConfirmations: (parishId?: string) => getData<ConfirmationRecord[]>(API_ENDPOINTS.sacraments.confirmation, parishId ? { parish_id: parishId } : undefined),
  listMatrimonies: (parishId?: string) => getData<MatrimonyRecord[]>(API_ENDPOINTS.sacraments.matrimony, parishId ? { parish_id: parishId } : undefined),
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
  issueCertificate: async (data: { sacrament_type: string; faithful_id: string; parish_id: string }): Promise<CertificateIssuance> => {
    const res = await apiClient.post<ApiResponse<CertificateIssuance>>(API_ENDPOINTS.sacraments.issueCertificate, data);
    return res.data.data;
  },

  // Statistics & Indicators
  listAnnualReports: (year?: number) => getData<AnnualReport[]>(API_ENDPOINTS.statistics.parishReports, year ? { year } : undefined),
  submitParishReport: async (data: Record<string, unknown>): Promise<AnnualReport> => {
    const res = await apiClient.post<ApiResponse<AnnualReport>>(API_ENDPOINTS.statistics.submitReport, data);
    return res.data.data;
  },
  getAnnuarioPontificio: (year: number) => getData<AnnuarioPontificioReport>(API_ENDPOINTS.statistics.annuarioPontificio, { year }),
  listIndicators: () => getData<IndicatorConfigView[]>(API_ENDPOINTS.statistics.indicators),
  computeIndicator: (key: string, params?: { year?: number; deanery_id?: string; archdiocese_id?: string }) =>
    getData<IndicatorResult>(API_ENDPOINTS.statistics.computeIndicator(key), params as Record<string, unknown> | undefined),
};



