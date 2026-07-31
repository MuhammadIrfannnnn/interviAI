import { AxiosError } from "axios";

interface FastAPIValidationError {
  type: string;
  loc: (string | number)[];
  msg: string;
  input?: unknown;
}

/**
 * FastAPI's error responses come in two shapes:
 *  - { detail: "some string" }                     — simple HTTPException
 *  - { detail: [{ type, loc, msg, input }, ...] }   — 422 validation errors
 * This normalizes both into a single string safe to render in JSX.
 */
export function extractErrorMessage(err: unknown, fallback: string): string {
  if (!(err instanceof AxiosError)) return fallback;

  const detail = err.response?.data?.detail;

  if (!detail) return fallback;
  if (typeof detail === "string") return detail;

  if (Array.isArray(detail)) {
    const messages = (detail as FastAPIValidationError[])
      .map((item) => {
        const field = item.loc?.[item.loc.length - 1];
        return field ? `${field}: ${item.msg}` : item.msg;
      })
      .filter(Boolean);
    if (messages.length) return messages.join(" · ");
  }

  return fallback;
}