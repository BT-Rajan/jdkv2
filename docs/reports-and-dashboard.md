# JDK — Reports and Dashboard

## Purpose

JDK should convert operational data into a clear understanding of the business.

The system should follow:

```text
Business Data
      ↓
Operational Position
      ↓
Risks and Constraints
      ↓
Decision
```

The dashboard provides the summary.

Reports provide the detail.

---

## Dashboard

The dashboard should answer:

> **What is happening in the business today?**

> **What requires attention?**

> **What may affect customer commitments?**

The dashboard should not attempt to display every available data point.

---

## Executive Dashboard

The executive dashboard may present:

```text
Customer Commitments
        ↓
Fulfilment Position
        ↓
Production Position
        ↓
Inventory Position
        ↓
Material Constraints
        ↓
Business Risk
```

Important information should be visible without requiring the user to navigate through multiple screens.

---

### Daily Operational Position

The dashboard may show:

```text
Opening Stock
Production
Consumption
Closing Stock
```

For relevant business areas:

* raw materials;
* finished goods;
* production;
* customer orders.

The exact metrics depend on the business data available.

---

## Calendar-Based View

The calendar is an important operational navigation surface.

Each day may contain a Daily Status entry.

```text
Date
  ↓
Daily Status
  ↓
Operational Summary
  ↓
Drill Down
```

A calendar day may show indicators such as:

```text
Production
Inventory
Orders
Fulfilment
Risks
```

The calendar should help users understand how the operational position changes over time.

---

## Daily Status Report

The Daily Status Report provides a point-in-time view of the business.

It may include:

```text
Opening Position
      ↓
Activity During the Day
      ↓
Closing Position
      ↓
Exceptions
      ↓
Risks
```

For example:

```text
Opening Inventory
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
Closing Inventory
```

The report should make the calculation understandable.

---

## Drill-Down

Summary information must be actionable.

```text
Dashboard Metric
      ↓
Daily Status
      ↓
Business Category
      ↓
Source Records
```

For example:

```text
Material Shortage
      ↓
Material
      ↓
Required Quantity
      ↓
Available Quantity
      ↓
Affected Products
      ↓
Affected Orders
```

The user should be able to move from summary to detail without losing context.

---

## Reports

Reports should answer specific business questions.

Examples:

```text
What was produced?
What was consumed?
What is available?
What is committed?
What is at risk?
What is delayed?
What is required?
```

A report should have a clear purpose.

JDK should avoid creating reports that merely reproduce database tables.

---

## Core Report Areas

Reports may cover:

### Inventory

```text
Opening
Movements
Closing
Availability
Shortages
```

### Production

```text
Planned
Produced
Variance
```

### Customer Orders

```text
Orders
Due
Fulfilled
Delayed
At Risk
```

### Materials

```text
Required
Available
Short
Expected
```

### Suppliers

```text
Expected Supply
Received
Delayed
Outstanding
```

### Feasibility and Risk

```text
At-Risk Orders
Constraints
Causes
Impact
```

---

## Executive and Operational Views

Different users may require different levels of information.

```text
Executive
    ↓
Summary
    ↓
Manager
    ↓
Analysis
    ↓
Operator
    ↓
Transaction Detail
```

The same underlying business data may be presented at different levels of abstraction.

---

## Role-Aware Dashboards

The dashboard should reflect the user's permissions and role.

A user should see:

* information they are authorized to access;
* actions they are authorized to perform;
* relevant business information for their responsibilities.

The frontend may adapt the interface.

The backend must always enforce access.

---

## Time-Based Analysis

Reports should support meaningful time-based analysis where appropriate.

Examples:

```text
Today
Yesterday
This Week
This Month
Custom Period
```

Time-based comparisons may help identify:

* trends;
* changes;
* recurring constraints;
* improving or deteriorating operational conditions.

---

## Report Status

Reports should indicate the time context of the information.

For example:

```text
As of:
22 July 2026
14:30
```

The user should understand whether information is:

```text
Current
Historical
Projected
```

These must not be confused.

---

## Dashboard Data

The dashboard should not contain independent business calculations that contradict the domain services.

```text
Authoritative Business Data
          ↓
      Domain Services
          ↓
      Dashboard / Reports
```

The dashboard is a consumer of business intelligence.

It should not become a second source of truth.

---

## Performance

Dashboard and report generation should be designed for the expected user population and data volume.

The system should:

* avoid unnecessary repeated calculations;
* load summaries efficiently;
* allow detailed information to be loaded when requested;
* avoid blocking the entire interface for a single slow report.

The interface should clearly indicate loading, empty, and error states.

---

## Report Export

Where required, reports may support export for authorized users.

Possible formats may include:

```text
PDF
Spreadsheet
CSV
```

Export should respect:

* user permissions;
* data access rules;
* the selected filters and time period.

---

## Error Handling

Reports and dashboards must use stable, unique error codes.

Examples:

```text
REPORT-001
Report could not be generated

REPORT-002
Invalid report parameters

REPORT-003
No data available

REPORT-004
Report export failed

DASHBOARD-001
Dashboard data could not be loaded

DASHBOARD-002
Dashboard data is temporarily unavailable
```

The frontend must use error codes rather than parsing error-message text.

---

## Reports and Dashboard Principle

The dashboard should answer:

> **What requires attention?**

The report should answer:

> **Why?**

The drill-down should answer:

> **What is the evidence?**

```text
Dashboard
    ↓
Report
    ↓
Drill-Down
    ↓
Source Records
```

The purpose of JDK reporting is not to display more information.

It is to help the right person understand the operational position and act on it.
