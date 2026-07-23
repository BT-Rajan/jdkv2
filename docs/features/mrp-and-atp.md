# JDK — MRP and ATP

## Purpose

MRP and ATP convert business commitments into operational answers.

```text
Customer Orders
      ↓
MRP
      ↓
Material & Production Requirements
      ↓
ATP
      ↓
What Can Be Fulfilled
```

Together, they answer:

> **Can we fulfil our commitments, and what is required to do so?**

---

## MRP

### Material Requirements Planning

MRP determines what materials are required to fulfil product requirements.

```text
Customer Orders
      ↓
Finished Goods
      ↓
Production Requirement
      ↓
Formula
      ↓
Material Requirement
```

MRP considers:

* customer requirements;
* existing finished goods;
* production requirements;
* product formulas;
* current material inventory;
* existing material commitments;
* expected supplier receipts.

---

## MRP Calculation Chain

```text
Customer Requirement
        ↓
Existing Finished Goods
        ↓
Remaining Product Requirement
        ↓
Production Requirement
        ↓
Formula
        ↓
Gross Material Requirement
        ↓
Available Material
        ↓
Net Material Requirement
```

Conceptually:

```text
Net Requirement
=
Gross Requirement
-
Available Material
```

The exact calculation must account for the relevant business rules.

---

## MRP Output

MRP should produce actionable results.

Possible outputs include:

```text
Material Required
Material Available
Material Shortage
Production Required
Expected Supply
Supply Date
Potential Constraint
```

The output should allow the user to understand:

> **What is required, what is available, and what is missing?**

---

## MRP Traceability

Every material requirement should be explainable.

```text
Material Shortage
      ↓
Material Requirement
      ↓
Product Requirement
      ↓
Customer Order
```

The system should be able to answer:

> **Why is this material required?**

and:

> **Which customer commitments are affected by this shortage?**

---

## ATP

### Available-to-Promise

ATP determines what the business can commit to a customer.

The basic flow is:

```text
Customer Requirement
      ↓
Existing Finished Goods
      ↓
Existing Commitments
      ↓
Production Possibility
      ↓
Material Availability
      ↓
Available-to-Promise
```

ATP should answer:

> **How much can we supply, and by when?**

---

## ATP Outcomes

An order or requirement may be classified as:

```text
Available
Partially Available
Available on Future Date
At Risk
Not Available
```

The result should be supported by the underlying calculations.

---

## ATP and Finished Goods

The first consideration is existing finished-goods availability.

```text
Physical Finished Goods
      -
Existing Commitments
      =
Available Finished Goods
```

If the available quantity is sufficient:

```text
Available Finished Goods
      ↓
ATP
```

If it is insufficient:

```text
Shortfall
      ↓
Production Requirement
```

---

## ATP and Production

A shortfall may be fulfilled through future production.

```text
Customer Requirement
      -
Available Finished Goods
      =
Production Requirement
```

The production requirement must then be evaluated against:

```text
Formula
      ↓
Material Requirement
      ↓
Material Availability
      ↓
Supplier Availability
      ↓
Production Feasibility
```

---

## MRP and ATP Relationship

MRP and ATP are related but distinct.

```text
             Customer Order
                   │
          ┌────────┴────────┐
          ▼                 ▼
        ATP               MRP
          │                 │
Can we fulfil?      What is required?
          │                 │
          └────────┬────────┘
                   ▼
            Fulfilment Decision
```

MRP provides the supply-side requirements.

ATP evaluates the fulfilment commitment.

---

## Order-Level Analysis

For each customer order, JDK should be able to determine:

```text
Required Quantity
      ↓
Available Finished Goods
      ↓
Production Requirement
      ↓
Material Requirement
      ↓
Material Availability
      ↓
Expected Supply
      ↓
Fulfilment Date
```

The result should be explainable rather than simply presenting a black-box status.

---

## Material Shortage Impact

A material shortage may affect multiple products.

```text
Material Shortage
      ├── Product A
      │      └── Customer Order 1
      │
      ├── Product B
      │      └── Customer Order 2
      │
      └── Product C
             └── Customer Order 3
```

The intelligence layer should help identify the downstream impact of a constraint.

---

## Prioritization

When resources are insufficient, the system may need to identify competing requirements.

```text
Limited Material
      ↓
Multiple Requirements
      ↓
Competing Commitments
      ↓
Potential Fulfilment Impact
```

JDK should expose the constraint and its impact.

Any prioritization rules must be explicitly defined by the business.

The system must not silently invent priority.

---

## Daily Status Integration

MRP and ATP contribute to the Daily Status.

The executive view may show:

```text
Orders
    ↓
Fulfilment Position
    ↓
At-Risk Orders
    ↓
Material Shortages
    ↓
Production Requirements
```

A user should be able to drill down:

```text
At-Risk Order
      ↓
Cause
      ↓
Material Shortage
      ↓
Required Quantity
      ↓
Current Availability
      ↓
Expected Supply
```

---

## Intelligence Principle

MRP and ATP should not merely produce numbers.

They should produce understanding.

The system should help answer:

> **What is happening?**

> **Why is it happening?**

> **What will be affected?**

> **What is required to resolve it?**

---

## Access

MRP and ATP operations are controlled through Perennia Access.

Possible permissions include:

```text
mrp.view
mrp.run

atp.view
atp.calculate

fulfilment_risk.view
```

The exact permission names must follow Perennia Access conventions.

The backend must enforce all permissions.

---

## Error Handling

MRP and ATP operations must use stable, unique error codes.

Examples:

```text
MRP-001
Unable to calculate material requirement

MRP-002
Active formula not available

MRP-003
Invalid material availability

MRP-004
Requirement calculation conflict

ATP-001
Unable to calculate availability

ATP-002
Insufficient finished-goods availability

ATP-003
Fulfilment date cannot be determined

ATP-004
ATP calculation depends on unresolved material constraint
```

The frontend must use error codes rather than parsing error-message text.

---

## MRP and ATP Principle

MRP answers:

> **What do we need to fulfil our commitments?**

ATP answers:

> **What can we actually promise?**

Together:

```text
Customer Commitment
        ↓
        ├── ATP → Can We Fulfil?
        │
        └── MRP → What Is Required?
                         ↓
                  Materials & Production
```

The purpose of JDK intelligence is to connect these answers into one understandable operational picture.
