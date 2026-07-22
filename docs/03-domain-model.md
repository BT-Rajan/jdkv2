# JDK — Domain Model

## Purpose

This document defines the core business entities in JDK, their attributes, their relationships, and the invariants that must hold between them.

It is the authoritative reference for building the data model, the domain services, and the intelligence layer. Table names, API shapes, and screens are derived from this document — not the other way around.

The domain model represents the business as it exists, independent of the user interface or technical implementation.

---

## 1. Domain Map

```text
Customer ──< Customer Order >── Product ── Formula >── Raw Material
                                    │                        │
                                    │                        ├──< Raw Material Inventory
                                    │                        └──< Raw Material Supply >── Supplier
                                    │
                                    └── Finished Goods Inventory ──< Production
```

Read `A ──< B` as "A has many B". Read `A >── B` as "many A reference one B".

Two supply chains meet at Production:

```text
Customer
    ↓
Customer Order
    ↓
Product
    ↓
Formula
    ↓
Raw Material
```

```text
Supplier
    ↓
Raw Material Supply
    ↓
Raw Material Inventory
    ↓
Production
    ↓
Finished Goods Inventory
```

---

## 2. Entities

Each entity below lists its identity, its core attributes, and the invariants that must hold. Attribute lists are the minimum needed to build the domain — implementation may add fields, but must not violate the invariants.

### 2.1 User

A person who accesses JDK.

| Attribute | Notes |
|---|---|
| `id` | primary key |
| `name` | |
| `credentials` | hashed, never exposed |
| `role` | see [07-security-and-roles.md](07-security-and-roles.md) |
| `permissions` | derived from role, may be overridden |
| `status` | active / disabled |

**Invariant:** every action taken in the system is attributable to a User.

---

### 2.2 Customer

An organisation or person to whom products are supplied.

| Attribute | Notes |
|---|---|
| `id` | primary key |
| `name` | |
| `contact_details` | |
| `status` | active / inactive |

**Relationship:** `Customer 1 ──< N Customer Order`

---

### 2.3 Product

A finished product that can be manufactured and supplied to a customer.

| Attribute | Notes |
|---|---|
| `id` | primary key |
| `name` | |
| `unit_of_measure` | |
| `formula_id` | current active formula |
| `status` | active / discontinued |

**Relationship:** `Product 1 ── 1 Formula` (a product has exactly one active formula at a time; formulas may be versioned)

---

### 2.4 Formula

Defines the materials and quantities required to produce one unit of a product (bill of materials).

| Attribute | Notes |
|---|---|
| `id` | primary key |
| `product_id` | |
| `version` | formulas are versioned, not overwritten |
| `effective_from` | |
| `lines` | set of `(raw_material_id, quantity_per_unit)` |

**Invariant:** a formula must resolve to at least one raw material line. Changing a formula creates a new version; it does not mutate history, because past production must remain explainable against the formula version used at the time.

---

### 2.5 Raw Material

A material consumed during production.

| Attribute | Notes |
|---|---|
| `id` | primary key |
| `name` | |
| `unit_of_measure` | |
| `status` | active / discontinued |

**Relationships:**

* `Raw Material N ──< N Formula Line` (used by many formulas)
* `Raw Material 1 ──< N Raw Material Supply` (supplied by many suppliers)
* `Raw Material 1 ── 1 Raw Material Inventory` (one running stock position)

---

### 2.6 Supplier

An organisation that supplies raw materials.

| Attribute | Notes |
|---|---|
| `id` | primary key |
| `name` | |
| `contact_details` | |
| `lead_time_days` | per supplier, may be overridden per material |
| `status` | active / inactive |

**Relationship:** `Supplier 1 ──< N Raw Material Supply`

---

### 2.7 Raw Material Supply

A specific supplier's ability to supply a specific raw material — the join between Supplier and Raw Material, carrying commercial terms.

| Attribute | Notes |
|---|---|
| `id` | primary key |
| `supplier_id` | |
| `raw_material_id` | |
| `lead_time_days` | overrides supplier default when set |
| `expected_deliveries` | scheduled/expected receipts |

---

### 2.8 Inventory

Represents the stock position of a material or finished good. Raw Material Inventory and Finished Goods Inventory share this shape; they differ in what they track.

| Attribute | Notes |
|---|---|
| `id` | primary key |
| `subject_id` | raw material id or product id |
| `subject_type` | `raw_material` \| `finished_good` |
| `physical_quantity` | what exists |
| `reserved_quantity` | committed against orders/production |
| `available_quantity` | derived, see §4 |
| `as_of` | timestamp the position is valid for |

**Invariant:**

```text
available_quantity = physical_quantity − reserved_quantity
```

**Movement types:** `receipt`, `consumption`, `production`, `allocation`, `delivery`, `adjustment`. Every change to `physical_quantity` or `reserved_quantity` must be recorded as a movement — inventory quantities are never edited directly, only derived from their movement history.

---

### 2.9 Production

Represents the conversion of raw materials into finished products.

| Attribute | Notes |
|---|---|
| `id` | primary key |
| `product_id` | |
| `formula_version` | the formula version used |
| `quantity` | units produced |
| `status` | planned / in progress / complete |
| `scheduled_date` | |
| `completed_date` | nullable |
| `driven_by` | order id(s) or forecast, for traceability |

**Invariant:** a Production record consumes Raw Material Inventory (per the formula) and, on completion, credits Finished Goods Inventory. Production is driven by product requirements and customer commitments — it should not exist without a traceable reason (an order or an explicit planning decision).

---

### 2.10 Customer Order

Represents a customer commitment to supply a product in a required quantity and timeframe.

| Attribute | Notes |
|---|---|
| `id` | primary key |
| `customer_id` | |
| `product_id` | |
| `quantity` | |
| `required_date` | |
| `status` | open / partially fulfilled / fulfilled / at risk / cancelled |

**Composition:**

```text
Customer Order = Customer + Product + Quantity + Required Date
```

**Invariant:** an order may draw on existing Finished Goods Inventory, or create a Production requirement, or both. An order's `status` is a derived/calculated field — see [05-intelligence-model.md](05-intelligence-model.md) — never set directly by a user.

---

## 3. Core Relationships

```text
Customer
    │
    └── Customer Order
            │
            └── Product
                    │
                    └── Formula
                            │
                            └── Raw Material
                                    │
                                    ├── Inventory
                                    │
                                    └── Supplier
```

```text
Customer Order
        ↓
Finished Goods Availability
        ↓
Production Requirement
        ↓
Material Requirement
        ↓
Material Availability
        ↓
Supplier Availability
```

---

## 4. Availability

The domain distinguishes between what exists and what is available. This distinction applies uniformly to finished goods, raw materials, production capacity, and supplier supply.

```text
Physical Quantity
        −
Existing Commitments
        =
Available Quantity
```

Every "can we do X" question in JDK — can we fulfil this order, can we start this production, can we rely on this shipment — reduces to this formula applied at the relevant level. This is why it is defined here, in the domain, rather than in application code.

---

## 5. Commitment and Fulfilment

A commitment creates a requirement. A requirement is checked against availability. The result is fulfilment, partial fulfilment, or a gap.

```text
Commitment
    ↓
Requirement
    ↓
Availability Check
    ↓
Fulfilment
```

A commitment may therefore propagate through multiple domain entities — this propagation is what the Intelligence layer calculates (see [05-intelligence-model.md](05-intelligence-model.md)).

---

## 6. Business State Is Derived

The state of the business is derived from the condition of its domain entities and their relationships — it is not a separate thing that must be kept in sync by hand. For example:

```text
Customer Order
        ↓
Material Requirement
        ↓
Material Not Available
        ↓
Supplier Lead Time
        ↓
Production Delay Risk
```

The domain model provides the facts. Operational calculations and business situations are derived from these facts, never stored as independent, hand-maintained truth.

---

## 7. Domain Boundary

The core domain is:

```text
Customer Commitments
        ↓
Products
        ↓
Materials
        ↓
Inventory
        ↓
Suppliers
        ↓
Production
        ↓
Finished Goods
        ↓
Fulfilment
```

MRP, ATP, feasibility analysis, risk analysis, and business reporting all operate on this domain — they read it, they do not redefine it.

**Rule for implementation:** the user interface, the API, and the intelligence layer must not introduce concepts, states, or relationships that are not traceable back to this document. If a screen needs a concept this document doesn't have, the concept belongs here first.
