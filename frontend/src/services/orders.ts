import { apiFetch } from "./api";
import { qs } from "./query";
import type { Order, Availability } from "../types";

export interface OrderSearchParams {
  q?: string;
  status?: string;
  customer_id?: number;
  limit?: number;
  offset?: number;
}

export const ordersApi = {
  search: (params: OrderSearchParams = {}) =>
    apiFetch<{ orders: Order[]; total: number }>(`/api/orders${qs(params)}`),

  get: (id: number) => apiFetch<Order>(`/api/orders/${id}`),

  checkAvailability: (productId: number, quantityKg: number) =>
    apiFetch<Availability>(`/api/orders/availability${qs({ product_id: productId, quantity_kg: quantityKg })}`),

  create: (body: {
    customer_id: number; product_id: number; quantity_kg: number; bag_size_kg?: number;
    delivery_date?: string; priority?: string; notes?: string;
  }) => apiFetch<Order>("/api/orders", { method: "POST", body }),

  update: (id: number, body: Partial<Order>) =>
    apiFetch<Order>(`/api/orders/${id}`, { method: "PATCH", body }),

  setStatus: (id: number, status: string) =>
    apiFetch<Order>(`/api/orders/${id}/status`, { method: "POST", body: { status } }),

  cancel: (id: number) => apiFetch<Order>(`/api/orders/${id}/cancel`, { method: "POST" }),

  feasibility: (id: number) => apiFetch(`/api/orders/${id}/feasibility`),
};
