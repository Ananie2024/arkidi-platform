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
  cell?: string | null;
  village?: string | null;
  parish_id: string;
  deanery_id?: string | null;
  geojson_geometry?: {
    type: string;
    coordinates: any;
  } | null;
  created_at: string;
}

export interface BuildingAsset {
  id: string;
  parcel_id: string;
  name: string;
  building_type: string;
  construction_year?: number | null;
  floors_count: number;
  condition: string;
  created_at: string;
}

export interface BuildingAssetCreate {
  parcel_id: string;
  name: string;
  building_type?: string;
  construction_year?: number | null;
  floors_count?: number;
  condition?: string;
}

