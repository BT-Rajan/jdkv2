<script setup lang="ts">
import { computed } from "vue";
import { useAuthStore } from "../../stores/auth";
import { useUiStore } from "../../stores/ui";
import {
  CUSTOMERS_VIEW, INVENTORY_VIEW, SUPPLIERS_VIEW, PRODUCTS_VIEW,
  ORDERS_VIEW, MRP_VIEW, REPORTS_VIEW, USERS_VIEW, SETTINGS_VIEW,
  FEASIBILITY_VIEW, SALES_ACCESS, DELIVERIES_VIEW, EMPLOYEES_VIEW,
} from "../../permissions";

const auth = useAuthStore();
const ui = useUiStore();

interface NavItem { to: string; label: string; icon: string; permission?: string; section?: string; }

const items: NavItem[] = [
  { to: "/", label: "Dashboard", icon: "▤", permission: REPORTS_VIEW },
  { to: "/feasibility", label: "Feasibility", icon: "◔", permission: FEASIBILITY_VIEW, section: "Order" },
  { to: "/quotations", label: "Quotations", icon: "▧", permission: SALES_ACCESS, section: "Order" },
  { to: "/orders", label: "Orders", icon: "▥", permission: ORDERS_VIEW, section: "Order" },
  { to: "/deliveries", label: "Deliveries", icon: "▨", permission: DELIVERIES_VIEW, section: "Order" },
  { to: "/customers", label: "Customers", icon: "◈", permission: CUSTOMERS_VIEW },
  { to: "/products", label: "Products & Formulas", icon: "◫", permission: PRODUCTS_VIEW },
  { to: "/materials", label: "Materials & Inventory", icon: "▦", permission: INVENTORY_VIEW },
  { to: "/suppliers", label: "Suppliers", icon: "◧", permission: SUPPLIERS_VIEW },
  { to: "/mrp", label: "MRP & ATP", icon: "◔", permission: MRP_VIEW },
  { to: "/users-directory", label: "Employees", icon: "☰", permission: EMPLOYEES_VIEW },
  { to: "/users", label: "Users", icon: "◍", permission: USERS_VIEW },
  { to: "/settings", label: "Settings", icon: "⚙", permission: SETTINGS_VIEW },
];

const visibleItems = computed(() => items.filter((i) => !i.permission || auth.hasPermission(i.permission)));
</script>

<template>
  <aside class="sidebar" :class="{ collapsed: ui.sidebarCollapsed }">
    <div class="brand">
      <span class="brand-mark">J</span>
      <span v-if="!ui.sidebarCollapsed" class="brand-name">JDK</span>
    </div>
    <nav class="nav">
      <template v-for="(item, idx) in visibleItems" :key="item.to">
        <div v-if="item.section && !ui.sidebarCollapsed && visibleItems[idx - 1]?.section !== item.section" class="nav-section">
          {{ item.section }}
        </div>
        <router-link :to="item.to" class="nav-item" active-class="active">
          <span class="nav-icon">{{ item.icon }}</span>
          <span v-if="!ui.sidebarCollapsed" class="nav-label">{{ item.label }}</span>
        </router-link>
      </template>
    </nav>
    <button class="collapse-btn" @click="ui.toggleSidebar" :aria-label="ui.sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'">
      {{ ui.sidebarCollapsed ? "»" : "«" }}
    </button>
  </aside>
</template>

<style scoped>
.sidebar {
  width: var(--sidebar-width);
  background: var(--color-neutral-900);
  color: var(--color-neutral-200);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  height: 100vh;
  position: sticky;
  top: 0;
  transition: width 0.15s ease;
}
.sidebar.collapsed { width: var(--sidebar-width-collapsed); }

.brand {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-5) var(--space-4);
  height: var(--topbar-height);
}
.brand-mark {
  display: inline-flex; align-items: center; justify-content: center;
  width: 32px; height: 32px;
  background: var(--color-primary-500);
  color: white;
  border-radius: var(--radius-sm);
  font-weight: 700;
}
.brand-name { font-weight: 700; color: white; letter-spacing: 0.02em; }

.nav { display: flex; flex-direction: column; gap: 2px; padding: var(--space-2); flex: 1; overflow-y: auto; }
.nav-item {
  display: flex; align-items: center; gap: var(--space-3);
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  color: var(--color-neutral-300);
  font-size: var(--text-sm);
  font-weight: 500;
}
.nav-item:hover { background: rgba(255,255,255,0.06); text-decoration: none; }
.nav-item.active { background: var(--color-primary-500); color: white; }
.nav-icon { width: 20px; text-align: center; }
.nav-section {
  padding: 10px 12px 2px;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-neutral-500);
}

.collapse-btn {
  margin: var(--space-3);
  background: rgba(255,255,255,0.06);
  border: none;
  color: var(--color-neutral-300);
  border-radius: var(--radius-sm);
  padding: 8px;
  cursor: pointer;
}
.collapse-btn:hover { background: rgba(255,255,255,0.12); }
</style>
