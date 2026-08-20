export type SacramentType =
  | 'BAPTISM'
  | 'FIRST_COMMUNION'
  | 'CONFIRMATION'
  | 'MATRIMONY'
  | 'HOLY_ORDERS'
  | 'RELIGIOUS_PROFESSION'
  | 'ANOINTING_OF_THE_SICK'
  | 'CHRISTIAN_FUNERAL';

export interface BaptismRecord {
  id: string;
  parish_id: string;
  faithful_id: string;
  registry_year: number;
  volume_number: string;
  page_number: string;
  act_number: string;
  celebration_date: string;
  minister_name: string;
  godfather_name?: string | null;
  godmother_name?: string | null;
  marginal_notes?: string | null;
  created_at: string;
}

export interface CertificateIssue {
  id: string;
  certificate_number: string;
  sacrament_type: SacramentType;
  faithful_id: string;
  parish_id: string;
  verification_token: string;
  qr_code_base64: string;
  created_at: string;
}
