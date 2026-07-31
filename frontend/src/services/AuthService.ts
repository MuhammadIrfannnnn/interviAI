import api from "./api";
import type {
  AuthResponse,
  LoginPayload,
  RegisterPayload,
  RegisterResponse,
  VerifyOtpPayload,
  ResendOtpPayload,
  ForgotPasswordPayload,
  ResetPasswordPayload,
  GoogleLoginPayload,
} from "../types/Auth";

export const authService = {
  async login(payload: LoginPayload): Promise<AuthResponse> {
    const { data } = await api.post<AuthResponse>("/auth/login", payload);
    return data;
  },

  // Register no longer logs the user in directly — it creates an
  // unverified account and triggers an OTP email. Call verifyOtp next.
  async register(payload: RegisterPayload): Promise<RegisterResponse> {
    const { data } = await api.post<RegisterResponse>("/auth/register", payload);
    return data;
  },

  async verifyOtp(payload: VerifyOtpPayload): Promise<AuthResponse> {
    const { data } = await api.post<AuthResponse>("/auth/verify-otp", payload);
    return data;
  },

  async resendOtp(payload: ResendOtpPayload): Promise<{ message: string }> {
    const { data } = await api.post<{ message: string }>("/auth/resend-otp", payload);
    return data;
  },

  async forgotPassword(payload: ForgotPasswordPayload): Promise<{ message: string }> {
    const { data } = await api.post<{ message: string }>("/auth/forgot-password", payload);
    return data;
  },

  async resetPassword(payload: ResetPasswordPayload): Promise<{ message: string }> {
    const { data } = await api.post<{ message: string }>("/auth/reset-password", payload);
    return data;
  },

  async googleLogin(payload: GoogleLoginPayload): Promise<AuthResponse> {
    const { data } = await api.post<AuthResponse>("/auth/google", payload);
    return data;
  },
};