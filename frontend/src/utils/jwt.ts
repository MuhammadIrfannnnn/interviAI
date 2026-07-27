export interface DecodedToken {
  sub: string; // user id
  email: string;
  role?: string;
  exp?: number;
}

/**
 * Decodes a JWT's payload without verifying the signature (verification is
 * the backend's job — this is purely for reading claims client-side, e.g.
 * to populate user info since the login response doesn't return a user
 * object).
 */
export function decodeToken(token: string): DecodedToken | null {
  try {
    const payload = token.split(".")[1];
    const decoded = atob(payload.replace(/-/g, "+").replace(/_/g, "/"));
    return JSON.parse(decoded);
  } catch {
    return null;
  }
}