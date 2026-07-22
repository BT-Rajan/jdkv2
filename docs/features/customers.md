# JDK — Customers

## Purpose

Customers are organisations or individuals to whom the business supplies products.

A customer may have:

```text
Customer
    ↓
Orders
    ↓
Products
    ↓
Fulfilment
```

The customer is the starting point for the business commitment chain.

---

## Customer Lifecycle

```text
Create
  ↓
Active
  ↓
Orders
  ↓
Fulfilment
  ↓
Inactive / Archived
```

A customer should not normally be physically deleted if historical orders or business records depend on the customer.

---

## Customer Information

The system may maintain information required to:

* identify the customer;
* communicate with the customer;
* process orders;
* fulfil commitments;
* maintain business records.

The exact fields are defined by the implementation and business requirements.

The domain should distinguish between:

```text
Customer Identity
      +
Contact Information
      +
Business Information
      +
Operational History
```

---

## Customer Operations

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

The available operations depend on the user's permissions.

---

## Customer Search

Users should be able to find customers using relevant identifying information.

Search should support the business need rather than requiring users to know internal identifiers.

Possible search criteria include:

* name;
* contact information;
* customer identifier;
* status.

Search results should be clear and should allow the user to open the customer's business context.

---

## Customer View

The customer view should provide relevant business context.

Depending on user role, this may include:

```text
Customer
    ↓
Orders
    ↓
Products
    ↓
Commitments
    ↓
Fulfilment Status
```

The customer should not be treated as an isolated database record.

---

## Customer and Orders

A customer may have multiple orders.

```text
Customer
    └── Order
          ├── Product
          ├── Quantity
          ├── Required Date
          └── Fulfilment Status
```

Customer orders create business commitments.

---

## Customer and Business Risk

A customer may be affected by operational constraints.

```text
Customer Order
      ↓
Material Requirement
      ↓
Material Constraint
      ↓
Production Risk
      ↓
Customer Fulfilment Risk
```

The customer view should eventually make relevant fulfilment risks visible.

---

## Customer Status

A customer may have an operational status such as:

```text
Active
Inactive
Archived
```

Status should reflect the business lifecycle and should not be confused with authentication or system-user status.

---

## Deactivation

Deactivation should be preferred over deletion when historical business data exists.

```text
Active Customer
      ↓
Inactive Customer
```

Historical orders and related business records should remain traceable.

---

## Access

Customer operations are controlled by Perennia Access.

Examples of JDK-specific permissions may include:

```text
customers.view
customers.create
customers.update
customers.deactivate
```

The exact permission names should follow the Perennia Access conventions.

The frontend may hide unavailable actions, but the backend must enforce access.

---

## Error Handling

Customer operations must use stable, unique error codes.

Examples:

```text
CUSTOMER-001
Customer not found

CUSTOMER-002
Customer already exists

CUSTOMER-003
Customer cannot be deactivated

CUSTOMER-004
Invalid customer information
```

The frontend must use the error code rather than parsing the error message.

---

## Customer Principle

A customer is not merely a master-data record.

A customer represents a business relationship that may contain:

```text
Customer
    ↓
Commitments
    ↓
Orders
    ↓
Products
    ↓
Fulfilment
    ↓
Business Risk
```

JDK should preserve this context as the product evolves.
