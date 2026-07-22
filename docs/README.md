# JDK Documentation

## Reading Order

1. [01-product.md](01-product.md) — what JDK is, the product problem, and product philosophy
2. [02-business-model.md](02-business-model.md) — the business JDK operates within
3. [03-domain-model.md](03-domain-model.md) — entities, attributes, relationships, invariants
4. [04-application-model.md](04-application-model.md) — how the business is experienced in the app
5. [05-intelligence-model.md](05-intelligence-model.md) — MRP, ATP, feasibility, risk
6. [06-architecture.md](06-architecture.md) — technical architecture
7. [07-security-and-roles.md](07-security-and-roles.md) — authentication, authorization, roles
8. [08-development-guide.md](08-development-guide.md) — how to work on this codebase

## Feature Documentation

`features/` holds one document per operational area, added as each is built out:

* [authentication-and-users.md](features/authentication-and-users.md)
* [customers.md](features/customers.md)
* [products-and-formulas.md](features/products-and-formulas.md)
* `materials-and-inventory.md` *(planned)*
* [finished-goods.md](features/finished-goods.md)
* `suppliers.md` *(planned)*
* `customer-orders.md` *(planned)*
* `mrp-and-atp.md` *(planned)*
* `feasibility-and-risk.md` *(planned)*
* `reports-and-dashboard.md` *(planned)*

## Roadmap

`roadmap.md` — *(planned)*

## Principle

Documents 01–06 are the source of truth for what JDK is and how it is built. Code, screens, and API shapes should be traceable back to these documents. If something needed to build a feature isn't covered here, it belongs here before it belongs in code.
