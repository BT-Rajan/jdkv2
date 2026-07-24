import { defineStore } from "pinia";

export interface Toast {
  id: number;
  kind: "success" | "error" | "info";
  message: string;
}

let nextId = 1;

export const useUiStore = defineStore("ui", {
  state: () => ({
    toasts: [] as Toast[],
    sidebarCollapsed: false,
  }),
  actions: {
    toast(message: string, kind: Toast["kind"] = "info") {
      const id = nextId++;
      this.toasts.push({ id, kind, message });
      setTimeout(() => this.dismiss(id), 5000);
    },
    dismiss(id: number) {
      this.toasts = this.toasts.filter((t) => t.id !== id);
    },
    toggleSidebar() {
      this.sidebarCollapsed = !this.sidebarCollapsed;
    },
  },
});
