# JDK — Feasibility and Risk

## Purpose

JDK should help the business understand whether a commitment can be fulfilled and what may prevent it.

```text
Customer Order
      ↓
Feasibility
      ↓
Risk
      ↓
Business Decision
```

The central question is:

> **Can we fulfil this commitment as promised?**

---

## Feasibility

Feasibility determines whether the required product can be supplied by the required date.

The analysis may consider:

```text
Customer Requirement
      ↓
Finished Goods
      ↓
Production Requirement
      ↓
Formula
      ↓
Materials
      ↓
Supplier Availability
      ↓
Required Date
```

---

## Feasibility Outcomes

A requirement may be classified as:

```text
Feasible
Partially Feasible
Feasible on a Later Date
At Risk
Not Feasible
```

The result must be supported by the underlying facts.

---

## Feasibility Chain

```text
Order
  ↓
Required Quantity
  ↓
Finished Goods Available?
  ↓
Production Required?
  ↓
Materials Available?
  ↓
Materials Expected?
  ↓
Production Possible by Required Date?
  ↓
Fulfilment Feasible?
```

Each step may introduce a constraint.

---

## Risk

Risk exists when a known condition may prevent the expected outcome.

```text
Expected Fulfilment
        ↓
Constraint
        ↓
Potential Impact
        ↓
Risk
```

Examples include:

* insufficient finished goods;
* insufficient raw materials;
* delayed supplier supply;
* production requirement exceeding available material;
* required date earlier than feasible production completion.

---

## Risk Is Not the Same as Failure

The system must distinguish between:

```text
Confirmed Failure
        ≠
Potential Risk
```

For example:

```text
Material Not Available
        +
Supplier Expected Before Production
        ↓
Currently Feasible
```

But:

```text
Material Not Available
        +
Supplier Expected After Required Date
        ↓
At Risk / Not Feasible
```

Risk must therefore consider timing.

---

## Risk Chain

A risk should be traceable to its cause.

```text
Customer Order
      ↓
Product Requirement
      ↓
Production Requirement
      ↓
Material Requirement
      ↓
Material Shortage
      ↓
Supplier Constraint
      ↓
Fulfilment Risk
```

The user should be able to drill down from the risk to the underlying source records.

---

## Risk Categories

Risk may arise from different areas.

```text
Finished Goods Risk
Material Risk
Production Risk
Supplier Risk
Timing Risk
Data Risk
```

Each risk should identify its category.

---

## Finished-Goods Risk

```text
Required Quantity
      >
Available Finished Goods
      ↓
Finished-Goods Risk
```

The system should determine whether the shortfall can be addressed through production.

---

## Material Risk

```text
Production Requirement
      ↓
Material Requirement
      ↓
Available Material
      ↓
Shortage
      ↓
Material Risk
```

The system should identify which product and customer commitments depend on the material.

---

## Supplier Risk

```text
Material Shortage
      ↓
Supplier Expected
      ↓
Expected Date
      ↓
Required Production Date
      ↓
Supplier Risk
```

A supplier is not necessarily a risk merely because material has not yet arrived.

The timing and reliability of expected supply are relevant.

---

## Production Risk

Production risk may arise when:

```text
Required Production
      ↓
Material Constraint
      OR
      ↓
Production Timing Constraint
      ↓
Production Risk
```

The exact capacity model may be introduced as the product evolves.

---

## Timing Risk

A commitment may be feasible in quantity but not by the required date.

```text
Required Date
      <
Earliest Feasible Date
      ↓
Timing Risk
```

This distinction is important.

```text
Can Fulfil
      ≠
Can Fulfil on Time
```

---

## Risk Severity

Risks may be classified according to business impact.

For example:

```text
Low
Medium
High
Critical
```

Severity should be based on defined business rules.

The system must not create arbitrary severity classifications without a clear basis.

---

## Risk Status

A risk may have a lifecycle:

```text
Identified
  ↓
Under Review
  ↓
Resolved
  ↓
Accepted
  ↓
Closed
```

The exact lifecycle depends on how the business manages operational risks.

---

## Risk Impact

A risk should identify what may be affected.

```text
Constraint
      ↓
Affected Product
      ↓
Affected Order
      ↓
Affected Customer
      ↓
Potential Business Impact
```

A single material shortage may affect multiple orders.

```text
Material Shortage
      ├── Order A
      ├── Order B
      └── Order C
```

The system should make this impact visible.

---

## Executive View

The executive should not need to understand every calculation to identify the important risks.

The system should surface:

```text
What Is At Risk?
      ↓
Why?
      ↓
What Is Affected?
      ↓
When?
      ↓
What Can Be Done?
```

The executive view should focus on:

* important commitments;
* significant constraints;
* timing;
* downstream impact;
* unresolved risks.

---

## Drill-Down

Every important risk should be explainable.

```text
Risk
  ↓
Impact
  ↓
Affected Order
  ↓
Product
  ↓
Production Requirement
  ↓
Material
  ↓
Supplier / Inventory
```

The user should be able to move from summary to detail without losing context.

---

## Feasibility and Daily Status

Feasibility and risk are important inputs to the Daily Status.

The daily executive view may show:

```text
Orders Due
      ↓
Orders At Risk
      ↓
Primary Constraints
      ↓
Material Shortages
      ↓
Expected Resolution
```

The daily status should provide a point-in-time operational picture.

---

## Access

Feasibility and risk information is controlled through Perennia Access.

Possible permissions include:

```text
feasibility.view
risk.view
risk.update
risk.resolve
```

The exact permission names must follow Perennia Access conventions.

The backend must enforce all permissions.

---

## Error Handling

Feasibility and risk operations must use stable, unique error codes.

Examples:

```text
FEASIBILITY-001
Unable to determine fulfilment feasibility

FEASIBILITY-002
Required product information is incomplete

FEASIBILITY-003
Required date cannot be evaluated

RISK-001
Risk analysis could not be completed

RISK-002
Risk source cannot be identified

RISK-003
Risk cannot be resolved while the underlying constraint remains active
```

The frontend must use error codes rather than parsing error-message text.

---

## Feasibility and Risk Principle

Feasibility answers:

> **Can we fulfil the commitment?**

Risk answers:

> **What may prevent us from fulfilling it?**

The system should connect both:

```text
Customer Commitment
        ↓
Feasibility
        ↓
Constraints
        ↓
Risk
        ↓
Impact
        ↓
Decision
```

The purpose is not merely to report problems.

It is to help the business understand problems early enough to act.
