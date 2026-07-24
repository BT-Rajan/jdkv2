const FALLBACK_MESSAGE = "Something went wrong. Please try again.";

// Mirrors app/core/errors.py on the backend. Kept as a fallback map here so
// the UI has a sensible message even if the backend's own `message` field is
// ever missing - the backend's message is always preferred when present.
const MESSAGES: Record<string, string> = {
  authentication_required: "Please sign in to continue.",
  invalid_or_expired_session: "Your session has expired. Please sign in again.",
  validation_error: "Please check the information you entered.",
  not_found: "The requested resource was not found.",
  conflict: "This action conflicts with the current state of the record.",
  invalid_credentials: "Invalid email or password.",
  account_not_authenticatable: "This account cannot sign in right now. Please verify your email or contact an administrator.",
  account_locked: "This account is temporarily locked due to repeated failed sign-in attempts.",
  invalid_token: "This link is invalid. Please request a new one.",
  expired_token: "This link has expired. Please request a new one.",
  token_already_used: "This link has already been used.",
  too_many_attempts: "Too many attempts. Please wait a while before trying again.",
  authorization_denied: "You do not have permission to do that.",
  network_error: "Couldn't reach the server. Check your connection and try again.",
};

export interface ApiErrorBody {
  code: string;
  message?: string;
}

export function resolveErrorMessage(body: ApiErrorBody | null, fallbackCode: string): string {
  if (body?.message) return body.message;
  const code = body?.code || fallbackCode;
  return MESSAGES[code] || FALLBACK_MESSAGE;
}
