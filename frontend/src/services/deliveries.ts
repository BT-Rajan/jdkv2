import { apiFetch } from "./api";
import { qs } from "./query";
import type { Delivery } from "../types";

export const deliveriesApi = {
  search: (params: { order_id?: number; status?: string; limit?: number; offset?: number } = {}) =>
    apiFetch<{ deliveries: Delivery[]; total: number }>(`/api/deliveries${qs(params)}`),

  get: (id: string) => apiFetch<Delivery>(`/api/deliveries/${id}`),

  create: (body: {
    order_id: number; delivery_date: string; dispatched_qty_kg: number;
    carrier?: string; tracking_ref?: string; notes?: string;
  }) => apiFetch<Delivery>("/api/deliveries", { method: "POST", body }),

  setStatus: (id: string, status: string) =>
    apiFetch<Delivery>(`/api/deliveries/${id}/status`, { method: "POST", body: { status } }),

  amend: (id: string, body: Partial<{
    delivery_date: string; dispatched_qty_kg: number; carrier: string; tracking_ref: string; notes: string;
  }>) => apiFetch<Delivery>(`/api/deliveries/${id}/amend`, { method: "PATCH", body }),
};
