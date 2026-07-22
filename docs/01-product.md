# JDK — Product

## What JDK Is

JDK is a manufacturing operations platform that connects business commitments with the operational resources required to fulfil them.

It helps a business understand:

* what it has committed to;
* what is required to fulfil those commitments;
* what is currently available;
* what is expected to happen;
* what actually happened;
* what has changed;
* what is at risk;
* and what action may be required.

The fundamental product flow is:

```text
Commitment
    ↓
Requirement
    ↓
Availability
    ↓
Expected
    ↓
Actual
    ↓
Variance
    ↓
Impact
    ↓
Risk
    ↓
Action
```

---

## The Product Problem

Manufacturing operations are connected.

A customer commitment may depend on:

```text
Customer Order
    ↓
Product
    ↓
Formula
    ↓
Raw Materials
    ↓
Supplier Availability
    ↓
Production
    ↓
Finished Goods
    ↓
Delivery
```

JDK connects these relationships so that the business can understand the consequences of operational events.

For example:

```text
Material Shortage
    ↓
Production Delay
    ↓
Order at Risk
```

The product should help answer:

> **What is happening, why is it happening, what does it affect, and what should happen next?**

---

## Product Philosophy

### Business meaning over database structure

The application should be organized around business activities, decisions, and responsibilities — not simply around database tables.

### Facts must be explainable

Important results should be traceable to their underlying data and calculations.

```text
Fact
  ↓
Calculation
  ↓
Interpretation
  ↓
Risk
```

### Drill-down is fundamental

Users should be able to move from:

```text
Summary
  ↓
Business Situation
  ↓
Cause
  ↓
Source Data
```

### Roles represent responsibility

Different users should see the information and actions relevant to their responsibilities.

### Preserve operational truth

The system should maintain a clear distinction between source data, calculated results, and interpretation.

---

## Product Direction

JDK is evolving from an operational MVP into a production-grade business operations platform.

The primary experience will move toward:

```text
Business Timeline
    ↓
Daily Status
    ↓
Business Situation
    ↓
Impact
    ↓
Risk
    ↓
Action
```

The existing operational capabilities — customers, products, formulas, materials, inventory, suppliers, orders, and MRP/ATP — form the foundation for this direction.

---

## Product Test

A feature belongs in the core JDK product when it helps the business understand:

> **What is happening, why it is happening, what it affects, what is at risk, or what should happen next.**
