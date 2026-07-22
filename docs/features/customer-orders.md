# JDK — Customer Orders

## Purpose

A customer order represents a commitment by the business to supply a product to a customer.

```text
Customer
      ↓
Order
      ↓
Product
      ↓
Quantity
      ↓
Required Date
      ↓
Fulfilment
```

An order is therefore a key input to:

* finished-goods allocation;
* production planning;
* material requirements;
* MRP;
* ATP;
* fulfilment feasibility;
* risk analysis.

---

## Order Lifecycle

The order lifecycle represents the progression of a customer commitment.

```text
Draft
  ↓
Confirmed
  ↓
Planned
  ↓
Partially Fulfilled
  ↓
Fulfilled
```

Possible exception states include:

```text
At Risk
Delayed
Cancelled
```

The exact state model should reflect the actual business process.

---

## Order Information

An order should identify:

```text
Customer
    +
Product
    +
Quantity
    +
Required Date
```

It may also contain information required to:

* identify the order;
* track its status;
* plan fulfilment;
* record fulfilment progress;
* understand related risks.

---

## Order and Finished Goods

The first fulfilment question is:

> **Can the order be fulfilled from available finished goods?**

```text
Customer Order
      ↓
Required Quantity
      ↓
Finished Goods Availability
      ↓
Available / Shortfall
```

If sufficient finished goods exist:

```text
Finished Goods
      ↓
Allocation
      ↓
Fulfilment
```

If not:

```text
Finished Goods Shortfall
      ↓
Production Requirement
```

---

## Order and Production

The remaining requirement may need to be produced.

```text
Order Requirement
      -
Available Finished Goods
      =
Production Requirement
```

Production feasibility may depend on:

```text
Production Requirement
      ↓
Formula
      ↓
Material Requirement
      ↓
Material Availability
      ↓
Production Timing
```

---

## Order and Materials

An order may indirectly create material requirements.

```text
Customer Order
      ↓
Product
      ↓
Formula
      ↓
Raw Materials
      ↓
Material Availability
```

A material shortage may affect the ability to fulfil the order.

---

## Order Feasibility

An order may be classified as:

```text
Feasible
Partially Feasible
Not Feasible
At Risk
```

The classification must be based on the underlying business calculations.

```text
Order
  ↓
Finished Goods
  ↓
Production
  ↓
Materials
  ↓
Suppliers
  ↓
Feasibility
```

---

## Order Risk

An order becomes at risk when a known constraint may prevent fulfilment as planned.

Example:

```text
Order
  ↓
Material Required
  ↓
Material Unavailable
  ↓
Supplier Expected
  ↓
Supplier Date Too Late
  ↓
Production Delayed
  ↓
Order At Risk
```

The risk should be explainable.

The user should be able to drill down from:

```text
Order Risk
      ↓
Cause
      ↓
Requirement
      ↓
Availability
      ↓
Source Records
```

---

## Order Fulfilment

Fulfilment may occur in one or more stages.

```text
Required Quantity
      ↓
Allocated Quantity
      ↓
Produced Quantity
      ↓
Delivered Quantity
      ↓
Remaining Quantity
```

The system should distinguish between:

```text
Ordered
Allocated
Produced
Delivered
Remaining
```

This distinction is important for understanding the actual state of the commitment.

---

## Order Changes

Changes to a confirmed order may affect:

```text
Finished Goods Availability
      ↓
Production Requirement
      ↓
Material Requirement
      ↓
Supplier Requirement
      ↓
Other Customer Commitments
```

Significant changes should therefore be:

* permission-controlled;
* validated;
* auditable.

---

## Order Cancellation

An order may be cancelled according to business rules.

Cancellation may affect:

```text
Existing Allocation
      ↓
Production Requirement
      ↓
Material Requirement
      ↓
Available Capacity
```

The system should preserve the history of the order and its cancellation.

---

## Order Search

Authorized users should be able to search orders using relevant criteria, such as:

* order identifier;
* customer;
* product;
* status;
* required date;
* fulfilment status;
* risk status.

Search should help users find commitments and understand their current state.

---

## Order Operations

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
Confirm
  ↓
Cancel
  ↓
Track Fulfilment
```

The available operations depend on the user's permissions and the order's current state.

---

## Daily Status

Customer orders contribute to the Daily Status.

The daily view may show:

```text
Orders Due
      ↓
Orders Fulfilled
      ↓
Orders Delayed
      ↓
Orders At Risk
```

The user should be able to drill down from the daily summary to individual orders.

---

## Access

Order operations are controlled through Perennia Access.

Possible permissions include:

```text
orders.view
orders.create
orders.update
orders.confirm
orders.cancel
orders.fulfil
```

The exact permission names must follow Perennia Access conventions.

The backend must enforce all permissions.

---

## Error Handling

Order operations must use stable, unique error codes.

Examples:

```text
ORDER-001
Customer order not found

ORDER-002
Invalid product

ORDER-003
Invalid quantity

ORDER-004
Required date is invalid

ORDER-005
Order cannot be confirmed

ORDER-006
Order cannot be cancelled

ORDER-007
Order conflicts with an existing commitment

ORDER-008
Order fulfilment is at risk
```

The frontend must use error codes rather than parsing error-message text.

---

## Customer Order Principle

A customer order is a commitment that propagates through the business.

```text
Customer Order
      ↓
Product Requirement
      ↓
Finished Goods
      ↓
Production
      ↓
Materials
      ↓
Suppliers
      ↓
Fulfilment
```

The key question is:

> **Can this commitment be fulfilled as promised, and if not, what is preventing it?**
