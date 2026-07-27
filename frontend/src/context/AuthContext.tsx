import { createContext, useEffect, useState } from "react";
import type { ReactNode } from "react";
import { authService } from "../services/AuthService";
import type { LoginPayload, RegisterPayload, User } from "../types/Auth";
import { decodeToken } from "../utils/jwt";

const TOKEN_KEY = "interviai_token";
const USER_KEY = "interviai_user";

export interface AuthContextValue {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (payload: LoginPayload) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => void;
}

// Exported so hooks/useAuth.ts can consume it. Default is undefined so the
// hook can throw a clear error if it's ever used outside the provider.
export const AuthContext = createContext<AuthContextValue | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  // Starts true: we don't know yet whether a stored session exists until
  // the effect below runs, and ProtectedRoute needs to wait for that.
  const [isLoading, setIsLoading] = useState(true);

  // Rehydrate from localStorage on mount. There's no GET /auth/me endpoint
  // in the backend yet, so the user object is cached alongside the token
  // rather than re-fetched. If a /auth/me endpoint gets added later, swap
  // this block to validate the token against it instead.
  useEffect(() => {
    const storedToken = localStorage.getItem(TOKEN_KEY);
    const storedUser = localStorage.getItem(USER_KEY);

    if (storedToken && storedUser) {
      try {
        setToken(storedToken);
        setUser(JSON.parse(storedUser));
      } catch {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
      }
    }

    setIsLoading(false);
  }, []);

  const persistSession = (accessToken: string, sessionUser: User) => {
    localStorage.setItem(TOKEN_KEY, accessToken);
    localStorage.setItem(USER_KEY, JSON.stringify(sessionUser));
    setToken(accessToken);
    setUser(sessionUser);
  };

  // The backend confirmed /auth/login returns only { access_token, token_type }
  // — no user object. We derive id/email/role from the JWT's own claims
  // instead, and layer in full_name from a `user` field if the response
  // ever includes one (e.g. register might differ from login).
  const buildUser = (accessToken: string, responseUser?: User): User => {
    const claims = decodeToken(accessToken);
    return {
      id: responseUser?.id ?? claims?.sub ?? "",
      email: responseUser?.email ?? claims?.email ?? "",
      full_name: responseUser?.full_name,
      role: responseUser?.role ?? claims?.role,
    };
  };

  const login = async (payload: LoginPayload) => {
    const { access_token, user: responseUser } = await authService.login(payload);
    persistSession(access_token, buildUser(access_token, responseUser));
  };

  const register = async (payload: RegisterPayload) => {
    const { access_token, user: responseUser } = await authService.register(payload);
    persistSession(access_token, buildUser(access_token, responseUser));
  };

  const logout = () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    setToken(null);
    setUser(null);
  };

  const value: AuthContextValue = {
    user,
    token,
    isAuthenticated: !!token,
    isLoading,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
