// Read-only display data for Settings > Roles & Permissions.
//
// Mirrors backend/app/permissions/definitions.py (PERMISSIONS / ROLES) the
// same way permissions.ts already does - there's no runtime coupling, so if
// a role's permission set changes on the backend, update this table too.
// Actual role assignment happens on the Users page; this tab is informational.
import {
  CUSTOMERS_VIEW, PRODUCTS_VIEW, INVENTORY_VIEW, SUPPLIERS_VIEW,
  ORDERS_VIEW, MRP_VIEW, REPORTS_VIEW, USERS_VIEW, SETTINGS_VIEW,
} from "./permissions";

export interface RoleInfo {
  code: string;
  label: string;
  description: string;
}

export const DISPLAY_ROLES: RoleInfo[] = [
  { code: "administrator", label: "Administrator", description: "System control - full administrative access" },
  { code: "executive", label: "Executive", description: "Business visibility and decisions" },
  { code: "operations", label: "Operations", description: "Operational coordination" },
  { code: "production", label: "Production", description: "Production activities" },
  { code: "procurement", label: "Procurement", description: "Supplier and material activities" },
];

export interface AreaInfo {
  key: string;
  label: string;
  viewPermission: string;
}

export const DISPLAY_AREAS: AreaInfo[] = [
  { key: "customers", label: "Customers", viewPermission: CUSTOMERS_VIEW },
  { key: "products", label: "Products", viewPermission: PRODUCTS_VIEW },
  { key: "inventory", label: "Inventory", viewPermission: INVENTORY_VIEW },
  { key: "suppliers", label: "Suppliers", viewPermission: SUPPLIERS_VIEW },
  { key: "orders", label: "Orders", viewPermission: ORDERS_VIEW },
  { key: "mrp", label: "MRP", viewPermission: MRP_VIEW },
  { key: "reports", label: "Reports", viewPermission: REPORTS_VIEW },
  { key: "users", label: "Users", viewPermission: USERS_VIEW },
  { key: "settings", label: "Settings", viewPermission: SETTINGS_VIEW },
];

// Which view-permission each role holds, per backend/app/permissions/definitions.py ROLES.
const ROLE_VIEW_PERMISSIONS: Record<string, string[]> = {
  administrator: [
    CUSTOMERS_VIEW, PRODUCTS_VIEW, INVENTORY_VIEW, SUPPLIERS_VIEW,
    ORDERS_VIEW, MRP_VIEW, REPORTS_VIEW, USERS_VIEW, SETTINGS_VIEW,
  ],
  executive: [
    CUSTOMERS_VIEW, PRODUCTS_VIEW, INVENTORY_VIEW, SUPPLIERS_VIEW,
    ORDERS_VIEW, MRP_VIEW, REPORTS_VIEW, USERS_VIEW, SETTINGS_VIEW,
  ],
  operations: [
    CUSTOMERS_VIEW, PRODUCTS_VIEW, INVENTORY_VIEW, SUPPLIERS_VIEW,
    ORDERS_VIEW, MRP_VIEW, REPORTS_VIEW,
  ],
  production: [
    PRODUCTS_VIEW, INVENTORY_VIEW, ORDERS_VIEW, MRP_VIEW, REPORTS_VIEW,
  ],
  procurement: [
    SUPPLIERS_VIEW, INVENTORY_VIEW, PRODUCTS_VIEW, MRP_VIEW, REPORTS_VIEW,
  ],
};

export function roleHasArea(roleCode: string, area: AreaInfo): boolean {
  return (ROLE_VIEW_PERMISSIONS[roleCode] ?? []).includes(area.viewPermission);
}
