import { apiClient } from './client';
import { API_ENDPOINTS } from './endpoints';
import { ApiResponse, PaginatedResult } from '../types/common.types';
import { Faithful } from '../types/faithful.types';
import { BaptismRecord } from '../types/sacrament.types';
import { LandParcel } from '../types/land.types';

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
  donation_type: string;
  donor_name_override?: string | null;
  amount: number;
  currency: string;
  payment_method: string;
  donation_date: string;
}

export interface MassSchedule {
  id: string;
  mass_date: string;
  start_time: string;
  language: string;
  celebrant_name?: string | null;
  liturgical_feast?: string | null;
}

export interface Ministry {
  id: string;
  name: string;
  category: string;
  leader_name?: string | null;
  meeting_schedule?: string | null;
  is_active: boolean;
}

export interface ArchiveBook {
  id: string;
  book_title: string;
  sacrament_type: string;
  volume_number: string;
  start_year: number;
  end_year: number;
  shelf_location?: string | null;
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

async function getData<T>(url: string, params?: Record<string, unknown>): Promise<T> {
  const response = await apiClient.get<ApiResponse<T>>(url, { params });
  return response.data.data;
}

export const domainApi = {
  listDeaneries: () => getData<Deanery[]>(API_ENDPOINTS.geography.deaneries),
  listParishes: (deaneryId?: string | null) => getData<Parish[]>(API_ENDPOINTS.geography.parishes, deaneryId ? { deanery_id: deaneryId } : undefined),
getParish: (id: string) => getData<Parish>(API_ENDPOINTS.geography.parishDetail(id)),
  getFaithful: (id: string) => getData<Faithful>(API_ENDPOINTS.faithful.detail(id)),
  getPriest: (id: string) => getData<Priest>(API_ENDPOINTS.clergy.detail(id)),
  listFaithful: (search?: string) => getData<PaginatedResult<Faithful>>(API_ENDPOINTS.faithful.list, search ? { search } : undefined),
  listPriests: () => getData<Priest[]>(API_ENDPOINTS.clergy.list),
  listDonations: (parishId: string) => getData<Donation[]>(API_ENDPOINTS.finance.donations, { parish_id: parishId }),
  listParcels: () => getData<LandParcel[]>(API_ENDPOINTS.landAssets.parcels),
  listMassSchedules: (parishId: string) => getData<MassSchedule[]>(API_ENDPOINTS.liturgy.masses, { parish_id: parishId }),
  listMinistries: () => getData<Ministry[]>(API_ENDPOINTS.ministries.list),
  listArchiveBooks: (parishId: string) => getData<ArchiveBook[]>(API_ENDPOINTS.archive.books, { parish_id: parishId }),
  listBaptisms: (parishId?: string) => getData<BaptismRecord[]>(API_ENDPOINTS.sacraments.baptism, parishId ? { parish_id: parishId } : undefined),
  listConfirmations: (parishId?: string) => getData<ConfirmationRecord[]>(API_ENDPOINTS.sacraments.confirmation, parishId ? { parish_id: parishId } : undefined),
  listMatrimonies: (parishId?: string) => getData<MatrimonyRecord[]>(API_ENDPOINTS.sacraments.matrimony, parishId ? { parish_id: parishId } : undefined),
  listAnnualReports: (year?: number) => getData<AnnualReport[]>(API_ENDPOINTS.statistics.parishReports, year ? { year } : undefined),
  getAnnuarioPontificio: (year: number) => getData<AnnuarioPontificioReport>(API_ENDPOINTS.statistics.annuarioPontificio, { year }),
};

