# JDK — Application Model

## Purpose

JDK is an operational application that helps users understand the current and expected state of the business.

The application should organize information around:

```text
Business Situation
    ↓
Understanding
    ↓
Drill-down
    ↓
Action
```

It should not simply expose database entities as disconnected screens.

---

## Application Structure

```text
Login
  ↓
Application Shell
  ↓
Business Timeline
  ↓
Operational Areas
```

The application shell provides:

* navigation;
* user identity;
* role-aware access;
* global application context.

---

## Primary Experience

After login, the user should immediately see the current business context.

The primary experience is:

```text
Business Timeline
        ↓
Select a Date
        ↓
Daily Status
        ↓
Business Situation
        ↓
Drill Down
```

The application should make the business understandable without requiring the user to navigate through multiple unrelated modules.

---

## Business Timeline

The Business Timeline is the primary temporal view of the business.

Each day may contain:

* opening inventory;
* production;
* material receipts;
* material consumption;
* customer commitments;
* deliveries;
* closing inventory;
* significant variances;
* risks.

The timeline should help answer:

> **What happened on this day, and what does it mean for the business?**

---

## Daily Status

Each business day has a Daily Status.

The status should provide a concise view of the day's important business information.

For example:

```text
Opening State
      ↓
Expected Activity
      ↓
Actual Activity
      ↓
Variance
      ↓
Closing State
```

The Daily Status should allow the user to open a detailed report.

The detailed report should support drill-down into the underlying business data.

---

## Business Situation

A Business Situation represents something that requires understanding or attention.

It may arise from:

* a variance;
* a shortage;
* a delay;
* a failed expectation;
* a fulfilment risk;
* a significant change.

The structure is:

```text
What Was Expected?
        ↓
What Happened?
        ↓
What Changed?
        ↓
What Is Affected?
        ↓
What Is At Risk?
        ↓
What Can Be Done?
```

---

## Drill-Down

Drill-down is a core application behavior.

The user should be able to move from:

```text
Summary
    ↓
Daily Status
    ↓
Business Situation
    ↓
Metric
    ↓
Calculation
    ↓
Source Record
```

A drill-down should preserve context.

The user should be able to inspect details and return to the previous view without losing the original context.

Details may be displayed using:

* a modal;
* a detail panel;
* a dedicated page;

depending on the depth and complexity of the information.

The interface should remain clear and avoid unnecessary navigation.

---

## Operational Areas

The application provides access to operational capabilities including:

* customers;
* products and formulas;
* raw materials;
* inventory;
* finished goods;
* suppliers;
* customer orders;
* MRP and ATP;
* feasibility and risk;
* reports.

These are supporting operational areas.

The application should not force the user to understand the underlying database structure in order to understand the business.

---

## Role-Based Experience

Users may have different responsibilities.

The application should adapt access and available actions according to role.

The principle is:

```text
Role
  ↓
Responsibility
  ↓
Relevant Information
  ↓
Permitted Action
```

An executive may need:

```text
What requires attention?
```

An operations user may need:

```text
What must be done?
```

A production user may need:

```text
What must be produced?
```

A procurement user may need:

```text
What must be sourced?
```

The underlying business truth remains the same.

The view and available actions may differ.

---

## Application States

Every important view should account for:

### Loading

Data is being retrieved.

### Empty

No relevant data exists.

### Error

The requested operation failed.

### Restricted

The user does not have permission.

### Partial

Some information is available while another source is unavailable.

The application should communicate these states clearly.

---

## Application Principle

The application should help the user move naturally through:

```text
SEE
  ↓
UNDERSTAND
  ↓
INVESTIGATE
  ↓
DECIDE
  ↓
ACT
```

JDK should not be designed as a collection of unrelated screens.

The application should present the business as a connected operational system.
