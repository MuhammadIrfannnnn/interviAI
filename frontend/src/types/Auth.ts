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

// Register no longer returns a token directly — it creates an unverified
// account and triggers an OTP email. The token only arrives after
// POST /auth/verify-otp succeeds.
export interface RegisterResponse {
  message: string;
  email: string;
}

export interface VerifyOtpPayload {
  email: string;
  otp: string;
}

export interface ResendOtpPayload {
  email: string;
}

export interface ForgotPasswordPayload {
  email: string;
}

export interface ResetPasswordPayload {
  email: string;
  otp: string;
  new_password: string;
}

export interface GoogleLoginPayload {
  id_token: string;
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