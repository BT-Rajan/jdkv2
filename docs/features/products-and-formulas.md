# JDK — Products and Formulas

## Purpose

Products are the finished goods that the business sells and supplies.

A formula defines the materials required to produce a product.

```text
Product
    ↓
Formula
    ↓
Raw Materials
```

This relationship is fundamental to:

* production;
* material planning;
* inventory;
* MRP;
* fulfilment feasibility.

---

## Products

### Product Lifecycle

```text
Create
  ↓
Active
  ↓
Manufactured / Sold
  ↓
Inactive
  ↓
Archived
```

A product may be:

```text
Active
Inactive
Archived
```

An inactive product should not normally be available for new operational transactions.

Historical transactions must remain traceable.

---

### Product Operations

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
Activate / Deactivate
```

The available operations depend on the user's permissions.

---

### Product and Customer Orders

A customer order refers to a product.

```text
Customer Order
      ↓
Product
      ↓
Required Quantity
      ↓
Required Date
```

A product may therefore have multiple customer commitments.

---

## Formulas

### Purpose

A formula defines what is required to produce a quantity of a product.

Conceptually:

```text
Product
    ↓
Formula
    ↓
Material A
Material B
Material C
```

For example:

```text
Product X
    ↓
Formula
    ├── Material A — Quantity
    ├── Material B — Quantity
    └── Material C — Quantity
```

The formula is used to calculate material requirements.

---

### Formula Quantity

A formula defines the material requirement for a defined quantity of finished product.

Conceptually:

```text
Product Requirement
        ×
Formula Requirement
        =
Material Requirement
```

For example:

```text
1 Unit of Product
        ↓
Material A: 2 Units
Material B: 5 Units
```

If the requirement is increased, the material requirement increases proportionally unless the business rules specify otherwise.

---

### Formula Version

A product may have different formulas over time.

```text
Product
   ↓
Formula Version 1
   ↓
Formula Version 2
   ↓
Formula Version 3
```

Formula changes may affect:

* material requirements;
* production;
* inventory planning;
* MRP;
* future fulfilment calculations.

Historical operations should remain associated with the formula applicable at the time.

---

### Formula Status

A formula may have a lifecycle:

```text
Draft
  ↓
Active
  ↓
Superseded
  ↓
Archived
```

Only an appropriate active formula should be used for new production or planning calculations.

---

### Formula Changes

Changes to formulas are operationally significant.

A change may alter:

```text
Formula
    ↓
Material Requirement
    ↓
Inventory Requirement
    ↓
Production Requirement
    ↓
Fulfilment Feasibility
```

Formula changes should therefore be:

* permission-controlled;
* validated;
* auditable.

---

## Product and Material Relationship

```text
Product
    │
    └── Formula
          │
          ├── Raw Material A
          ├── Raw Material B
          └── Raw Material C
```

A raw material may be used in multiple products.

```text
Raw Material
    ├── Product A
    ├── Product B
    └── Product C
```

This relationship is important because a shortage of one material may affect multiple products and customer commitments.

---

## Product and MRP

The formula is one of the inputs to MRP.

```text
Customer Orders
        ↓
Product Requirement
        ↓
Formula
        ↓
Material Requirement
        ↓
Material Availability
```

The product and formula model must therefore provide reliable data to the intelligence layer.

---

## Product and Feasibility

A product commitment may be affected by:

* finished-goods availability;
* production requirements;
* formula requirements;
* raw-material availability;
* supplier availability.

```text
Customer Order
      ↓
Product
      ↓
Formula
      ↓
Materials
      ↓
Availability
      ↓
Fulfilment Feasibility
```

---

## Access

Product and formula operations are controlled through Perennia Access.

Possible permissions include:

```text
products.view
products.create
products.update
products.deactivate

formulas.view
formulas.create
formulas.update
formulas.activate
formulas.archive
```

The exact permission names must follow the Perennia Access conventions.

The backend must enforce all permissions.

---

## Error Handling

Product and formula operations must use stable error codes.

Examples:

```text
PRODUCT-001
Product not found

PRODUCT-002
Product already exists

PRODUCT-003
Product cannot be deactivated

FORMULA-001
Formula not found

FORMULA-002
Formula contains invalid material

FORMULA-003
Formula cannot be activated

FORMULA-004
Formula change conflicts with an existing operation
```

The frontend must use error codes rather than interpreting error-message text.

---

## Product Principle

A product is not simply a catalogue item.

Within JDK:

```text
Product
    ↓
Formula
    ↓
Materials
    ↓
Production
    ↓
Finished Goods
    ↓
Customer Fulfilment
```

The product and formula model is therefore a foundation of the entire operational intelligence chain.
