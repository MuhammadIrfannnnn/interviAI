import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { AxiosError } from "axios";
import { AuthLayout } from "../../layouts/AuthLayout";
import { Input } from "../../components/ui/Input";
import { Button } from "../../components/ui/Button";
import { loginSchema } from "../../utils/validation/authSchemas";
import type { LoginFormValues } from "../../utils/validation/authSchemas";
import { useAuth } from "../../hooks/useAuth";
import { extractErrorMessage } from "../../utils/ExtractErrorMessage";
import { GoogleSignInButton } from "../../components/auth/GoogleSignInButton";

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();
  const [formError, setFormError] = useState<string | null>(null);
  const justReset = (location.state as { justReset?: boolean } | null)?.justReset;

  const {
    register,
    handleSubmit,
    getValues,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormValues>({ resolver: zodResolver(loginSchema) });

  const onSubmit = async (values: LoginFormValues) => {
    setFormError(null);
    try {
      await login(values);
      navigate("/dashboard");
    } catch (err) {
      // Unverified accounts get a 403 — send them straight to the OTP
      // screen instead of showing a generic auth error.
      if (err instanceof AxiosError && err.response?.status === 403) {
        navigate("/verify-otp", { state: { email: getValues("email") } });
        return;
      }
      setFormError(extractErrorMessage(err, "Invalid email or password."));
    }
  };

  return (
    <AuthLayout
      title="Welcome back"
      subtitle="Sign in to continue your practice interviews."
    >
      {justReset && (
        <p className="mb-4 rounded-md border border-accent-muted bg-accent-soft px-3 py-2 text-sm text-accent">
          Password reset — sign in with your new password.
        </p>
      )}

      <GoogleSignInButton onError={setFormError} disabled={isSubmitting} />

      <div className="my-5 flex items-center gap-3">
        <div className="h-px flex-1 bg-border-subtle" />
        <span className="text-xs text-text-muted">or</span>
        <div className="h-px flex-1 bg-border-subtle" />
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4" noValidate>
        <Input
          label="Email"
          type="email"
          autoComplete="email"
          placeholder="you@example.com"
          error={errors.email?.message}
          {...register("email")}
        />
        <div>
          <Input
            label="Password"
            type="password"
            autoComplete="current-password"
            placeholder="••••••••"
            error={errors.password?.message}
            {...register("password")}
          />
          <Link
            to="/forgot-password"
            className="mt-1.5 inline-block text-xs text-text-secondary hover:text-accent"
          >
            Forgot password?
          </Link>
        </div>

        {formError && (
          <p role="alert" className="rounded-md border border-danger bg-danger-soft px-3 py-2 text-sm text-danger">
            {formError}
          </p>
        )}

        <Button type="submit" isLoading={isSubmitting} className="mt-2 w-full">
          Sign in
        </Button>
      </form>

      <p className="mt-6 text-sm text-text-secondary">
        Don't have an account?{" "}
        <Link to="/register" className="font-medium text-accent hover:text-accent-hover">
          Create one
        </Link>
      </p>
    </AuthLayout>
  );
}
