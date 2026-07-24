import { apiFetch } from "./api";
import { qs } from "./query";
import type { Product } from "../types";

export interface ProductSearchParams {
  q?: string;
  status?: string;
  limit?: number;
  offset?: number;
}

export const productsApi = {
  search: (params: ProductSearchParams = {}) =>
    apiFetch<{ products: Product[]; total: number }>(`/api/products${qs(params)}`),

  get: (id: number) => apiFetch<Product>(`/api/products/${id}`),

  create: (body: { name: string; category?: string; unit_of_measure?: string; default_bag_size_kg?: number }) =>
    apiFetch<Product>("/api/products", { method: "POST", body }),

  update: (id: number, body: Partial<Product>) =>
    apiFetch<Product>(`/api/products/${id}`, { method: "PATCH", body }),

  setStatus: (id: number, status: string) =>
    apiFetch<Product>(`/api/products/${id}/status`, { method: "POST", body: { status } }),

  createFormulaVersion: (id: number, body: {
    effective_from: string;
    lines: { material_id: number; quantity_per_unit: number }[];
  }) => apiFetch<Product>(`/api/products/${id}/formula-versions`, { method: "POST", body }),

  recordFinishedGoodsMovement: (id: number, deltaKg: number) =>
    apiFetch(`/api/products/${id}/finished-goods/movements`, { method: "POST", body: { delta_kg: deltaKg } }),
};
