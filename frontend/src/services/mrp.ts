import { apiFetch } from "./api";
import { qs } from "./query";
import type { MrpSnapshot, FeasibilityResult, DashboardSummary } from "../types";

export const mrpApi = {
  calculate: () => apiFetch<MrpSnapshot>("/api/mrp"),

  whyMaterialRequired: (materialId: number) => apiFetch(`/api/mrp/materials/${materialId}/why-required`),

  atp: (productId: number, requestedKg: number) =>
    apiFetch(`/api/mrp/atp${qs({ product_id: productId, requested_kg: requestedKg })}`),
};

export const feasibilityApi = {
  assessOrder: (orderId: number) => apiFetch<FeasibilityResult>(`/api/orders/${orderId}/feasibility`),
  assessAllOpenOrders: () => apiFetch<FeasibilityResult[]>("/api/feasibility/open-orders"),
};

export const dashboardApi = {
  summary: () => apiFetch<DashboardSummary>("/api/dashboard"),
};
