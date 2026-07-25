import { apiFetch } from "./api";
import type { ProductionCycle, ProductionCycleUpsertRequest } from "../types";

export const productionApi = {
  get: (productId: number) =>
    apiFetch<ProductionCycle>(`/api/products/${productId}/production-cycle`),

  upsert: (productId: number, body: ProductionCycleUpsertRequest) =>
    apiFetch<ProductionCycle>(`/api/products/${productId}/production-cycle`, { method: "PUT", body }),
};
