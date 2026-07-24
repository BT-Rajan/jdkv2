import { config } from "../config";
import { resolveErrorMessage, type ApiErrorBody } from "./errors";

export class ApiError extends Error {
  code: string;
  status: number;
  constructor(code: string, message: string, status: number) {
    super(message);
    this.code = code;
    this.status = status;
  }
}

/**
 * Token storage strategy (documented deliberately - this is the one place
 * it happens):
 *
 *   - The access token lives ONLY in memory (this module's closure). It is
 *     never written to localStorage/sessionStorage, so a successful XSS
 *     read of storage cannot obtain it, and it disappears on tab close.
 *   - The refresh token IS persisted (localStorage), so a page reload
 *     doesn't force a full re-login. This is a deliberate usability/security
 *     trade-off: an XSS bug could still steal the refresh token. The proper
 *     fix is a backend change (httpOnly, Secure, SameSite=strict cookie for
 *     the refresh token) which this codebase does not yet implement - see
 *     README "Known gaps".
 */
const REFRESH_TOKEN_KEY = "jdk_refresh_token";

let accessToken: string | null = null;
let accessTokenExpiresAt: number | null = null;

export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function hasSession(): boolean {
  return !!getRefreshToken();
}

export function setSession(tokens: { access_token: string; access_token_expires_at: number; refresh_token: string }) {
  accessToken = tokens.access_token;
  accessTokenExpiresAt = tokens.access_token_expires_at;
  localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
}

export function setAccessTokenOnly(tokens: { access_token: string; access_token_expires_at: number }) {
  accessToken = tokens.access_token;
  accessTokenExpiresAt = tokens.access_token_expires_at;
}

export function clearSession() {
  accessToken = null;
  accessTokenExpiresAt = null;
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

async function parseErrorBody(response: Response): Promise<ApiErrorBody | null> {
  try {
    const body = await response.json();
    return body?.error ?? null;
  } catch {
    return null;
  }
}

interface FetchOptions {
  method?: string;
  body?: unknown;
  auth?: boolean;
}

async function rawFetch(path: string, options: FetchOptions, withAuth: boolean): Promise<Response> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (withAuth && accessToken) {
    headers["Authorization"] = `Bearer ${accessToken}`;
  }
  try {
    return await fetch(`${config.apiBaseUrl}${path}`, {
      method: options.method || "GET",
      headers,
      body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
    });
  } catch {
    throw new ApiError("network_error", resolveErrorMessage(null, "network_error"), 0);
  }
}

let refreshInFlight: Promise<boolean> | null = null;

async function refreshAccessToken(): Promise<boolean> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return false;

  // Coalesce concurrent 401s into a single refresh call.
  if (!refreshInFlight) {
    refreshInFlight = (async () => {
      const response = await rawFetch(
        "/api/auth/refresh",
        { method: "POST", body: { refresh_token: refreshToken } },
        false,
      );
      if (!response.ok) {
        clearSession();
        return false;
      }
      const data = await response.json();
      setSession(data);
      return true;
    })().finally(() => {
      refreshInFlight = null;
    });
  }
  return refreshInFlight;
}

export async function apiFetch<T = unknown>(path: string, options: FetchOptions = {}): Promise<T> {
  const withAuth = options.auth !== false;
  let response = await rawFetch(path, options, withAuth);

  if (response.status === 401 && withAuth) {
    const refreshed = await refreshAccessToken();
    if (refreshed) {
      response = await rawFetch(path, options, withAuth);
    }
  }

  if (!response.ok) {
    const errorBody = await parseErrorBody(response);
    throw new ApiError(
      errorBody?.code || "unexpected_error",
      resolveErrorMessage(errorBody, "unexpected_error"),
      response.status,
    );
  }

  if (response.status === 204) return null as T;
  return response.json();
}

export async function apiUpload<T = unknown>(path: string, formData: FormData): Promise<T> {
  const headers: Record<string, string> = {};
  if (accessToken) headers["Authorization"] = `Bearer ${accessToken}`;

  let response: Response;
  try {
    response = await fetch(`${config.apiBaseUrl}${path}`, { method: "POST", headers, body: formData });
  } catch {
    throw new ApiError("network_error", resolveErrorMessage(null, "network_error"), 0);
  }

  if (response.status === 401) {
    const refreshed = await refreshAccessToken();
    if (refreshed) {
      headers["Authorization"] = `Bearer ${accessToken}`;
      response = await fetch(`${config.apiBaseUrl}${path}`, { method: "POST", headers, body: formData });
    }
  }

  if (!response.ok) {
    const errorBody = await parseErrorBody(response);
    throw new ApiError(
      errorBody?.code || "unexpected_error",
      resolveErrorMessage(errorBody, "unexpected_error"),
      response.status,
    );
  }
  return response.json();
}

export async function apiDownload(path: string): Promise<{ blob: Blob; filename: string | null }> {
  const headers: Record<string, string> = {};
  if (accessToken) headers["Authorization"] = `Bearer ${accessToken}`;

  let response = await fetch(`${config.apiBaseUrl}${path}`, { headers });
  if (response.status === 401) {
    const refreshed = await refreshAccessToken();
    if (refreshed) {
      headers["Authorization"] = `Bearer ${accessToken}`;
      response = await fetch(`${config.apiBaseUrl}${path}`, { headers });
    }
  }
  if (!response.ok) {
    const errorBody = await parseErrorBody(response);
    throw new ApiError(
      errorBody?.code || "unexpected_error",
      resolveErrorMessage(errorBody, "unexpected_error"),
      response.status,
    );
  }
  const disposition = response.headers.get("Content-Disposition") || "";
  const match = disposition.match(/filename="?([^"]+)"?/);
  return { blob: await response.blob(), filename: match ? match[1] : null };
}
