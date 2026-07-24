import { apiFetch } from "./api";
import { qs } from "./query";
import type { UserSummary, AuditEntry } from "../types";

export interface UserSearchParams {
  q?: string;
  status?: string;
  role?: string;
  limit?: number;
  offset?: number;
}


export const usersApi = {
  search: (params: UserSearchParams = {}) =>
    apiFetch<{ users: UserSummary[]; total: number }>(`/api/users${qs(params)}`),

  get: (subjectId: string) => apiFetch<UserSummary>(`/api/users/${subjectId}`),

  audit: (subjectId: string) => apiFetch<AuditEntry[]>(`/api/users/${subjectId}/audit`),

  create: (body: {
    email: string; initial_password: string; full_name: string;
    phone?: string; department?: string; role: string;
  }) => apiFetch<UserSummary>("/api/users", { method: "POST", body }),

  updateProfile: (subjectId: string, body: { full_name?: string; phone?: string; department?: string }) =>
    apiFetch<UserSummary>(`/api/users/${subjectId}/profile`, { method: "PATCH", body }),

  changeRole: (subjectId: string, role: string) =>
    apiFetch<UserSummary>(`/api/users/${subjectId}/role`, { method: "POST", body: { role } }),

  deactivate: (subjectId: string) =>
    apiFetch<UserSummary>(`/api/users/${subjectId}/deactivate`, { method: "POST" }),
};

export const ASSIGNABLE_ROLES = [
  { code: "operations", label: "Operations" },
  { code: "production", label: "Production" },
  { code: "procurement", label: "Procurement" },
  { code: "executive", label: "Executive" },
  { code: "administrator", label: "Administrator" },
];
