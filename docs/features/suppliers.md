# JDK — Suppliers

## Purpose

Suppliers provide materials required for production.

The core relationship is:

```text
Supplier
      ↓
Material Supply
      ↓
Material Availability
      ↓
Production
      ↓
Finished Goods
      ↓
Customer Fulfilment
```

A supplier may provide one or more materials.

A material may be supplied by one or more suppliers.

```text
Supplier A ──┐
             ├── Material
Supplier B ──┘
```

---

## Supplier Lifecycle

```text
Create
  ↓
Active
  ↓
Supply Relationship
  ↓
Inactive
  ↓
Archived
```

Possible statuses may include:

```text
Active
Inactive
Suspended
Archived
```

A supplier should not normally be deleted when historical supply records depend on it.

---

## Supplier Information

The system may maintain information required to:

* identify the supplier;
* communicate with the supplier;
* associate materials with the supplier;
* track expected supply;
* support procurement decisions.

The domain should distinguish between:

```text
Supplier Identity
      +
Contact Information
      +
Supply Relationship
      +
Supply History
```

---

## Supplier and Materials

A supplier may provide multiple materials.

```text
Supplier
    ├── Material A
    ├── Material B
    └── Material C
```

The relationship may include information relevant to supply planning, such as:

* expected lead time;
* supply status;
* agreed supply information;
* historical performance where supported.

The exact attributes should be defined by the implementation and business requirements.

---

## Supplier and Material Availability

Supplier information may affect future material availability.

```text
Material Requirement
        ↓
Current Inventory
        ↓
Shortfall
        ↓
Supplier Availability
        ↓
Expected Receipt
        ↓
Future Material Availability
```

A supplier delay may therefore create a downstream production or fulfilment risk.

---

## Supplier Commitments

A supplier may have an expected supply commitment.

Conceptually:

```text
Material
      ↓
Required Quantity
      ↓
Supplier
      ↓
Expected Quantity
      ↓
Expected Date
```

The business should be able to distinguish between:

```text
Required
      ↓
Ordered / Expected
      ↓
Received
      ↓
Remaining
```

---

## Supplier and MRP

MRP may identify a material shortage.

```text
Material Requirement
      ↓
Available Inventory
      ↓
Shortage
      ↓
Supplier Supply
      ↓
Expected Availability
```

Supplier information may therefore affect whether a production or customer commitment is feasible.

---

## Supplier Risk

A supplier-related risk may arise when:

```text
Material Required
      ↓
Material Not Available
      ↓
Supplier Expected
      ↓
Supplier Date Too Late
      ↓
Production Risk
      ↓
Fulfilment Risk
```

The system should allow the user to understand this chain.

```text
Customer Order
      ↓
Production Requirement
      ↓
Material Requirement
      ↓
Supplier
      ↓
Expected Supply Date
      ↓
Fulfilment Impact
```

---

## Supplier Operations

Authorized users may be able to:

```text
Search
  ↓
View
  ↓
Create
  ↓
Update
  ↓
Deactivate
```

Where supply commitments are supported, authorized users may also:

```text
Record Expected Supply
        ↓
Update Expected Date
        ↓
Record Receipt
        ↓
View Supply History
```

The exact workflow depends on the procurement process implemented by JDK.

---

## Supplier and Inventory

A supplier receipt increases material availability.

```text
Supplier
      ↓
Material Receipt
      ↓
Material Inventory
      ↓
Available Material
```

The receipt should be traceable to its source.

---

## Access

Supplier operations are controlled through Perennia Access.

Possible permissions include:

```text
suppliers.view
suppliers.create
suppliers.update
suppliers.deactivate

supplier_supply.view
supplier_supply.create
supplier_supply.update
supplier_supply.receive
```

The exact permission names must follow Perennia Access conventions.

The backend must enforce all permissions.

---

## Error Handling

Supplier operations must use stable, unique error codes.

Examples:

```text
SUPPLIER-001
Supplier not found

SUPPLIER-002
Supplier already exists

SUPPLIER-003
Supplier cannot be deactivated

SUPPLIER-004
Material is not associated with this supplier

SUPPLY-001
Supply commitment not found

SUPPLY-002
Invalid expected supply date

SUPPLY-003
Receipt quantity exceeds permitted quantity
```

The frontend must use error codes rather than parsing error-message text.

---

## Supplier Principle

A supplier is not merely a contact record.

Within JDK:

```text
Supplier
      ↓
Material
      ↓
Availability
      ↓
Production
      ↓
Finished Goods
      ↓
Customer Fulfilment
```

The key question is:

> **If a required material is not currently available, when can it become available, and what commitments depend on it?**
