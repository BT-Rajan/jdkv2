/**
 * Central place every configurable value is read from. Nothing in the app
 * reads import.meta.env directly outside this file, so adding a new
 * setting (a feature flag, a different default page size, ...) means
 * touching one file.
 */
export const config = {
  apiBaseUrl: (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, ""),
  appName: import.meta.env.VITE_APP_NAME || "JDK Manufacturing Operations",
  defaultPageSize: 20,
} as const;
