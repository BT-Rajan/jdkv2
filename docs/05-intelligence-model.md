# JDK — Intelligence Model

## Purpose

JDK uses operational data to determine whether business commitments can be fulfilled.

The intelligence layer transforms:

```text
Operational Data
      ↓
Calculations
      ↓
Feasibility
      ↓
Risk
```

It should help answer:

> **Given what the business has committed to and what resources are available, what can be fulfilled, what cannot, and why?**

---

## Intelligence Flow

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
Supplier Lead Time
      ↓
Production Timing
      ↓
Fulfilment Feasibility
```

---

## MRP

MRP determines what materials and production are required to fulfil customer commitments.

It considers:

* customer orders;
* product formulas;
* finished-goods availability;
* existing reservations;
* production requirements;
* raw-material requirements;
* current inventory;
* expected material availability.

The output may include:

```text
Required Production
Required Materials
Material Shortages
```

---

## ATP

ATP determines what quantity can be promised based on current and expected availability.

The basic principle is:

```text
Available Quantity
    =
Physical Stock
    -
Existing Commitments
```

Depending on the business situation, future production and expected material availability may also affect fulfilment feasibility.

---

## Feasibility

Feasibility evaluates whether a customer commitment can be fulfilled.

A commitment may be:

```text
Feasible
Partially Feasible
Not Feasible
At Risk
```

The result should be based on the underlying requirements and constraints.

---

## Constraints

The intelligence layer identifies constraints such as:

* insufficient finished goods;
* insufficient raw materials;
* production requirements;
* supplier lead times;
* delayed material availability;
* production timing limitations.

A constraint may affect a downstream commitment.

```text
Material Constraint
      ↓
Production Constraint
      ↓
Fulfilment Constraint
```

---

## Risk

Risk is derived from the relationship between a commitment and its constraints.

```text
Commitment
      ↓
Requirement
      ↓
Constraint
      ↓
Potential Impact
      ↓
Risk
```

For example:

```text
Customer Order
      ↓
Material Required
      ↓
Material Unavailable
      ↓
Production Delayed
      ↓
Order At Risk
```

Risk should be explainable.

The system should be able to show:

```text
Risk
  ↓
Cause
  ↓
Calculation
  ↓
Source Data
```

---

## Intelligence Output

The intelligence layer should produce information that can be consumed by:

* operational workflows;
* daily status;
* business situations;
* reports;
* dashboards;
* future decision-support capabilities.

The separation should be:

```text
Source Data
      ↓
Intelligence Calculation
      ↓
Business Interpretation
      ↓
User Experience
```

---

## Deterministic Foundation

The current JDK intelligence capability is primarily deterministic.

It is based on:

* known business data;
* defined formulas;
* inventory quantities;
* customer commitments;
* supplier information;
* lead times;
* production requirements;
* explicit calculations.

The result should be reproducible and explainable.

Future AI capabilities may be added above this foundation, but AI should not replace the underlying business calculations.

---

## Intelligence Principle

JDK should not merely report:

> **What is the current number?**

It should progressively help determine:

```text
What is available?
      ↓
What is required?
      ↓
What is missing?
      ↓
What is affected?
      ↓
What is at risk?
```

The intelligence layer provides the calculations and conclusions that allow the application to present the business situation clearly.
