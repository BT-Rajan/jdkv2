import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router";
import { useAuthStore } from "../stores/auth";
import {
  CUSTOMERS_VIEW, INVENTORY_VIEW, SUPPLIERS_VIEW, PRODUCTS_VIEW,
  ORDERS_VIEW, MRP_VIEW, REPORTS_VIEW, USERS_VIEW,
} from "../permissions";

const routes: RouteRecordRaw[] = [
  {
    path: "/login",
    name: "login",
    component: () => import("../pages/auth/LoginPage.vue"),
    meta: { public: true },
  },
  {
    path: "/forgot-password",
    name: "forgot-password",
    component: () => import("../pages/auth/ForgotPasswordPage.vue"),
    meta: { public: true },
  },
  {
    path: "/reset-password",
    name: "reset-password",
    component: () => import("../pages/auth/ResetPasswordPage.vue"),
    meta: { public: true },
  },
  {
    path: "/verify-email",
    name: "verify-email",
    component: () => import("../pages/auth/VerifyEmailPage.vue"),
    meta: { public: true },
  },
  {
    path: "/access-denied",
    name: "access-denied",
    component: () => import("../pages/AccessDeniedPage.vue"),
    meta: { public: true },
  },
  {
    path: "/",
    component: () => import("../components/layout/AppShell.vue"),
    children: [
      { path: "", name: "dashboard", component: () => import("../pages/DashboardPage.vue"), meta: { permission: REPORTS_VIEW } },

      { path: "customers", name: "customers", component: () => import("../pages/customers/CustomersListPage.vue"), meta: { permission: CUSTOMERS_VIEW } },
      { path: "customers/:id", name: "customer-detail", component: () => import("../pages/customers/CustomerDetailPage.vue"), meta: { permission: CUSTOMERS_VIEW } },

      { path: "materials", name: "materials", component: () => import("../pages/materials/MaterialsListPage.vue"), meta: { permission: INVENTORY_VIEW } },
      { path: "materials/:id", name: "material-detail", component: () => import("../pages/materials/MaterialDetailPage.vue"), meta: { permission: INVENTORY_VIEW } },

      { path: "suppliers", name: "suppliers", component: () => import("../pages/suppliers/SuppliersListPage.vue"), meta: { permission: SUPPLIERS_VIEW } },
      { path: "suppliers/:id", name: "supplier-detail", component: () => import("../pages/suppliers/SupplierDetailPage.vue"), meta: { permission: SUPPLIERS_VIEW } },

      { path: "products", name: "products", component: () => import("../pages/products/ProductsListPage.vue"), meta: { permission: PRODUCTS_VIEW } },
      { path: "products/:id", name: "product-detail", component: () => import("../pages/products/ProductDetailPage.vue"), meta: { permission: PRODUCTS_VIEW } },

      { path: "orders", name: "orders", component: () => import("../pages/orders/OrdersListPage.vue"), meta: { permission: ORDERS_VIEW } },
      { path: "orders/:id", name: "order-detail", component: () => import("../pages/orders/OrderDetailPage.vue"), meta: { permission: ORDERS_VIEW } },

      { path: "mrp", name: "mrp", component: () => import("../pages/mrp/MrpPage.vue"), meta: { permission: MRP_VIEW } },

      { path: "users", name: "users", component: () => import("../pages/users/UsersListPage.vue"), meta: { permission: USERS_VIEW } },
      { path: "users/:id", name: "user-detail", component: () => import("../pages/users/UserDetailPage.vue"), meta: { permission: USERS_VIEW } },
    ],
  },
  { path: "/:pathMatch(.*)*", name: "not-found", component: () => import("../pages/NotFoundPage.vue"), meta: { public: true } },
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();
  if (!auth.ready) {
    await auth.initialize();
  }

  if (to.meta.public) {
    return true;
  }

  if (!auth.isAuthenticated) {
    return { name: "login", query: { redirect: to.fullPath } };
  }

  const permission = to.meta.permission as string | undefined;
  if (permission && !auth.hasPermission(permission)) {
    return { name: "access-denied" };
  }

  return true;
});
