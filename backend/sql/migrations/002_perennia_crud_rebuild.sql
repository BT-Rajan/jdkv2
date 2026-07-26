-- ════════════════════════════════════════════════════════════════════════
--  Migration 002: rebuild Customers / Suppliers / Raw Materials / Products /
--  Users(directory) on top of perennia-crud.
--
--  Run this against an *existing* JDK database (one that already has
--  migration 001 / the original schema.sql applied). Fresh installs get
--  the final shape directly from schema.sql and do not need this file.
--
--  Safe to re-run: scripts/init_db.py already treats "column/table already
--  exists" errnos (1060, 1050, ...) as skippable - see _ALREADY_EXISTS_ERRNOS.
-- ════════════════════════════════════════════════════════════════════════

-- ── Customers: add client type, promote "address" to "delivery_address",
--    rename gstin -> tax_id (same meaning, clearer for a GCC deployment) ──
ALTER TABLE customers
  ADD COLUMN client_type VARCHAR(50) NULL AFTER name;

ALTER TABLE customers
  CHANGE COLUMN address delivery_address TEXT NULL;

ALTER TABLE customers
  CHANGE COLUMN gstin tax_id VARCHAR(20) NULL;

-- ── Suppliers: same tax-id rename, nothing else changes ──────────────────
ALTER TABLE suppliers
  CHANGE COLUMN gstin tax_id VARCHAR(20) NULL;

-- ── Raw Materials: shelf life + a default/primary supplier reference.
--    (Per-supplier pricing/lead-time terms still live in
--    raw_material_supply - this is just "who we usually buy this from",
--    shown on the material's own form.) ────────────────────────────────────
ALTER TABLE raw_materials
  ADD COLUMN shelf_life_days SMALLINT NULL,
  ADD COLUMN default_supplier_id INT UNSIGNED NULL,
  ADD CONSTRAINT fk_material_default_supplier
      FOREIGN KEY (default_supplier_id) REFERENCES suppliers(id);

-- ── Inventory movements: capture goods-receipt paperwork (received date
--    can differ from created_at/data-entry time; invoice reference/amount
--    for reconciliation) so "Add Raw Material" can record an opening
--    receipt in the same place as the material master. ───────────────────
ALTER TABLE inventory_movements
  ADD COLUMN received_date DATE NULL,
  ADD COLUMN invoice_id VARCHAR(80) NULL,
  ADD COLUMN invoice_amount DECIMAL(12,2) NULL;

-- ── Employees (HR directory) ──────────────────────────────────────────────
-- Deliberately separate from perennia-auth's auth_subjects/auth_identifiers
-- and from JDK's own user_profiles (login-linked user administration).
-- This table has no bearing on who can sign in - it is a plain business
-- directory of people, matching the Users form fields as specified
-- (Name, Designation, Phone, Email, Address, Start-date, End-date, role).
-- `role` here is a free-text job title/role label, NOT an RBAC permission
-- role (those are seeded/enforced via perennia-access, see
-- app/permissions/definitions.py).
CREATE TABLE IF NOT EXISTS employees (
  id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  full_name     VARCHAR(150) NOT NULL,
  designation   VARCHAR(100) NULL,
  phone         VARCHAR(30)  NULL,
  email         VARCHAR(200) NULL,
  address       TEXT         NULL,
  start_date    DATE         NULL,
  end_date      DATE         NULL,
  role          VARCHAR(100) NULL,
  created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;
