export type UserRole = 'caregiver' | 'patient_adult' | 'clinician' | 'moderator' | 'admin';

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

export interface ConsentAgreementInput {
  terms_accepted: boolean;
  privacy_policy_accepted: boolean;
  ai_safety_disclaimer_accepted: boolean;
}

export interface RegisterRequest {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  consents?: ConsentAgreementInput;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponseData {
  user: User;
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface AuthMeResponseData {
  user: User;
  patient_count: number;
}

export interface LogoutResponseData {
  message: string;
}
