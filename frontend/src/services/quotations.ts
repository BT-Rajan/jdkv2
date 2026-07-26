import { apiFetch } from "./api";
import { qs } from "./query";
import type { Quotation, Order } from "../types";

export const quotationsApi = {
  search: (params: { customer_id?: number; status?: string; limit?: number; offset?: number } = {}) =>
    apiFetch<{ quotations: Quotation[]; total: number }>(`/api/quotations${qs(params)}`),

  get: (id: string) => apiFetch<Quotation>(`/api/quotations/${id}`),

  create: (body: { feasibility_id: string; unit_price: number; valid_until?: string; terms?: string; notes?: string }) =>
    apiFetch<Quotation>("/api/quotations", { method: "POST", body }),

  update: (id: string, body: Partial<Pick<Quotation, "unit_price" | "valid_until" | "terms" | "notes">>) =>
    apiFetch<Quotation>(`/api/quotations/${id}`, { method: "PATCH", body }),

  setStatus: (id: string, status: string) =>
    apiFetch<Quotation>(`/api/quotations/${id}/status`, { method: "POST", body: { status } }),

  amend: (id: string, body: Partial<Pick<Quotation, "unit_price" | "valid_until" | "terms" | "notes">>) =>
    apiFetch<Quotation>(`/api/quotations/${id}/amend`, { method: "PATCH", body }),

  convertToOrder: (id: string, body: {
    order_date?: string; delivery_date: string; bag_size_kg?: number; priority?: string; notes?: string;
  }) => apiFetch<Order>(`/api/quotations/${id}/convert-to-order`, { method: "POST", body }),
};
