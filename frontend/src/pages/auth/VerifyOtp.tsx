import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { AxiosError } from "axios";

import { AuthLayout } from "../../layouts/AuthLayout";
import { Button } from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";
import { OtpInput } from "../../components/ui/OtpInput";
import { authService } from "../../services/AuthService";
import { useAuth } from "../../hooks/useAuth";

const RESEND_COOLDOWN_SECONDS = 45;

export default function VerifyOtp() {
  const navigate = useNavigate();
  const location = useLocation();
  const { completeVerification } = useAuth();

  // Email normally arrives via route state from Register. If someone lands
  // here directly (e.g. refreshed the page and lost state), fall back to
  // asking for it manually rather than dead-ending them.
  const stateEmail = (location.state as { email?: string; fullName?: string } | null)?.email;
  const stateFullName = (location.state as { email?: string; fullName?: string } | null)?.fullName;
  const [email, setEmail] = useState(stateEmail ?? "");
  const [otp, setOtp] = useState("");
  const [isVerifying, setIsVerifying] = useState(false);
  const [isResending, setIsResending] = useState(false);
  const [cooldown, setCooldown] = useState(stateEmail ? RESEND_COOLDOWN_SECONDS : 0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [infoMessage, setInfoMessage] = useState<string | null>(null);

  useEffect(() => {
    if (cooldown <= 0) return;
    const timer = setTimeout(() => setCooldown((c) => c - 1), 1000);
    return () => clearTimeout(timer);
  }, [cooldown]);

  const handleVerify = async () => {
    if (!email.trim()) {
      setErrorMessage("Enter your email.");
      return;
    }
    if (otp.length !== 6) {
      setErrorMessage("Enter the 6-digit code.");
      return;
    }

    setErrorMessage(null);
    setIsVerifying(true);
    try {
      const { access_token } = await authService.verifyOtp({ email: email.trim(), otp });
      completeVerification(access_token, stateFullName);
      navigate("/resume");
    } catch (err) {
      const message =
        err instanceof AxiosError
          ? (err.response?.data?.detail as string) ?? "Invalid or expired code."
          : "Something went wrong. Try again.";
      setErrorMessage(message);
    } finally {
      setIsVerifying(false);
    }
  };

  const handleResend = async () => {
    if (!email.trim() || cooldown > 0) return;

    setErrorMessage(null);
    setInfoMessage(null);
    setIsResending(true);
    try {
      await authService.resendOtp({ email: email.trim() });
      setInfoMessage("A new code has been sent.");
      setCooldown(RESEND_COOLDOWN_SECONDS);
    } catch {
      setErrorMessage("Couldn't resend the code. Try again shortly.");
    } finally {
      setIsResending(false);
    }
  };

  return (
    <AuthLayout
      title="Verify your email"
      subtitle={
        stateEmail
          ? `Enter the 6-digit code sent to ${stateEmail}.`
          : "Enter your email and the code you received."
      }
    >
      <div className="flex flex-col gap-4">
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
          <OtpInput value={otp} onChange={setOtp} disabled={isVerifying} />
        </div>

        {errorMessage && (
          <p
            role="alert"
            className="rounded-md border border-danger bg-danger-soft px-3 py-2 text-sm text-danger"
          >
            {errorMessage}
          </p>
        )}
        {infoMessage && (
          <p className="rounded-md border border-accent-muted bg-accent-soft px-3 py-2 text-sm text-accent">
            {infoMessage}
          </p>
        )}

        <Button onClick={handleVerify} isLoading={isVerifying} className="mt-1 w-full">
          Verify
        </Button>

        <button
          onClick={handleResend}
          disabled={cooldown > 0 || isResending}
          className="text-sm text-accent hover:text-accent-hover disabled:cursor-not-allowed disabled:text-text-muted"
        >
          {cooldown > 0 ? `Resend code in ${cooldown}s` : isResending ? "Sending…" : "Resend code"}
        </button>
      </div>

      <p className="mt-6 text-sm text-text-secondary">
        Wrong email?{" "}
        <Link to="/register" className="font-medium text-accent hover:text-accent-hover">
          Go back
        </Link>
      </p>
    </AuthLayout>
  );
}
