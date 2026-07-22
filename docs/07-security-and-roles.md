# JDK — Security and Roles

## 1. Security Objective

JDK contains business, customer, inventory, supplier, order, and operational data.

Security must ensure that:

* only authenticated users can access the application;
* users can perform only permitted actions;
* sensitive operations are protected;
* access is controlled by role and permission;
* security is enforced by the backend.

---

## 2. Authentication

The application requires authentication before access to protected functionality.

```text
User
  ↓
Login
  ↓
Access Token
  +
Refresh Token
  ↓
Authenticated Session
```

The system should support:

* login;
* access-token validation;
* token refresh;
* logout;
* token revocation where required.

Authentication is a backend responsibility.

---

## 3. Authorization

Authentication answers:

> **Who is the user?**

Authorization answers:

> **What is the user allowed to do?**

The backend must enforce authorization for:

* viewing data;
* creating records;
* modifying records;
* deleting records;
* executing business operations;
* accessing administrative functions.

Frontend visibility is not a security control.

---

## 4. Roles

A role represents a user's responsibility within the business.

The exact role set may evolve, but JDK should support role-based access.

Typical responsibilities may include:

```text
Administrator
    ↓
System Control

Executive
    ↓
Business Visibility & Decisions

Operations
    ↓
Operational Coordination

Production
    ↓
Production Activities

Procurement
    ↓
Supplier & Material Activities
```

Roles should be based on responsibility rather than merely on screen access.

---

## 5. Permissions

A permission represents an allowed capability.

Examples:

```text
View Orders
Create Orders
Edit Orders
Delete Orders

View Inventory
Adjust Inventory

View MRP
Execute MRP

Manage Users
Manage System
```

The authorization model should allow permissions to be associated with roles.

```text
User
  ↓
Role
  ↓
Permissions
```

---

## 6. Access Control

Access should be enforced at the backend.

```text
Request
  ↓
Authenticated?
  ↓
Authorized?
  ↓
Business Operation
```

If the user is not authorized:

```text
Request
  ↓
Access Denied
```

The frontend may improve usability by hiding actions the user cannot perform, but the backend must independently enforce the restriction.

---

## 7. Sensitive Operations

Some operations require particular protection.

Examples include:

* user administration;
* role and permission changes;
* inventory adjustments;
* deletion of important business records;
* changes to formulas;
* changes affecting fulfilment calculations.

Such operations should be restricted according to role and permission.

---

## 8. Data Protection

The system should protect:

* user credentials;
* authentication tokens;
* customer information;
* supplier information;
* business operations;
* inventory information.

Passwords must never be stored in plain text.

Sensitive credentials and secrets must not be committed to source control.

---

## 9. Auditability

Important business changes should be traceable.

Where appropriate, the system should record:

```text
Who
  ↓
Did What
  ↓
When
  ↓
To Which Record
```

Auditability is particularly important for:

* inventory changes;
* formula changes;
* user and permission changes;
* important order changes;
* administrative actions.

---

## 10. Security Principle

Security should follow this rule:

> **Trust is established by authentication. Access is granted by authorization. Business operations are protected by the backend.**

The security model should remain simple, explicit, and enforceable.
