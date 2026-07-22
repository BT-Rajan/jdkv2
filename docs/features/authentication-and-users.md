# JDK — Authentication and Users

## Purpose

JDK uses **Perennia Auth** for authentication and **Perennia Access** for authorization.

JDK does not create its own authentication system.

```text
Perennia Auth
      ↓
Identity
      ↓
Perennia Access
      ↓
Roles & Permissions
      ↓
JDK
```

JDK provides the application-specific user-management interface required by JDK administrators.

---

## Authentication

Authentication is provided by Perennia Auth.

```text
User
  ↓
Perennia Auth
  ↓
Authenticated Identity
  ↓
JDK
```

JDK must use the public Perennia Auth interfaces for:

* login;
* token validation;
* session management;
* logout;
* user identity.

JDK must not maintain a separate password or authentication system.

---

## Authorization

Authorization is provided through Perennia Access.

```text
User
  ↓
Role
  ↓
Permissions
```

JDK consumes the access information provided by Perennia Access to determine what the authenticated user may do.

---

## JDK User Administration

JDK administrators require a user-management capability.

An authorized administrator should be able to:

```text
Search
   ↓
View
   ↓
Create
   ↓
Update
   ↓
Change Access
   ↓
Deactivate
```

The user-management interface should be available only to authorized administrators.

---

## User Administration Capabilities

### Search Users

Administrators should be able to search users using relevant attributes such as:

* name;
* email;
* phone number;
* user identifier;
* status;
* role.

Search should be server-side where appropriate.

---

### View User

An administrator may view:

* identity information;
* account status;
* assigned roles;
* relevant access information.

Sensitive authentication data must never be exposed.

---

### Create User

An authorized administrator may create or invite a user through the Perennia Auth process.

The JDK application must not directly create passwords or bypass Perennia Auth.

Conceptually:

```text
JDK Administrator
        ↓
Create / Invite User
        ↓
Perennia Auth
        ↓
User Identity
```

---

### Update User

An administrator may update permitted user information through the appropriate Perennia interfaces.

Changes must respect the ownership boundary:

```text
Identity Information
        ↓
Perennia Auth

Access Information
        ↓
Perennia Access

JDK Business Information
        ↓
JDK
```

---

## Promote and Demote Users

Administrators may change a user's role or access level where authorized.

```text
User
  ↓
Current Role
  ↓
Promote / Demote
  ↓
New Role
```

For example:

```text
Operator
    ↓
Supervisor
    ↓
Manager
```

or:

```text
Manager
    ↓
Supervisor
    ↓
Operator
```

A role change is an authorization operation and must be performed through the Perennia Access model.

JDK should not maintain a separate local role hierarchy.

---

## Access Changes

The administrator may:

* assign a role;
* remove a role;
* change a user's access level;
* suspend or deactivate access where supported;
* restore access where supported.

All access changes must be authorized.

```text
Administrator
      ↓
Permission Check
      ↓
Perennia Access
      ↓
Access Change
```

---

## Delete and Deactivate

User deletion must follow the capabilities and policies of Perennia Auth.

Where permanent deletion is not appropriate, the preferred operation may be:

```text
Active User
     ↓
Deactivated User
```

A deactivated user must not be able to access JDK.

The application must not retain an independent active-user state that contradicts Perennia Auth.

---

## Administrator Protection

Administrative operations must be protected by appropriate permissions.

```text
User
  ↓
Authenticated
  ↓
Administrator Permission
  ↓
User Management
```

The following operations are particularly sensitive:

* creating users;
* deleting or deactivating users;
* assigning roles;
* removing roles;
* promoting users;
* demoting users.

These operations should be auditable.

---

## Audit Trail

Administrative changes should record:

```text
Administrator
      ↓
Action
      ↓
Target User
      ↓
Previous State
      ↓
New State
      ↓
Timestamp
```

Example:

```text
Administrator A
promoted
User B
from Operator
to Supervisor
on [timestamp]
```

---

## Ownership Boundary

```text
┌─────────────────────────────┐
│       Perennia Auth         │
│                             │
│  Identity                   │
│  Authentication             │
│  Credentials                │
│  Sessions                   │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│      Perennia Access        │
│                             │
│  Roles                      │
│  Permissions                │
│  Access Decisions            │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│            JDK              │
│                             │
│  User Administration UI     │
│  JDK Business Data          │
│  JDK Business Permissions   │
│  Audit of JDK Actions       │
└─────────────────────────────┘
```

JDK provides the administrative experience.

Perennia Auth and Perennia Access remain the authoritative platforms for identity and access.

The key distinction is:

**JDK Admin = can manage users through the application.**
**Perennia Auth = owns the identity.**
**Perennia Access = owns roles and permissions.**

So the JDK admin can **search, view, create, update, promote, demote, deactivate, and potentially delete users**, but all actual identity/access operations should go through the Perennia platform APIs.
