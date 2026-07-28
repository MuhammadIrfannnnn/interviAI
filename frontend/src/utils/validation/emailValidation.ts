// Stricter than Zod's built-in .email(), which accepts things like
// "a@b.c" or trailing/leading dots that most real providers reject.
// This still can't *prove* an email is real/deliverable — only an OTP
// or confirmation link can do that — but it catches the common cases of
// obviously fake or throwaway addresses at signup.

const STRICT_EMAIL_REGEX =
  /^[a-zA-Z0-9](?:[a-zA-Z0-9._%+-]*[a-zA-Z0-9])?@[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?)+$/;

// A representative set of well-known disposable/temp-email providers —
// not exhaustive (no static list ever is), but covers the large majority
// of throwaway signups in practice. Easy to extend as needed.
const DISPOSABLE_DOMAINS = new Set([
  "mailinator.com",
  "guerrillamail.com",
  "guerrillamail.info",
  "10minutemail.com",
  "10minutemail.net",
  "tempmail.com",
  "temp-mail.org",
  "throwawaymail.com",
  "yopmail.com",
  "getnada.com",
  "trashmail.com",
  "fakeinbox.com",
  "mailnesia.com",
  "dispostable.com",
  "sharklasers.com",
  "maildrop.cc",
  "mintemail.com",
  "mytemp.email",
  "moakt.com",
  "spamgourmet.com",
]);

export function isStrictlyValidEmail(email: string): boolean {
  if (!STRICT_EMAIL_REGEX.test(email)) return false;

  const domain = email.split("@")[1]?.toLowerCase();
  if (!domain) return false;

  // Requires at least one dot after the last hyphen-safe label and a
  // TLD of 2+ letters — rules out things like "user@localhost" or "user@test".
  const tld = domain.split(".").pop() ?? "";
  if (tld.length < 2 || !/^[a-zA-Z]+$/.test(tld)) return false;

  return true;
}

export function isDisposableEmailDomain(email: string): boolean {
  const domain = email.split("@")[1]?.toLowerCase();
  return domain ? DISPOSABLE_DOMAINS.has(domain) : false;
}