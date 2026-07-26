import { apiFetch } from "./api";
import { qs } from "./query";
import type { FeasibilityRun } from "../types";

export const feasibilityWorkflowApi = {
  search: (params: { customer_id?: number; outcome?: string; status?: string; limit?: number; offset?: number } = {}) =>
    apiFetch<{ runs: FeasibilityRun[]; total: number }>(`/api/feasibility${qs(params)}`),

  get: (id: string) => apiFetch<FeasibilityRun>(`/api/feasibility/${id}`),

  run: (body: { customer_id: number; product_id: number; quantity_kg: number; requested_delivery_date: string; notes?: string }) =>
    apiFetch<FeasibilityRun>("/api/feasibility", { method: "POST", body }),

  amend: (id: string, notes: string | null) =>
    apiFetch<FeasibilityRun>(`/api/feasibility/${id}`, { method: "PATCH", body: { notes } }),
};
