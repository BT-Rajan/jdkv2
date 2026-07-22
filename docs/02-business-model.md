# JDK — Business Model

## 1. The Business

JDK is designed for a manufacturing business that converts customer commitments into finished products through the coordinated use of:

* finished-goods inventory;
* raw materials;
* suppliers;
* production capacity;
* time.

The business must continuously answer:

> **Can we fulfil our customer commitments with the resources currently available or expected to become available?**

---

## 2. The Core Business Flow

```text
Customer
    ↓
Customer Order
    ↓
Product
    ↓
Formula / BOM
    ↓
Raw Material Requirement
    ↓
Material Availability
    ↓
Production Requirement
    ↓
Finished Goods
    ↓
Delivery
```

A customer order may be fulfilled from:

```text
Existing Finished Goods
        +
New Production
```

New production may require:

```text
Raw Materials
        ↓
Supplier Supply
```

---

## 3. Commitments Drive the Business

A customer order creates a commitment.

The commitment has:

* a customer;
* a product;
* a quantity;
* a required date.

The commitment creates requirements across the business.

```text
Customer Commitment
        ↓
Finished Goods Requirement
        ↓
Production Requirement
        ↓
Material Requirement
        ↓
Supplier Requirement
```

A problem in any part of this chain can affect fulfilment.

---

## 4. Inventory and Production

The business has two important inventory categories:

### Raw Materials

Used to manufacture products.

```text
Opening Stock
    +
Receipts
    -
Consumption
    ±
Adjustments
    =
Closing Stock
```

### Finished Goods

Available to fulfil customer commitments.

```text
Opening Stock
    +
Production
    -
Allocations / Deliveries
    ±
Adjustments
    =
Closing Stock
```

Inventory availability is not the same as physical stock.

The business must distinguish between:

```text
Physical Stock
    -
Existing Commitments
    =
Available Stock
```

---

## 5. Suppliers

Suppliers affect the ability to fulfil customer commitments.

A material requirement must be considered together with:

* current stock;
* expected receipts;
* supplier lead time;
* required production date.

A material shortage may therefore create a future production or delivery risk.

---

## 6. Production

Production converts raw materials into finished goods.

Production planning must consider:

* what needs to be produced;
* how much needs to be produced;
* when it is required;
* what materials are required;
* whether those materials are available;
* whether the production timing supports the customer commitment.

---

## 7. The Business Decision Chain

The central business chain is:

```text
Customer Commitment
        ↓
What must be fulfilled?
        ↓
What is already available?
        ↓
What must be produced?
        ↓
What materials are required?
        ↓
What materials are available?
        ↓
What must be sourced?
        ↓
When can production happen?
        ↓
Can the commitment be fulfilled?
```

---

## 8. Business Risk

A business risk occurs when an expected commitment may not be fulfilled as planned.

Examples:

```text
Material Shortage
        ↓
Production Delay
        ↓
Customer Order Risk
```

or:

```text
Supplier Delay
        ↓
Material Unavailable
        ↓
Production Delayed
        ↓
Delivery Delayed
```

The business must therefore understand not only the current state, but also the effect of current conditions on future commitments.

---

## 9. The Business Model in One View

```text
CUSTOMER
    ↓
COMMITMENT
    ↓
PRODUCT
    ↓
MATERIALS + PRODUCTION
    ↓
FINISHED GOODS
    ↓
DELIVERY

SUPPLIERS
    ↓
MATERIAL AVAILABILITY
    ↓
PRODUCTION CAPABILITY
    ↓
FULFILMENT CAPABILITY
```

JDK exists to make these relationships visible and actionable.
