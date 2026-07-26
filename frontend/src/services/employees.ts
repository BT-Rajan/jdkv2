import { apiFetch } from "./api";
import { qs } from "./query";
import type { Employee } from "../types";

export interface EmployeeSearchParams {
  q?: string;
  role?: string;
  limit?: number;
  offset?: number;
}

export const employeesApi = {
  search: (params: EmployeeSearchParams = {}) =>
    apiFetch<{ employees: Employee[]; total: number }>(`/api/employees${qs(params)}`),

  get: (id: number) => apiFetch<Employee>(`/api/employees/${id}`),

  create: (body: Partial<Employee>) => apiFetch<Employee>("/api/employees", { method: "POST", body }),

  update: (id: number, body: Partial<Employee>) =>
    apiFetch<Employee>(`/api/employees/${id}`, { method: "PATCH", body }),

  delete: (id: number) => apiFetch<void>(`/api/employees/${id}`, { method: "DELETE" }),
};
