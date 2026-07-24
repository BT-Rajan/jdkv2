// ── Auth ──────────────────────────────────────────────────────────────────
export interface TokenResponse {
  access_token: string;
  access_token_expires_at: number;
  refresh_token: string;
}

export interface MeResponse {
  subject_id: string;
  email: string | null;
  full_name: string | null;
  department: string | null;
  roles: string[];
  permissions: string[];
}

// ── Users ─────────────────────────────────────────────────────────────────
export interface UserSummary {
  subject_id: string;
  email: string;
  full_name: string | null;
  phone: string | null;
  department: string | null;
  status: string;
  roles: string[];
  created_at: string;
}

export interface AuditEntry {
  actor_subject_id: string;
  action: string;
  target_subject_id: string;
  previous_state: Record<string, unknown> | null;
  new_state: Record<string, unknown> | null;
  created_at: string;
}

// ── Customers ─────────────────────────────────────────────────────────────
export interface OrderHistoryEntry {
  id: number;
  order_no: string;
  quantity_kg: number;
  delivery_date: string | null;
  status: string;
  priority: string;
  product_name: string;
}

export interface Customer {
  id: number;
  name: string;
  contact_person: string | null;
  email: string | null;
  phone: string | null;
  address: string | null;
  billing_address: string | null;
  gstin: string | null;
  payment_terms: string | null;
  credit_limit: number;
  status: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
  orders?: OrderHistoryEntry[];
}

// ── Materials & Inventory ─────────────────────────────────────────────────
export interface ProductRef {
  id: number;
  name: string;
}

export interface MovementEntry {
  id: number;
  movement_type: "receipt" | "consumption" | "adjustment";
  quantity: number;
  reference: string | null;
  actor_subject_id: string | null;
  created_at: string;
}

export interface Material {
  id: number;
  name: string;
  unit: string;
  status: string;
  current_stock: number;
  minimum_stock: number;
  reorder_point: number;
  lead_time_days: number;
  used_by_products?: ProductRef[];
  recent_movements?: MovementEntry[];
}

// ── Suppliers ─────────────────────────────────────────────────────────────
export interface MaterialSupplyTerm {
  id: number;
  material_id: number;
  material_name: string;
  unit: string;
  price: number;
  lead_time_days: number;
  minimum_order_qty: number;
  payment_terms: string | null;
  delivery_cost: number;
}

export interface Supplier {
  id: number;
  name: string;
  contact_person: string | null;
  phone: string | null;
  email: string | null;
  address: string | null;
  gstin: string | null;
  category: string | null;
  rating: number | null;
  status: string;
  notes: string | null;
  created_at: string;
  materials_supplied?: MaterialSupplyTerm[];
}

// ── Products & Formulas ───────────────────────────────────────────────────
export interface FormulaLine {
  material_id: number;
  material_name: string;
  unit: string;
  quantity_per_unit: number;
}

export interface Formula {
  id: number;
  product_id: number;
  version: number;
  effective_from: string;
  is_active: boolean;
  created_at: string;
  lines: FormulaLine[];
}

export interface FormulaVersionSummary {
  id: number;
  version: number;
  effective_from: string;
  is_active: boolean;
  created_at: string;
}

export interface FinishedGoods {
  product_id: number;
  available_kg: number;
  available_bags: number;
  updated_at: string;
}

export interface Product {
  id: number;
  name: string;
  category: string | null;
  unit_of_measure: string;
  default_bag_size_kg: number;
  status: string;
  created_at: string;
  active_formula?: Formula | null;
  formula_versions?: FormulaVersionSummary[];
  finished_goods?: FinishedGoods | null;
}

// ── Customer Orders ───────────────────────────────────────────────────────
export interface Availability {
  available_kg: number;
  required_kg: number;
  shortfall_kg: number;
  fulfillable_from_stock: boolean;
}

export interface Order {
  id: number;
  order_no: string;
  customer_id: number;
  customer_name: string;
  product_id: number;
  product_name: string;
  quantity_kg: number;
  bag_size_kg: number;
  bags: number;
  delivery_date: string | null;
  status: string;
  priority: "critical" | "high" | "normal" | "low";
  notes: string | null;
  created_at: string;
  updated_at: string;
  availability?: Availability;
}

export const ORDER_STATUSES = [
  "draft", "confirmed", "planned", "partially_fulfilled",
  "fulfilled", "at_risk", "delayed", "cancelled",
] as const;

// ── MRP / ATP ─────────────────────────────────────────────────────────────
export interface ContributingOrder {
  order_id: number;
  order_no: string;
  customer_name: string;
  quantity_kg: number;
  delivery_date: string | null;
}

export interface ProductionRequirement {
  product_id: number;
  product_name: string;
  total_ordered_kg: number;
  finished_goods_kg: number;
  production_required_kg: number;
  has_active_formula: boolean;
  contributing_orders: ContributingOrder[];
}

export interface SuggestedSupplier {
  supplier_id: number;
  supplier_name: string;
  price: number;
  lead_time_days: number;
  minimum_order_qty: number;
  is_projected: boolean;
}

export interface MaterialRequirement {
  material_id: number;
  material_name: string;
  unit: string;
  gross_required: number;
  current_stock: number;
  net_required: number;
  shortage: boolean;
  affected_product_ids: number[];
  suggested_supplier: SuggestedSupplier | null;
  estimated_supply_date: string | null;
}

export interface MrpSnapshot {
  production_requirements: ProductionRequirement[];
  material_requirements: MaterialRequirement[];
  has_shortages: boolean;
}

export interface FeasibilityResult {
  order_id: number;
  order_no: string;
  outcome: "feasible" | "partially_feasible" | "feasible_on_later_date" | "at_risk" | "not_feasible";
  required_date: string | null;
  estimated_fulfillment_date: string;
  promptly_available_kg: number;
  remaining_kg: number;
  requested_kg: number;
  constraints: unknown[];
}

// ── Dashboard ─────────────────────────────────────────────────────────────
export interface DashboardSummary {
  open_order_count: number;
  products_with_open_demand: number;
  low_stock_material_count: number;
  low_stock_materials: Material[];
  material_shortage_count: number;
  top_material_shortages: MaterialRequirement[];
  orders_needing_attention_count: number;
  orders_needing_attention: FeasibilityResult[];
}

// ── Attachments ───────────────────────────────────────────────────────────
export interface Attachment {
  id: string;
  entity_type: string;
  entity_id: string;
  file_id: string;
  filename: string;
  label: string | null;
  uploaded_by_subject_id: string | null;
  created_at: string;
}

// ── Generic list envelope ─────────────────────────────────────────────────
export interface ListResponse<T> {
  total: number;
  [key: string]: T[] | number;
}
