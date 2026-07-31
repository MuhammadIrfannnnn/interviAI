import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { AxiosError } from "axios";

import { AuthLayout } from "../../layouts/AuthLayout";
import { Button } from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";
import { OtpInput } from "../../components/ui/OtpInput";
import { authService } from "../../services/AuthService";

export default function ResetPassword() {
  const navigate = useNavigate();
  const location = useLocation();
  const stateEmail = (location.state as { email?: string } | null)?.email;

  const [email, setEmail] = useState(stateEmail ?? "");
  const [otp, setOtp] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    if (!email.trim()) return setErrorMessage("Enter your email.");
    if (otp.length !== 6) return setErrorMessage("Enter the 6-digit code.");
    if (newPassword.length < 8) return setErrorMessage("Password must be at least 8 characters.");
    if (newPassword !== confirmPassword) return setErrorMessage("Passwords don't match.");

    setIsSubmitting(true);
    try {
      await authService.resetPassword({ email: email.trim(), otp, new_password: newPassword });
      navigate("/login", { state: { justReset: true } });
    } catch (err) {
      const message =
        err instanceof AxiosError
          ? (err.response?.data?.detail as string) ?? "Invalid or expired code."
          : "Something went wrong. Try again.";
      setErrorMessage(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AuthLayout title="Reset your password" subtitle="Enter the code we sent you and a new password.">
      <form onSubmit={handleSubmit} className="flex flex-col gap-4" noValidate>
        {!stateEmail && (
          <Input
            label="Email"
            type="email"
            autoComplete="email"
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        )}

        <div className="flex flex-col gap-1.5">
          <label className="text-sm font-medium text-text-secondary">Verification code</label>
          <OtpInput value={otp} onChange={setOtp} disabled={isSubmitting} />
        </div>

        <Input
          label="New password"
          type="password"
          autoComplete="new-password"
          placeholder="At least 8 characters"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
        />
        <Input
          label="Confirm new password"
          type="password"
          autoComplete="new-password"
          placeholder="••••••••"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
        />

        {errorMessage && (
          <p
            role="alert"
            className="rounded-md border border-danger bg-danger-soft px-3 py-2 text-sm text-danger"
          >
            {errorMessage}
          </p>
        )}

        <Button type="submit" isLoading={isSubmitting} className="mt-2 w-full">
          Reset password
        </Button>
      </form>

      <p className="mt-6 text-sm text-text-secondary">
        <Link to="/forgot-password" className="font-medium text-accent hover:text-accent-hover">
          Didn't get a code? Request a new one
        </Link>
      </p>
    </AuthLayout>
  );
}
