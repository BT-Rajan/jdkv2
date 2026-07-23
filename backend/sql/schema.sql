-- ════════════════════════════════════════════════════════════════════════
--  JDK Manufacturing Operations Platform — business schema
--  Applied to the same database as perennia-auth / perennia-access /
--  perennia-search / perennia-notify / perennia-files (see scripts/init_db.py).
--  Engine: InnoDB | Charset: utf8mb4
-- ════════════════════════════════════════════════════════════════════════

-- ── User Administration (JDK's own extension of perennia-auth identity) ────
-- Identity, credentials and sessions belong to perennia-auth
-- (auth_subjects / auth_identifiers). Roles and permissions belong to
-- perennia-access (roles / user_roles). This table holds only the JDK
-- business-profile fields neither package is responsible for.
CREATE TABLE IF NOT EXISTS user_profiles (
  subject_id   CHAR(36)     NOT NULL PRIMARY KEY,
  full_name    VARCHAR(150) NOT NULL,
  phone        VARCHAR(30)  NULL,
  department   VARCHAR(100) NULL,
  created_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_user_profiles_subject FOREIGN KEY (subject_id)
      REFERENCES auth_subjects(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS user_admin_audit (
  id                 CHAR(36)     NOT NULL PRIMARY KEY,
  actor_subject_id   CHAR(36)     NOT NULL,
  action             VARCHAR(64)  NOT NULL,
  target_subject_id  CHAR(36)     NOT NULL,
  previous_state     JSON         NULL,
  new_state          JSON         NULL,
  created_at         DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_audit_target (target_subject_id)
) ENGINE=InnoDB;

-- ── Customers ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS customers (
  id               INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name             VARCHAR(200) NOT NULL UNIQUE,
  contact_person   VARCHAR(150) NULL,
  email            VARCHAR(200) NULL,
  phone            VARCHAR(50)  NULL,
  address          TEXT         NULL,
  billing_address  TEXT         NULL,
  gstin            VARCHAR(20)  NULL,
  payment_terms    VARCHAR(100) NULL,
  credit_limit     DECIMAL(14,2) NOT NULL DEFAULT 0,
  status           ENUM('active','inactive') NOT NULL DEFAULT 'active',
  notes            TEXT         NULL,
  created_at       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ── Raw Materials & Inventory ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS raw_materials (
  id    INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name  VARCHAR(200) NOT NULL UNIQUE,
  unit  VARCHAR(20)  NOT NULL DEFAULT 'kg',
  status ENUM('active','inactive') NOT NULL DEFAULT 'active'
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS raw_material_inventory (
  id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  material_id     INT UNSIGNED NOT NULL UNIQUE,
  current_stock   DECIMAL(14,3) NOT NULL DEFAULT 0,
  minimum_stock   DECIMAL(14,3) NOT NULL DEFAULT 0,
  reorder_point   DECIMAL(14,3) NOT NULL DEFAULT 0,
  lead_time_days  SMALLINT      NOT NULL DEFAULT 0,
  updated_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_inventory_material FOREIGN KEY (material_id) REFERENCES raw_materials(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS inventory_movements (
  id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  material_id   INT UNSIGNED NOT NULL,
  movement_type ENUM('receipt','consumption','adjustment') NOT NULL,
  quantity      DECIMAL(14,3) NOT NULL,
  reference     VARCHAR(120) NULL,
  actor_subject_id CHAR(36) NULL,
  created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_movement_material FOREIGN KEY (material_id) REFERENCES raw_materials(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ── Suppliers ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS suppliers (
  id             INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name           VARCHAR(200) NOT NULL UNIQUE,
  contact_person VARCHAR(150) NULL,
  phone          VARCHAR(50)  NULL,
  email          VARCHAR(200) NULL,
  address        TEXT         NULL,
  gstin          VARCHAR(20)  NULL,
  category       VARCHAR(100) NULL,
  rating         TINYINT      NULL,
  status         ENUM('active','inactive') NOT NULL DEFAULT 'active',
  notes          TEXT         NULL,
  created_at     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS raw_material_supply (
  id                INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  material_id       INT UNSIGNED NOT NULL,
  supplier_id       INT UNSIGNED NOT NULL,
  price             DECIMAL(12,4) NOT NULL DEFAULT 0,
  lead_time_days    SMALLINT      NOT NULL DEFAULT 0,
  minimum_order_qty DECIMAL(14,3) NOT NULL DEFAULT 0,
  payment_terms     VARCHAR(100)  NULL,
  delivery_cost     DECIMAL(12,2) NOT NULL DEFAULT 0,
  UNIQUE KEY uq_material_supplier (material_id, supplier_id),
  CONSTRAINT fk_supply_material FOREIGN KEY (material_id) REFERENCES raw_materials(id) ON DELETE CASCADE,
  CONSTRAINT fk_supply_supplier FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ── Products, Formulas (versioned BOM) & Finished Goods ─────────────────
CREATE TABLE IF NOT EXISTS products (
  id                   INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name                 VARCHAR(200) NOT NULL UNIQUE,
  category             VARCHAR(100) NULL,
  unit_of_measure      VARCHAR(20)  NOT NULL DEFAULT 'kg',
  default_bag_size_kg  DECIMAL(10,3) NOT NULL DEFAULT 50,
  status               ENUM('active','discontinued') NOT NULL DEFAULT 'active',
  created_at           DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Formulas are versioned, never mutated in place (see 03-domain-model.md):
-- changing a formula creates a new version so past production stays
-- explainable against the version used at the time.
CREATE TABLE IF NOT EXISTS formulas (
  id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  product_id      INT UNSIGNED NOT NULL,
  version         INT UNSIGNED NOT NULL,
  effective_from  DATE         NOT NULL,
  is_active       TINYINT(1)   NOT NULL DEFAULT 1,
  created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_product_version (product_id, version),
  CONSTRAINT fk_formula_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS formula_lines (
  id             INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  formula_id     INT UNSIGNED NOT NULL,
  material_id    INT UNSIGNED NOT NULL,
  quantity_per_unit DECIMAL(12,6) NOT NULL,
  UNIQUE KEY uq_formula_material (formula_id, material_id),
  CONSTRAINT fk_line_formula FOREIGN KEY (formula_id) REFERENCES formulas(id) ON DELETE CASCADE,
  CONSTRAINT fk_line_material FOREIGN KEY (material_id) REFERENCES raw_materials(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS finished_goods_inventory (
  id             INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  product_id     INT UNSIGNED NOT NULL UNIQUE,
  available_kg   DECIMAL(14,3) NOT NULL DEFAULT 0,
  available_bags INT           NOT NULL DEFAULT 0,
  updated_at     DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_fg_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ── Customer Orders ───────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS customer_orders (
  id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  order_no      VARCHAR(50)   NOT NULL UNIQUE,
  customer_id   INT UNSIGNED  NOT NULL,
  product_id    INT UNSIGNED  NOT NULL,
  quantity_kg   DECIMAL(14,3) NOT NULL,
  bag_size_kg   DECIMAL(10,3) NOT NULL DEFAULT 50,
  bags          INT           NOT NULL DEFAULT 0,
  delivery_date DATE          NULL,
  status        ENUM('draft','confirmed','planned','partially_fulfilled','fulfilled',
                      'at_risk','delayed','cancelled')
                NOT NULL DEFAULT 'draft',
  priority      ENUM('critical','high','normal','low') NOT NULL DEFAULT 'normal',
  notes         TEXT          NULL,
  created_by_subject_id CHAR(36) NULL,
  created_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_order_customer FOREIGN KEY (customer_id) REFERENCES customers(id),
  CONSTRAINT fk_order_product FOREIGN KEY (product_id) REFERENCES products(id)
) ENGINE=InnoDB;

-- ── Production Schedule ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS production_schedules (
  id                  INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  schedule_no         VARCHAR(50)   NOT NULL UNIQUE,
  product_id          INT UNSIGNED  NOT NULL,
  planned_qty_kg      DECIMAL(14,3) NOT NULL,
  start_date          DATE          NOT NULL,
  end_date            DATE          NOT NULL,
  shift               ENUM('day','night','full_day') NOT NULL DEFAULT 'day',
  manpower_available  SMALLINT      NOT NULL DEFAULT 0,
  manpower_required   SMALLINT      NOT NULL DEFAULT 0,
  status              ENUM('planned','confirmed','in_progress','completed','cancelled')
                      NOT NULL DEFAULT 'planned',
  linked_order_id     INT UNSIGNED  NULL,
  notes               TEXT          NULL,
  created_at          DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at          DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_schedule_product FOREIGN KEY (product_id) REFERENCES products(id),
  CONSTRAINT fk_schedule_order FOREIGN KEY (linked_order_id) REFERENCES customer_orders(id)
) ENGINE=InnoDB;

-- ── Attachments (generic link from any JDK entity to a perennia-files file) ─
-- perennia-files stores and versions the bytes; it has no notion of "this
-- file belongs to supplier #12" - that ownership mapping is JDK's own, kept
-- here rather than adding an owner_type/owner_id column to a package we
-- don't own.
CREATE TABLE IF NOT EXISTS entity_attachments (
  id                    CHAR(36)     NOT NULL PRIMARY KEY,
  entity_type           VARCHAR(40)  NOT NULL,
  entity_id             VARCHAR(40)  NOT NULL,
  file_id               CHAR(36)     NOT NULL,
  filename              VARCHAR(255) NOT NULL,
  label                 VARCHAR(150) NULL,
  uploaded_by_subject_id CHAR(36)    NULL,
  created_at            DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_attachments_entity (entity_type, entity_id)
) ENGINE=InnoDB;

-- ── Factory configuration ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS factory_config (
  key_name  VARCHAR(120) NOT NULL PRIMARY KEY,
  val       TEXT         NOT NULL
) ENGINE=InnoDB;

INSERT IGNORE INTO factory_config (key_name, val) VALUES
  ('batch_size_kg',                '1000'),
  ('daily_production_capacity_kg', '20000'),
  ('working_days_per_week',        '6'),
  ('company_name',                 'JDK');
