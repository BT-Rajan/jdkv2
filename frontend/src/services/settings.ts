import { apiFetch } from "./api";
import type { AppSettings, UpdateSettingsRequest } from "../types";

export const settingsApi = {
  get: () => apiFetch<AppSettings>("/api/settings"),

  update: (body: UpdateSettingsRequest) =>
    apiFetch<AppSettings>("/api/settings", { method: "PATCH", body }),
};
