# JDK — Architecture

## 1. Architecture

JDK is a modular monolith consisting of:

```text
Vue 3 + TypeScript
        ↓
Service Interfaces
        ↓
FastAPI
        ↓
Domain & Intelligence Services
        ↓
MySQL
```

The application is designed for a small number of users with different responsibilities. The architecture should therefore prioritize:

* clarity;
* maintainability;
* security;
* explainability;
* ease of change.

Microservices are not required.

---

## 2. System Boundaries

```text
┌─────────────────────────────┐
│       Vue Application       │
│                             │
│  Application Shell          │
│  Business Experiences      │
│  Operational Features      │
│  State & UI                 │
└──────────────┬──────────────┘
               │
               │ Service Contracts / HTTP API
               ▼
┌─────────────────────────────┐
│       FastAPI Backend       │
│                             │
│  API Layer                 │
│       ↓                     │
│  Application Services      │
│       ↓                     │
│  Domain Services           │
│       ↓                     │
│  Intelligence              │
│       ↓                     │
│  Repositories              │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│           MySQL             │
└─────────────────────────────┘
```

---

## 3. Frontend Architecture

The frontend is organized around **business experiences and capabilities**, not database tables.

```text
frontend/
└── src/
    ├── app/
    │   ├── App.vue
    │   ├── router.ts
    │   └── application-shell/
    │
    ├── layouts/
    │   ├── AuthLayout.vue
    │   └── AppLayout.vue
    │
    ├── features/
    │   ├── calendar/
    │   ├── daily-status/
    │   ├── business-situations/
    │   ├── orders/
    │   ├── inventory/
    │   ├── products/
    │   ├── customers/
    │   ├── suppliers/
    │   └── mrp/
    │
    ├── services/
    │   ├── api/
    │   └── stubs/
    │
    ├── stores/
    │
    ├── components/
    │   ├── ui/
    │   └── business/
    │
    └── types/
```

The application shell provides:

* navigation;
* user identity;
* role-aware access;
* calendar or business timeline;
* global application context.

---

## 4. Application Experience

The primary application experience is:

```text
Login
  ↓
Application Shell
  ↓
Business Timeline / Calendar
  ↓
Daily Status
  ↓
Business Situation
  ↓
Drill-down
  ↓
Action
```

Operational capabilities remain available through the application shell.

The application should not force users to navigate through unrelated modules to understand the current business situation.

---

## 5. Frontend Service Boundary

The frontend communicates with business services through defined interfaces.

For example:

```text
Daily Status View
        ↓
Daily Status Service
        ↓
Service Interface
        ↓
Stub or API Implementation
```

The UI should not directly depend on:

* database structure;
* backend implementation;
* arbitrary HTTP calls inside components.

A feature should be able to use:

```text
Stub Service
```

during UI development and later:

```text
API Service
```

without requiring a redesign of the user experience.

---

## 6. Stub-First Development

During the UI-first phase:

```text
Vue
  ↓
Service Interface
  ↓
Stub Service
```

Example:

```text
DailyStatusService
        ↓
StubDailyStatusService
```

After the backend is available:

```text
DailyStatusService
        ↓
ApiDailyStatusService
        ↓
FastAPI
```

The stub should represent realistic business behavior and data.

Hardcoded business data should not be embedded directly into page components.

---

## 7. Backend Architecture

The backend is a modular monolith.

```text
backend/
└── app/
    ├── main.py
    │
    ├── api/
    │   ├── auth.py
    │   ├── customers.py
    │   ├── products.py
    │   ├── inventory.py
    │   ├── suppliers.py
    │   ├── orders.py
    │   ├── mrp.py
    │   └── daily_status.py
    │
    ├── domain/
    │   ├── customers/
    │   ├── products/
    │   ├── inventory/
    │   ├── suppliers/
    │   ├── orders/
    │   └── production/
    │
    ├── intelligence/
    │   ├── mrp.py
    │   ├── atp.py
    │   ├── feasibility.py
    │   └── risk.py
    │
    ├── repositories/
    │
    ├── models/
    │
    └── core/
        ├── config.py
        ├── security.py
        └── database.py
```

The backend owns:

* authentication;
* authorization;
* business rules;
* domain operations;
* MRP;
* ATP;
* feasibility;
* risk calculations;
* persistence.

---

## 8. Business Capability Boundaries

The main capabilities are:

```text
Authentication & Users
Customers
Products & Formulas
Materials & Inventory
Finished Goods
Suppliers
Customer Orders
MRP & ATP
Feasibility & Risk
Daily Status & Reports
```

These are logical boundaries within the modular monolith.

They do not need to become separate services.

---

## 9. Business Composition

The backend should compose business information where appropriate.

For example, the frontend should request:

```text
Daily Status
```

rather than separately requesting:

```text
Opening Stock
Production
Receipts
Consumption
Orders
Closing Stock
```

and attempting to assemble the business meaning itself.

The backend should produce the business result:

```text
Daily Status
    ↓
Opening State
    ↓
Expected Activity
    ↓
Actual Activity
    ↓
Variance
    ↓
Business Situation
```

The frontend presents the result.

---

## 10. Intelligence Boundary

The intelligence layer operates on domain data.

```text
Domain Data
    ↓
Domain Rules
    ↓
Intelligence Calculations
    ↓
Business Result
```

For example:

```text
Customer Order
    ↓
Product Requirement
    ↓
Material Requirement
    ↓
Availability Calculation
    ↓
Feasibility Result
```

The frontend must not reproduce these calculations.

---

## 11. API Boundary

The API is the boundary between the Vue application and the backend.

The API should expose business capabilities rather than database tables wherever practical.

Examples:

```text
GET  /daily-status/{date}
GET  /business-situations
GET  /orders
POST /orders
GET  /inventory
GET  /mrp/analysis
```

The API is responsible for:

* authentication;
* authorization;
* validation;
* business operations;
* calculated results;
* error responses.

The frontend is not a security boundary.

---

## 12. Data Layer

MySQL is the persistent system of record.

Repositories provide the boundary between application logic and database access.

```text
Application Service
        ↓
Repository
        ↓
MySQL
```

Business logic should not be scattered across:

* Vue components;
* API route handlers;
* SQL queries.

---

## 13. Security Boundary

Security is enforced by the backend.

The backend is responsible for:

* authentication;
* token validation;
* refresh tokens;
* logout and revocation;
* role checks;
* permission checks;
* protected operations.

The frontend may hide unavailable actions for usability, but authorization must always be enforced by the backend.

---

## 14. Architectural Principle

The system should maintain this separation:

```text
Presentation
    ↓
Frontend Services
    ↓
API
    ↓
Application Services
    ↓
Domain
    ↓
Intelligence
    ↓
Repositories
    ↓
Database
```

The architecture should remain simple enough to understand and strong enough to support the evolution of JDK from an MVP into a production-grade business operations platform.
