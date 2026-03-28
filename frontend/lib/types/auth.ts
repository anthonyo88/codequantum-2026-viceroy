export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface AuthUser {
  id: string;
  email: string;
  role: "admin" | "scout" | "viewer";
  company_id: string;
  company_name: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  company_name: string;
  company_type: CompanyType;
  contact_email: string;
  password: string;
}

export type CompanyType =
  | "f1_team"
  | "formula2"
  | "formula3"
  | "indycar"
  | "sponsor"
  | "other";

export type SubscriptionTier = "free" | "pro" | "enterprise";

export interface CompanyOut {
  id: string;
  name: string;
  company_type: CompanyType;
  subscription_tier: SubscriptionTier;
  contact_email: string;
  is_verified: boolean;
  query_quota_monthly: number;
  queries_used_this_month: number;
  created_at: string;
}
