export type LandUseType =
  | 'CHURCH_COMPOUND'
  | 'CENTRALE_CHAPEL'
  | 'HEALTH_FACILITY'
  | 'EDUCATIONAL'
  | 'AGRICULTURAL'
  | 'COMMERCIAL_RENTAL'
  | 'CONVENT_MONASTERY'
  | 'CEMETERY'
  | 'VACANT_RESERVE';

export type TenureStatus =
  | 'FREEHOLD'
  | 'EMPHYTEUTIC_LEASE'
  | 'DISPUTED'
  | 'IN_REGISTRATION';

export interface LandParcel {
  id: string;
  upi: string;
  parcel_name: string;
  title_deed_number?: string | null;
  land_use: LandUseType;
  tenure_status: TenureStatus;
  area_sqm: number;
  acquisition_date?: string | null;
  estimated_value_rwf?: number | null;
  province: string;
  district?: string | null;
  sector?: string | null;
  parish_id: string;
  deanery_id?: string | null;
  created_at: string;
}
