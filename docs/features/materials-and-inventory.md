# JDK — Materials and Inventory

## Purpose

Materials and inventory represent the physical resources required to manufacture and fulfil products.

The core relationship is:

```text
Raw Material
    ↓
Inventory
    ↓
Production
    ↓
Finished Product
```

Inventory is not only a number.

JDK must distinguish between:

```text
Physical Stock
      ↓
Committed / Reserved Stock
      ↓
Available Stock
```

---

## Materials

A material is a resource used in the manufacture of one or more products.

A material may be:

* held in inventory;
* consumed in production;
* supplied by one or more suppliers;
* required by multiple product formulas.

```text
Material
    ├── Formula A
    ├── Formula B
    └── Formula C
```

A material shortage may therefore affect multiple products and customer commitments.

---

## Material Lifecycle

```text
Create
  ↓
Active
  ↓
Used in Operations
  ↓
Inactive
  ↓
Archived
```

A material should not normally be deleted if historical inventory or production records depend on it.

---

## Inventory

Inventory represents the quantity of a material or finished product available to the business.

JDK should maintain a clear distinction between:

```text
Opening Quantity
      +
Receipts / Production
      -
Consumption / Deliveries
      ±
Adjustments
      =
Closing Quantity
```

The exact movement types depend on the material or product context.

---

## Inventory Availability

The basic availability concept is:

```text
Physical Stock
      -
Existing Commitments
      =
Available Stock
```

A quantity may physically exist but not be available for a new commitment.

For example:

```text
Physical Stock: 100
Existing Commitments: 80
Available Stock: 20
```

Availability calculations must be performed consistently throughout the system.

---

## Inventory Movements

Inventory changes should be represented as business events or movements.

Examples include:

```text
Opening Balance
Receipt
Production
Consumption
Allocation
Delivery
Adjustment
Transfer
```

The inventory balance should be explainable from its movements.

```text
Opening Balance
      ↓
+ Receipts
      ↓
+ Production
      ↓
- Consumption
      ↓
- Deliveries
      ↓
± Adjustments
      ↓
Closing Balance
```

---

## Inventory Adjustments

Inventory adjustments change the recorded quantity to reflect an approved business correction.

Adjustments must be:

* permission-controlled;
* validated;
* auditable.

An adjustment should record:

```text
Who
  ↓
Changed What
  ↓
From Which Quantity
  ↓
To Which Quantity
  ↓
Why
  ↓
When
```

An adjustment must not silently overwrite historical truth.

---

## Material Requirements

Material requirements are derived from production requirements and formulas.

```text
Product Requirement
        ↓
Formula
        ↓
Material Requirement
        ↓
Available Inventory
        ↓
Shortage / Surplus
```

The same material may be required by multiple products.

The intelligence layer must therefore consider total relevant requirements.

---

## Material Shortage

A material shortage exists when the required quantity exceeds the available quantity.

```text
Required Quantity
      >
Available Quantity
      ↓
Shortage
```

A shortage may result in:

```text
Material Shortage
      ↓
Production Constraint
      ↓
Customer Fulfilment Risk
```

The shortage should be traceable to the requirements that caused it.

---

## Inventory and Daily Status

Inventory contributes to the Daily Status.

A daily status may include:

```text
Opening Stock
      +
Receipts
      +
Production
      -
Consumption
      -
Deliveries
      ±
Adjustments
      =
Closing Stock
```

The system should allow users to drill down from a daily inventory figure to the underlying movements.

```text
Daily Figure
      ↓
Inventory Calculation
      ↓
Inventory Movements
      ↓
Source Records
```

---

## Inventory and MRP

Inventory is a primary input to MRP.

```text
Customer Orders
      ↓
Production Requirement
      ↓
Material Requirement
      ↓
Inventory Availability
      ↓
Shortage / Surplus
```

MRP should not independently maintain a competing inventory balance.

Inventory remains the authoritative source of recorded stock.

---

## Material and Suppliers

Materials may be supplied by one or more suppliers.

```text
Material
    ├── Supplier A
    ├── Supplier B
    └── Supplier C
```

Supplier availability and expected receipts may affect future material availability.

```text
Current Stock
      +
Expected Receipts
      ↓
Future Availability
```

---

## Material and Production

Materials are consumed during production.

```text
Material Inventory
      ↓
Production Consumption
      ↓
Finished Goods
```

The actual consumption may be compared with the expected formula requirement.

This may produce a variance:

```text
Expected Consumption
        ≠
Actual Consumption
        ↓
Production Variance
```

---

## Access

Materials and inventory operations are controlled through Perennia Access.

Possible permissions include:

```text
materials.view
materials.create
materials.update
materials.deactivate

inventory.view
inventory.adjust
inventory.receive
inventory.consume
```

The exact permission names must follow Perennia Access conventions.

The backend must enforce all permissions.

---

## Error Handling

Material and inventory operations must use stable, unique error codes.

Examples:

```text
MATERIAL-001
Material not found

MATERIAL-002
Material already exists

MATERIAL-003
Material cannot be deactivated

INVENTORY-001
Inventory record not found

INVENTORY-002
Insufficient available inventory

INVENTORY-003
Invalid inventory movement

INVENTORY-004
Inventory adjustment requires authorization

INVENTORY-005
Inventory operation conflicts with an existing commitment
```

The frontend must use error codes rather than parsing error-message text.

---

## Inventory Principle

Inventory must be explainable.

At any point, the system should be able to answer:

> **How did we arrive at this quantity?**

The answer should be traceable through:

```text
Opening Balance
      ↓
Movements
      ↓
Commitments
      ↓
Availability
      ↓
Current Position
```

Inventory is therefore both:

```text
A Physical Business Resource
              +
A Source of Operational Intelligence
```
