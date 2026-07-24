import { defineStore } from "pinia";
import { apiFetch, setSession, clearSession, hasSession } from "../services/api";
import type { MeResponse, TokenResponse } from "../types";

interface AuthState {
  subjectId: string | null;
  email: string | null;
  fullName: string | null;
  department: string | null;
  roles: string[];
  permissions: string[];
  ready: boolean; // true once the initial identity load has resolved (or been skipped)
}

export const useAuthStore = defineStore("auth", {
  state: (): AuthState => ({
    subjectId: null,
    email: null,
    fullName: null,
    department: null,
    roles: [],
    permissions: [],
    ready: false,
  }),

  getters: {
    isAuthenticated: (state) => !!state.subjectId,
    hasPermission: (state) => (code: string) => state.permissions.includes(code),
    hasAnyPermission: (state) => (codes: string[]) => codes.some((c) => state.permissions.includes(c)),
  },

  actions: {
    _reset() {
      this.subjectId = null;
      this.email = null;
      this.fullName = null;
      this.department = null;
      this.roles = [];
      this.permissions = [];
    },

    /** Called once on app boot. Silently resolves an existing session
     * (via the refresh token) into fresh identity/permissions, or leaves
     * the user signed out - never throws. */
    async initialize() {
      if (!hasSession()) {
        this._reset();
        this.ready = true;
        return;
      }
      try {
        const me = await apiFetch<MeResponse>("/api/auth/me");
        this.subjectId = me.subject_id;
        this.email = me.email;
        this.fullName = me.full_name;
        this.department = me.department;
        this.roles = me.roles;
        this.permissions = me.permissions;
      } catch {
        clearSession();
        this._reset();
      } finally {
        this.ready = true;
      }
    },

    async login(email: string, password: string) {
      const tokens = await apiFetch<TokenResponse>("/api/auth/login", {
        method: "POST",
        body: { email, password },
        auth: false,
      });
      setSession(tokens);
      const me = await apiFetch<MeResponse>("/api/auth/me");
      this.subjectId = me.subject_id;
      this.email = me.email;
      this.fullName = me.full_name;
      this.department = me.department;
      this.roles = me.roles;
      this.permissions = me.permissions;
    },

    async logout() {
      try {
        await apiFetch("/api/auth/logout", { method: "POST" });
      } catch {
        // Best-effort - clear local state regardless of network outcome.
      }
      clearSession();
      this._reset();
    },
  },
});
