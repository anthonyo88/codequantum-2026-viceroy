import { apiClient } from "./client";
import type { LoginRequest, RegisterRequest, TokenResponse } from "@/lib/types/auth";

export async function login(data: LoginRequest): Promise<TokenResponse> {
  const res = await apiClient.post<TokenResponse>("/api/v1/auth/login", data);
  return res.data;
}

export async function register(data: RegisterRequest): Promise<TokenResponse> {
  const res = await apiClient.post<TokenResponse>("/api/v1/auth/register", {
    company_name: data.company_name,
    company_type: data.company_type,
    contact_email: data.contact_email,
    password: data.password,
  });
  return res.data;
}

export async function refreshTokens(refreshToken: string): Promise<TokenResponse> {
  const res = await apiClient.post<TokenResponse>("/api/v1/auth/refresh", {
    refresh_token: refreshToken,
  });
  return res.data;
}

export async function logout(): Promise<void> {
  await apiClient.post("/api/v1/auth/logout").catch(() => {});
}
