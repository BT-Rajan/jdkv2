// Mirrors backend/app/permissions/definitions.py. If a permission code
// changes on the backend, update it here too - there's no runtime coupling
// between the two, just a shared vocabulary.
export const USERS_VIEW = "users.view";
export const USERS_MANAGE = "users.manage";

export const CUSTOMERS_VIEW = "customer.view";
export const CUSTOMERS_MANAGE = "customer.manage";

export const PRODUCTS_VIEW = "product.view";
export const PRODUCTS_MANAGE = "product.manage";

export const INVENTORY_VIEW = "inventory.view";
export const INVENTORY_ADJUST = "inventory.adjust";

export const SUPPLIERS_VIEW = "supplier.view";
export const SUPPLIERS_MANAGE = "supplier.manage";

export const ORDERS_VIEW = "order.view";
export const ORDERS_CREATE = "order.create";
export const ORDERS_EDIT = "order.edit";
export const ORDERS_DELETE = "order.delete";

export const MRP_VIEW = "mrp.view";
export const MRP_EXECUTE = "mrp.execute";

export const REPORTS_VIEW = "reports.view";

export const FILE_UPLOAD = "file.upload";
export const FILE_VIEW = "file.view";
export const FILE_DELETE = "file.delete";
