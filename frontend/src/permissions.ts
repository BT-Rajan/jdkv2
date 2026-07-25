// Mirrors backend/app/permissions/definitions.py. If a permission code
// changes on the backend, update it here too - there's no runtime coupling
// between the two, just a shared vocabulary.
export const USERS_VIEW = "users_view";
export const USERS_MANAGE = "users_manage";

export const CUSTOMERS_VIEW = "customer_view";
export const CUSTOMERS_MANAGE = "customer_manage";

export const PRODUCTS_VIEW = "product_view";
export const PRODUCTS_MANAGE = "product_manage";

export const INVENTORY_VIEW = "inventory_view";
export const INVENTORY_ADJUST = "inventory_adjust";

export const SUPPLIERS_VIEW = "supplier_view";
export const SUPPLIERS_MANAGE = "supplier_manage";

export const ORDERS_VIEW = "order_view";
export const ORDERS_CREATE = "order_create";
export const ORDERS_EDIT = "order_edit";
export const ORDERS_DELETE = "order_delete";

export const MRP_VIEW = "mrp_view";
export const MRP_EXECUTE = "mrp_execute";

export const REPORTS_VIEW = "reports_view";

export const SETTINGS_VIEW = "settings_view";
export const SETTINGS_MANAGE = "settings_manage";

export const FILE_UPLOAD = "file.upload";
export const FILE_VIEW = "file.view";
export const FILE_DELETE = "file.delete";
