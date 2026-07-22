# JDK — Development Guide

## 1. Purpose

This document defines how JDK should be developed.

The objective is to build a production-grade application that is:

* understandable;
* reusable;
* maintainable;
* secure;
* predictable;
* easy to extend.

The application should prefer simple, well-defined solutions over unnecessary abstraction.

---

## 2. Understand Before Implementing

Before implementing a feature, understand:

```text
Product
    ↓
Business Model
    ↓
Domain
    ↓
Application Experience
    ↓
Architecture
```

Before writing code, answer:

* What business problem does this solve?
* Who uses it?
* What business concept does it represent?
* What data does it require?
* What rules apply?
* What can go wrong?
* Who is allowed to perform the operation?
* What should happen after success?

Do not begin with the screen or database table alone.

---

## 3. Prefer Reusable Solutions

Code should be designed for reuse where reuse represents a real common concept.

Prefer:

```text
Reusable Component
Reusable Service
Reusable Domain Rule
Reusable Validation
Reusable Error Definition
```

over repeatedly implementing the same behavior.

Examples:

* shared table behavior;
* shared form controls;
* shared date handling;
* shared API client;
* shared authentication handling;
* shared error presentation;
* shared business calculations.

However, do not create abstractions merely to avoid a few repeated lines of code.

> **Reuse a concept, not just code.**

---

## 4. Keep Interfaces Simple

Every interface should expose only what its consumer needs.

A component should not require unnecessary configuration.

A service should not expose internal implementation details.

Prefer:

```text
DailyStatusService
    ↓
getDailyStatus(date)
```

over exposing multiple internal operations when the consumer only needs the business result.

Simple interfaces are easier to:

* understand;
* test;
* replace;
* reuse;
* connect to real infrastructure.

---

## 5. Separate Responsibilities

Keep responsibilities clear.

```text
UI
  ↓
Service
  ↓
API
  ↓
Application Logic
  ↓
Domain Logic
  ↓
Data Access
```

### UI

Responsible for:

* presentation;
* interaction;
* user feedback.

### Services

Responsible for:

* communicating with APIs or stubs;
* providing a consistent interface to the UI.

### Application Logic

Responsible for:

* coordinating business operations.

### Domain Logic

Responsible for:

* business rules;
* business calculations;
* invariants.

### Data Access

Responsible for:

* persistence;
* retrieval.

Do not place all logic in one layer.

---

## 6. Stub-First Development

During UI development, use realistic stubs.

```text
UI
  ↓
Service Interface
  ↓
Stub Implementation
```

Later:

```text
UI
  ↓
Same Service Interface
  ↓
API Implementation
```

The UI should not need to know whether the data came from:

* a stub;
* an API;
* a database.

This minimizes rework.

---

## 7. Error Handling Is a Product Feature

Every error is a business event.

Errors must not be treated as generic failures.

The system should distinguish between:

```text
Validation Error
Authentication Error
Authorization Error
Business Rule Error
Resource Not Found
Conflict
Infrastructure Failure
Unexpected Error
```

Each defined error should have a unique error code.

Example:

```text
INV-001
Insufficient available inventory
```

```text
ORD-003
Order cannot be fulfilled by the requested date
```

```text
AUTH-002
Session has expired
```

The error code should be stable even if the user-facing message changes.

---

## 8. Error Structure

Errors should have a consistent structure.

Conceptually:

```json
{
  "code": "INV-001",
  "message": "Insufficient available inventory",
  "details": {},
  "request_id": "..."
}
```

The exact implementation may evolve, but the following should be consistent:

* unique code;
* human-readable message;
* optional structured details;
* request or correlation identifier where appropriate.

---

## 9. Error Codes

Error codes should be:

* unique;
* stable;
* meaningful;
* documented;
* usable by both frontend and backend.

Codes should identify the source or category.

Examples:

```text
AUTH-xxx
USER-xxx
CUSTOMER-xxx
PRODUCT-xxx
INVENTORY-xxx
SUPPLIER-xxx
ORDER-xxx
MRP-xxx
ATP-xxx
SYSTEM-xxx
```

The frontend should use the error code to determine appropriate behavior.

For example:

```text
INV-001
    ↓
Show inventory explanation

AUTH-002
    ↓
Refresh session or request login

ORD-003
    ↓
Show fulfilment conflict
```

The frontend should not depend on parsing error-message text.

---

## 10. Handle Errors at the Correct Level

Errors should be handled where they can be meaningfully handled.

```text
Domain Error
    ↓
Application Error
    ↓
API Error Response
    ↓
User Experience
```

A known business error should not become:

```text
500 Internal Server Error
```

For example:

```text
Insufficient Material
```

is a valid business result and should be communicated as such.

It is not necessarily a system failure.

---

## 11. Never Hide Errors

Do not:

* silently ignore errors;
* return empty data when an operation failed;
* display misleading success messages;
* swallow exceptions;
* replace a meaningful error with a generic message.

If an operation fails, the user should understand:

* that it failed;
* why it failed;
* what they can do next, where possible.

---

## 12. Reuse Business Rules

Business rules must have a single authoritative implementation.

For example:

```text
Available Inventory
```

should not be calculated differently in:

* the frontend;
* the dashboard;
* the MRP engine;
* the order screen.

A business rule should have one authoritative definition.

---

## 13. Avoid Unnecessary Complexity

Do not introduce:

* microservices without a real need;
* abstractions without a clear purpose;
* excessive state management;
* duplicate business logic;
* unnecessary dependencies;
* premature optimization.

Prefer:

```text
Simple
    +
Clear
    +
Reusable
    +
Testable
```

over:

```text
Complex
    +
Abstract
    +
Difficult to Explain
```

---

## 14. UI Development Principles

The interface should be:

* simple;
* consistent;
* predictable;
* responsive;
* clear about system state.

Every important operation should communicate:

```text
Loading
    ↓
Success
    OR
Failure
```

The user should never be left wondering whether an operation is still running or whether it succeeded.

---

## 15. Test the Business, Not Just the Code

Testing should cover:

* business rules;
* calculations;
* permissions;
* error conditions;
* important workflows.

Especially test:

```text
Valid Input
Invalid Input
Missing Data
Insufficient Resources
Conflicting Operations
Unauthorized Access
Infrastructure Failure
```

Every important error code should have a known scenario that produces it.

---

## 16. Development Principle

The guiding principle for JDK development is:

> **Build simple interfaces on top of reusable, well-defined business capabilities, and make every failure understandable.**
