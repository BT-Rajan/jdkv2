import { apiFetch } from "./api";
import { qs } from "./query";
import type { Customer } from "../types";

export interface CustomerSearchParams {
  q?: string;
  status?: string;
  limit?: number;
  offset?: number;
}

export const customersApi = {
  search: (params: CustomerSearchParams = {}) =>
    apiFetch<{ customers: Customer[]; total: number }>(`/api/customers${qs(params)}`),

  get: (id: number) => apiFetch<Customer>(`/api/customers/${id}`),

  create: (body: Partial<Customer>) => apiFetch<Customer>("/api/customers", { method: "POST", body }),

  update: (id: number, body: Partial<Customer>) =>
    apiFetch<Customer>(`/api/customers/${id}`, { method: "PATCH", body }),

  deactivate: (id: number) => apiFetch<Customer>(`/api/customers/${id}/deactivate`, { method: "POST" }),
};
