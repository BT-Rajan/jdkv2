import { apiFetch } from "./api";
import { qs } from "./query";
import type { Material } from "../types";

export interface MaterialSearchParams {
  q?: string;
  low_stock_only?: boolean;
  limit?: number;
  offset?: number;
}

export const materialsApi = {
  search: (params: MaterialSearchParams = {}) =>
    apiFetch<{ materials: Material[]; total: number }>(`/api/materials${qs(params)}`),

  get: (id: number) => apiFetch<Material>(`/api/materials/${id}`),

  create: (body: { name: string; unit: string }) =>
    apiFetch<Material>("/api/materials", { method: "POST", body }),

  setReorderConfig: (id: number, body: { minimum_stock: number; reorder_point: number; lead_time_days: number }) =>
    apiFetch<Material>(`/api/materials/${id}/reorder-config`, { method: "PATCH", body }),

  recordMovement: (id: number, body: { movement_type: string; quantity: number; reference?: string }) =>
    apiFetch<Material>(`/api/materials/${id}/movements`, { method: "POST", body }),
};
