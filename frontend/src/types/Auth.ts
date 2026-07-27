export interface User {
  id: string;
  email: string;
  full_name?: string;
  role?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  // NOTE: confirmed that POST /auth/login does NOT return this — only
  // access_token and token_type. Keeping this optional in case /auth/register
  // differs. User info is derived from the decoded JWT instead (see
  // utils/jwt.ts and AuthContext.tsx).
  user?: User;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  full_name: string;
  email: string;
  password: string;
}