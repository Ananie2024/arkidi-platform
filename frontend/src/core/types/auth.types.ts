export type UserRole =
  | 'SUPER_ADMIN'
  | 'CHANCELLOR'
  | 'ECONOMO'
  | 'DEAN'
  | 'PARISH_PRIEST'
  | 'PARISH_VICAR'
  | 'PARISH_SECRETARY'
  | 'MINISTRY_LEADER'
  | 'READ_ONLY_AUDITOR';

export interface UserProfile {
  sub: string;
  email: string;
  username: string;
  full_name?: string;
  role: UserRole;
  parish_id?: string | null;
  deanery_id?: string | null;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}
