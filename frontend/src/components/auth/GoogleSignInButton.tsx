import { GoogleLogin } from "@react-oauth/google";
import type { CredentialResponse } from "@react-oauth/google";
import { useNavigate } from "react-router-dom";
import { AxiosError } from "axios";

import { useAuth } from "../../hooks/useAuth";
import { extractErrorMessage } from "../../utils/ExtractErrorMessage";
import { decodeToken } from "../../utils/jwt";

interface GoogleSignInButtonProps {
  onError: (message: string) => void;
  disabled?: boolean;
}

export function GoogleSignInButton({ onError, disabled }: GoogleSignInButtonProps) {
  const navigate = useNavigate();
  const { loginWithGoogle } = useAuth();

  const handleSuccess = async (credentialResponse: CredentialResponse) => {
    const idToken = credentialResponse.credential;
    if (!idToken) {
      onError("Google didn't return a valid credential. Try again.");
      return;
    }

    try {
      // Google's own ID token carries the real name/picture — grab it
      // before the token is handed off, since our backend's response
      // doesn't return a user object to get it from otherwise.
      const googleClaims = decodeToken(idToken);
      await loginWithGoogle(idToken, googleClaims?.name);
      navigate("/dashboard");
    } catch (err) {
      const message =
        err instanceof AxiosError
          ? extractErrorMessage(err, "Couldn't sign in with Google. Try again.")
          : "Network error — check your connection and try again.";
      onError(message);
    }
  };

  return (
    <div className={disabled ? "pointer-events-none opacity-50" : ""}>
      <GoogleLogin
        onSuccess={handleSuccess}
        onError={() => onError("Google sign-in was cancelled or failed. Try again.")}
        theme="filled_black"
        shape="rectangular"
        size="large"
        width="100%"
      />
    </div>
  );
}
