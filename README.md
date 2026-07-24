# jdkv2

JDK is a manufacturing operations platform that connects business commitments with the operational resources required to fulfil them.

## Documentation

Start with [`docs/README.md`](docs/README.md) for the full documentation index.

Core reading order:

1. [Product](docs/01-product.md) — what JDK is and why
2. [Business Model](docs/02-business-model.md) — the business JDK operates
3. [Domain Model](docs/03-domain-model.md) — entities, attributes, invariants
4. [Application Model](docs/04-application-model.md) — how the app is experienced
5. [Intelligence Model](docs/05-intelligence-model.md) — MRP, ATP, feasibility, risk
6. [Architecture](docs/06-architecture.md) — how it's built

---

## Implementation

A rebuild of JDK's manufacturing operations tooling, built to the spec above,
reusing [`perennia-reference-app`](https://github.com/BT-Rajan/perennia-reference-app)'s
integration pattern for the shared Perennia platform packages:
**perennia-auth**, **perennia-access**, **perennia-search**, **perennia-notify**,
and **perennia-files**. None of those five packages are vendored, forked, or
reimplemented here - they are installed as dependencies (see
`backend/pyproject.toml`) and used only through their public APIs.

## Architecture

FastAPI backend + (planned) Vue 3/TypeScript frontend, per
`jdkv2/docs/06-architecture.md`. One shared MySQL database holds every
package's schema plus JDK's own business schema (`backend/sql/schema.sql`).

```
backend/app/
  core/           settings, DB connection, error catalog, and the one seam
                  (core/security.py) where perennia-auth/access/search/
                  notify/files are constructed and exposed as FastAPI deps
  permissions/    JDK's permission & role vocabulary, seeded into
                  perennia-access on startup
  domain/         one folder per business capability - repository (SQL),
                  service (orchestration), search_provider (where indexed)
  intelligence/   MRP/ATP engine, feasibility/risk engine, dashboard
  api/            FastAPI routers - thin, no business logic
  models/         pydantic request/response schemas
```

Every protected route depends on `get_current_identity` (perennia-auth) and,
where authorization matters, `require_permission(...)` (perennia-access) -
see `app/core/security.py`. No route implements its own token parsing or
role checks.

## What's implemented

| Capability | Status |
|---|---|
| Authentication & Users | Done - login/refresh/logout, admin search/create/update/promote/demote/deactivate, audit trail |
| Customers | Done - CRUD, search-indexed, order history |
| Materials & Inventory | Done - stock ledger, reorder config, low-stock alerts via perennia-notify to procurement-role users |
| Suppliers | Done - CRUD, search-indexed, material supply terms (price/lead time/MOQ) |
| Products & Formulas | Done - versioned formulas (never mutated in place), finished-goods ledger |
| Customer Orders | Done - CRUD, finished-goods availability check, status lifecycle, at-risk/delayed/cancelled notifications |
| MRP & ATP | Done - full requirement chain (orders → production requirement → formula → gross/net material requirement → supplier suggestion), traceability, ATP |
| Feasibility & Risk | Done - per-order and portfolio-wide risk classification built on ATP |
| Reports & Dashboard | Done - aggregated "what needs attention" view |
| File attachments | Done - generic entity-attachment linking (customers/suppliers/products/orders) via perennia-files |
| Production Scheduling | **Not started.** `production_schedules` table exists in the schema; no domain/service/API layer yet. |
| Finished Goods (dedicated spec) | **Partially covered.** A basic ledger lives inside the Products domain; `jdkv2/docs/features/finished-goods.md` was not read in detail, so batch/lot tracking, quality holds, or multi-warehouse requirements it may describe are not yet reflected. |
| Frontend | Done - Vue 3 + TypeScript + Pinia + Vue Router, covering every implemented backend domain. Type-checks and production-builds clean (`npm run build`). |

## Known gaps worth knowing about

- **No purchase-order tracking yet.** MRP's "suggested supplier" and
  estimated supply dates are *projections* (cheapest active supplier's
  quoted price/lead time), not commitments against a placed order. Every
  such value is flagged `is_projected: true` in API responses.
- **perennia-auth has no public "deactivate a user" API.** JDK's
  deactivation (`app/domain/users/service.py::deactivate`) is composed from
  revoke-all-sessions + strip-all-roles instead of reaching into
  perennia-auth's internals. If a real suspend/disable API is added
  upstream, switch to it directly.
- A synthetic **system identity** (`app/permissions/definitions.py::SYSTEM_IDENTITY`)
  is used for internal operations (search reindexing, system-triggered
  notifications) that aren't really "a user's action" even though they
  happen inside a request handler.

## Setup

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e .
cp ../.env.example ../.env   # then fill in AUTH_SIGNING_SECRET, FILES_SIGNING_SECRET, DB_*
python scripts/init_db.py                 # creates the DB, applies every schema, seeds permissions
python scripts/create_admin.py you@company.com "a-strong-password" "Your Name"
uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` for the interactive API reference.

```bash
cd frontend
npm install
cp .env.example .env   # VITE_API_BASE_URL must match the backend above
npm run dev            # http://localhost:5173
```

`npm run build` type-checks (`vue-tsc --noEmit`) before bundling, so a broken
type is a broken build, not a runtime surprise.

**Token handling, briefly:** the access token lives in memory only (never
written to storage); the refresh token is persisted in `localStorage` so a
page reload doesn't force a re-login. That second part is a deliberate,
documented trade-off (see `frontend/src/services/api.ts`) - the proper fix
is a backend change to issue the refresh token as an httpOnly cookie, which
this codebase does not yet do.
