export type Gender = 'MALE' | 'FEMALE';

export type CanonicalStatus =
  | 'CATECHUMEN'
  | 'BAPTIZED'
  | 'CONFIRMED'
  | 'CANONICAL_MARRIAGE'
  | 'CIVIL_ONLY'
  | 'CLERGY_OR_RELIGIOUS'
  | 'DECEASED';

export interface Faithful {
  id: string;
  registration_number: string;
  first_name: string;
  last_name: string;
  christian_name: string;
  gender: Gender;
  date_of_birth?: string | null;
  place_of_birth?: string | null;
  phone_number?: string | null;
  email?: string | null;
  canonical_status: CanonicalStatus;
  parish_id: string;
  family_id?: string | null;
  scc_id?: string | null;
  created_at: string;
}
