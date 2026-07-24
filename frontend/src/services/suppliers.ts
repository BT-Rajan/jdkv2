import { apiFetch } from "./api";
import { qs } from "./query";
import type { Supplier } from "../types";

export interface SupplierSearchParams {
  q?: string;
  category?: string;
  status?: string;
  limit?: number;
  offset?: number;
}

export const suppliersApi = {
  search: (params: SupplierSearchParams = {}) =>
    apiFetch<{ suppliers: Supplier[]; total: number }>(`/api/suppliers${qs(params)}`),

  get: (id: number) => apiFetch<Supplier>(`/api/suppliers/${id}`),

  create: (body: Partial<Supplier>) => apiFetch<Supplier>("/api/suppliers", { method: "POST", body }),

  update: (id: number, body: Partial<Supplier>) =>
    apiFetch<Supplier>(`/api/suppliers/${id}`, { method: "PATCH", body }),

  deactivate: (id: number) => apiFetch<Supplier>(`/api/suppliers/${id}/deactivate`, { method: "POST" }),

  setSupplyTerms: (id: number, body: {
    material_id: number; price: number; lead_time_days: number;
    minimum_order_qty: number; payment_terms?: string; delivery_cost: number;
  }) => apiFetch<Supplier>(`/api/suppliers/${id}/supply-terms`, { method: "PUT", body }),
};
