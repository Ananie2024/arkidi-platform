import { Faithful } from '../core/types/faithful.types';
import { BaptismRecord } from '../core/types/sacrament.types';
import { LandParcel } from '../core/types/land.types';
import type {
  Deanery,
  Parish,
  Priest,
  Donation,
  MassSchedule,
  Ministry,
  ArchiveBook,
  AnnualReport,
  AnnuarioPontificioReport,
} from '../core/api/domain';

/**
 * Shared domain fixtures for module-page tests. Every object is typed against
 * the real API contracts so drift between `core/api/domain` and the fixtures
 * fails the type check.
 */

export const deaneryFixture: Deanery = {
  id: 'deanery-1',
  archdiocese_id: 'arch-1',
  name: 'Deanery of Kigali Centre',
  code: 'DOY-KGL-01',
  vicar_forane_name: 'Fr. Jean Mutangana',
  created_at: '2024-01-15T08:00:00Z',
};

export const parishFixture: Parish = {
  id: 'parish-1',
  deanery_id: 'deanery-1',
  name: 'Sainte Famille Parish',
  code: 'PAR-SF-01',
  patron_saint: 'Holy Family',
  establishment_date: '1933-09-08',
  phone: '+250788111222',
  email: 'saintefamille@kigali.cat',
  address: 'KN 2 Ave, Kigali',
  latitude: -1.9536,
  longitude: 30.0606,
  district: 'Nyarugenge',
  sector: 'Nyamirambo',
  created_at: '2024-01-15T08:00:00Z',
};

export const priestFixture: Priest = {
  id: 'priest-1',
  first_name: 'Jean',
  last_name: 'Uwimana',
  title: 'Abbé',
  clergy_type: 'DIOCESAN',
  date_of_birth: '1975-04-12',
  ordaining_bishop: 'Msgr. Antoine Kambanda',
  congregation: null,
  phone_number: '+250788333444',
  email: 'abbe.uwimana@kigali.cat',
  biography: 'Ordained in 2003; served in three parishes.',
  status: 'ACTIVE_DUTY',
  ordination_date: '2003-08-15',
  current_parish_id: 'parish-1',
  current_role: 'Parish Priest',
};

export const faithfulFixture: Faithful = {
  id: 'faithful-1',
  registration_number: 'REG-2026-0001',
  first_name: 'Alice',
  last_name: 'Mukamana',
  christian_name: 'Marie',
  gender: 'FEMALE',
  date_of_birth: '1990-06-01',
  place_of_birth: 'Kigali',
  phone_number: '+250788555666',
  email: 'alice@example.com',
  canonical_status: 'CONFIRMED',
  parish_id: 'parish-1',
  family_id: 'family-1',
  scc_id: 'scc-1',
  created_at: '2026-01-10T10:00:00Z',
};

export const donationFixture: Donation = {
  id: 'donation-1',
  receipt_number: 'RC-2026-0042',
  donation_type: 'TITHE',
  donor_name_override: 'Mukamana Alice',
  amount: 25000,
  currency: 'RWF',
  payment_method: 'MOMO',
  donation_date: '2026-03-01',
};

export const massScheduleFixture: MassSchedule = {
  id: 'mass-1',
  mass_date: '2026-03-08',
  start_time: '09:30',
  language: 'KINYARWANDA',
  celebrant_name: 'Abbé Uwimana',
  liturgical_feast: 'Second Sunday of Lent',
};

export const ministryFixture: Ministry = {
  id: 'ministry-1',
  name: 'Chorale Sainte Cécile',
  category: 'CHOIR',
  leader_name: 'Kelly Irakoze',
  meeting_schedule: 'Saturdays 15:00',
  is_active: true,
};

export const archiveBookFixture: ArchiveBook = {
  id: 'book-1',
  book_title: 'Registre des Baptêmes 1920-1935',
  sacrament_type: 'BAPTISM',
  volume_number: 'I',
  start_year: 1920,
  end_year: 1935,
  shelf_location: 'Salle A / Étagère 3',
};

export const annualReportFixture: AnnualReport = {
  id: 'report-1',
  parish_id: 'parish-1',
  report_year: 2026,
  total_catholic_population: 5200,
  infant_baptisms: 61,
  adult_baptisms: 9,
  confirmations: 44,
  marriages_both_catholic: 17,
  marriages_mixed_religion: 5,
};

export const annuarioFixture: AnnuarioPontificioReport = {
  year: 2026,
  total_parishes: 27,
  total_priests: 142,
  total_catholics: 480000,
  total_baptisms: 3100,
  total_confirmations: 1850,
  total_marriages: 640,
};

export const landParcelFixture: LandParcel = {
  id: 'parcel-1',
  upi: '1/02/07/02/1234',
  parcel_name: 'Paroisse Sainte Famille Compound',
  title_deed_number: 'TD-2021-556677',
  land_use: 'CHURCH_COMPOUND',
  tenure_status: 'FREEHOLD',
  area_sqm: 12450.5,
  acquisition_date: '1955-01-01',
  estimated_value_rwf: 450000000,
  province: 'Kigali City',
  district: 'Nyarugenge',
  sector: 'Nyamirambo',
  parish_id: 'parish-1',
  deanery_id: 'deanery-1',
  created_at: '2024-02-01T08:00:00Z',
};

export const baptismFixture: BaptismRecord = {
  id: 'baptism-1',
  parish_id: 'parish-1',
  faithful_id: 'faithful-1',
  registry_year: 1923,
  volume_number: 'I',
  page_number: '42',
  act_number: 'B-1923-118',
  celebration_date: '1923-05-20',
  minister_name: 'Père Léon Classe',
  godfather_name: 'Joseph Habimana',
  godmother_name: 'Marie Nyirabagenzi',
  marginal_notes: null,
  created_at: '1923-05-20T00:00:00Z',
};
