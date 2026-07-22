# JDK — Finished Goods

## Purpose

Finished goods are completed products available for customer fulfilment.

The core flow is:

```text
Raw Materials
      ↓
Production
      ↓
Finished Goods
      ↓
Customer Fulfilment
```

Finished goods may also exist before new production is required.

```text
Finished Goods Inventory
      ↓
Customer Order
      ↓
Allocation / Delivery
```

---

## Finished Goods Availability

The business must distinguish between:

```text
Physical Finished Goods
        ↓
Committed / Allocated Quantity
        ↓
Available Finished Goods
```

The basic concept is:

```text
Physical Finished Goods
      -
Existing Commitments
      =
Available Finished Goods
```

A product may physically exist in inventory but be unavailable for a new customer commitment.

---

## Finished Goods Lifecycle

```text
Production Completed
        ↓
Available
        ↓
Allocated
        ↓
Delivered
```

Possible states may include:

```text
Available
Allocated
Dispatched
Delivered
Blocked
```

The exact lifecycle depends on the operational process.

---

## Finished Goods and Customer Orders

A customer order creates a requirement for finished goods.

```text
Customer Order
      ↓
Product
      ↓
Required Quantity
      ↓
Finished Goods Availability
```

The order may be fulfilled from:

```text
Existing Finished Goods
        +
New Production
```

---

## Allocation

Finished goods may be allocated against customer commitments.

```text
Available Finished Goods
        ↓
Customer Commitment
        ↓
Allocated Quantity
        ↓
Remaining Available Quantity
```

Allocation should be traceable.

The system should be able to answer:

> **Which customer commitment is this finished-goods quantity associated with?**

---

## Finished Goods and Production

Production increases finished-goods availability.

```text
Production
      ↓
Finished Goods Receipt
      ↓
Available Quantity
```

Production output may be compared with the planned production quantity.

```text
Planned Quantity
        ≠
Actual Quantity
        ↓
Production Variance
```

The variance may affect fulfilment feasibility.

---

## Finished Goods Inventory Movement

Finished-goods quantity may change through:

```text
Opening Balance
      +
Production
      -
Allocation
      -
Delivery
      ±
Adjustment
      =
Closing Balance
```

The balance should be explainable through the underlying movements.

```text
Closing Quantity
      ↓
Inventory Calculation
      ↓
Finished-Goods Movements
      ↓
Source Records
```

---

## Finished Goods and ATP

Finished goods are a primary input to Available-to-Promise analysis.

```text
Physical Finished Goods
        ↓
Existing Commitments
        ↓
Available Quantity
        ↓
ATP
```

If available finished goods are insufficient, the system may consider:

```text
Required Production
        ↓
Material Availability
        ↓
Production Timing
        ↓
Fulfilment Feasibility
```

---

## Finished Goods and Risk

A finished-goods shortage may create a fulfilment risk.

```text
Customer Order
      ↓
Required Quantity
      ↓
Available Finished Goods
      ↓
Shortage
      ↓
Production Requirement
      ↓
Potential Delivery Risk
```

The risk should be traceable to:

```text
Customer Commitment
      ↓
Product Requirement
      ↓
Available Quantity
      ↓
Shortfall
```

---

## Finished Goods and Daily Status

Finished goods contribute to the Daily Status.

A daily view may show:

```text
Opening Finished Goods
      +
Production
      -
Allocations
      -
Deliveries
      ±
Adjustments
      =
Closing Finished Goods
```

The user should be able to drill down from a daily figure to the underlying events.

---

## Finished Goods and MRP

MRP should consider existing finished-goods availability before calculating new production requirements.

```text
Customer Requirement
        ↓
Existing Finished Goods
        ↓
Available Quantity
        ↓
Remaining Requirement
        ↓
Production Requirement
```

The intelligence layer should avoid treating the entire customer requirement as a new production requirement when sufficient finished goods already exist.

---

## Access

Finished-goods operations are controlled through Perennia Access.

Possible permissions include:

```text
finished_goods.view
finished_goods.allocate
finished_goods.adjust
finished_goods.receive
finished_goods.dispatch
```

The exact permission names must follow Perennia Access conventions.

The backend must enforce all permissions.

---

## Error Handling

Finished-goods operations must use stable, unique error codes.

Examples:

```text
FINISHED-GOODS-001
Finished-goods record not found

FINISHED-GOODS-002
Insufficient available finished goods

FINISHED-GOODS-003
Quantity cannot be allocated

FINISHED-GOODS-004
Invalid finished-goods movement

FINISHED-GOODS-005
Allocation conflicts with an existing commitment
```

The frontend must use error codes rather than parsing error-message text.

---

## Finished-Goods Principle

Finished goods are the bridge between:

```text
Production
      ↓
Available Product
      ↓
Customer Commitment
      ↓
Fulfilment
```

The key question is:

> **What finished goods are available, what is already committed, and what additional production is required to fulfil the remaining commitments?**

Finished goods are deliberately kept separate from raw-material inventory. The two are related, but they serve different business purposes:

* **Materials** enable production.
* **Finished goods** enable fulfilment.

That distinction is important when implementing MRP, ATP, Daily Status, and risk analysis.
