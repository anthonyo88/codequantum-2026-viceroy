"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from "react";
import {
  login as apiLogin,
  register as apiRegister,
  logout as apiLogout,
  refreshTokens,
} from "@/lib/api/auth";
import {
  setAccessToken,
  setRefreshToken,
  getRefreshToken,
  clearTokens,
  setSessionCookie,
} from "@/lib/api/client";
import type { AuthUser, LoginRequest, RegisterRequest } from "@/lib/types/auth";

interface AuthContextValue {
  user: AuthUser | null;
  isLoading: boolean;
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Silent refresh on mount
  useEffect(() => {
    const refreshToken = getRefreshToken();
    if (!refreshToken) {
      setIsLoading(false);
      return;
    }

    refreshTokens(refreshToken)
      .then((tokens) => {
        setAccessToken(tokens.access_token);
        setRefreshToken(tokens.refresh_token);
        setSessionCookie();
        // Decode the JWT payload to get user info
        const payload = parseJwtPayload(tokens.access_token);
        if (payload) setUser(payload);
      })
      .catch(() => {
        clearTokens();
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, []);

  async function login(data: LoginRequest) {
    const tokens = await apiLogin(data);
    setAccessToken(tokens.access_token);
    setRefreshToken(tokens.refresh_token);
    setSessionCookie();
    const payload = parseJwtPayload(tokens.access_token);
    if (payload) setUser(payload);
  }

  async function register(data: RegisterRequest) {
    const tokens = await apiRegister(data);
    setAccessToken(tokens.access_token);
    setRefreshToken(tokens.refresh_token);
    setSessionCookie();
    const payload = parseJwtPayload(tokens.access_token);
    if (payload) setUser(payload);
  }

  async function logout() {
    await apiLogout();
    clearTokens();
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

function parseJwtPayload(token: string): AuthUser | null {
  try {
    const base64 = token.split(".")[1];
    const decoded = JSON.parse(atob(base64));
    return {
      id: decoded.sub ?? decoded.user_id ?? "",
      email: decoded.email ?? "",
      role: decoded.role ?? "viewer",
      company_id: decoded.company_id ?? "",
      company_name: decoded.company_name ?? "",
    };
  } catch {
    return null;
  }
}
