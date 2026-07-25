# JDK — Production Cycles

## Purpose

A production cycle defines how a single batch of ONE product is actually run on the floor.

```text
Product
    ↓
Production Cycle
    ↓
Batch Size, Timing, Labour, Machinery, Output
```

Different products run differently - a production cycle is therefore per-product, not a single
factory-wide setting.

---

## Relationship to Formula

The formula (see `products-and-formulas.md`) defines material *composition* - how much of each
material goes into one unit of product. The production cycle defines how a *batch* of that
product is run.

Raw material requirements per batch are derived, not re-entered:

```text
Formula Quantity Per Unit
        ×
Production Cycle Batch Size
        =
Raw Material Required Per Batch
```

This keeps material composition in one place (the formula) so the two can never drift out of
sync.

---

## Production Cycle Fields

```text
Batch Size
Time Per Batch
Finished Products Per Batch
Output Per Batch
Manpower Required
Machinery Required
Special Requirements
```

`Finished Products Per Batch` is the count of discrete finished units (e.g. bags) a batch yields.
`Output Per Batch` is the total output quantity produced (e.g. kg) - the two may differ when a
unit's size varies from the default.

`Special Requirements` captures anything atypical about running this product - curing time,
temperature control, allergen handling, and similar operational notes.

---

## Relationship to Production Schedule

A production cycle is master/reference data - it describes how a batch is normally run. A
production schedule (see `backend/sql/schema.sql: production_schedules`) is a dated instance of
production being planned or executed, and may reference the cycle's manpower/timing as a
starting point.

```text
Production Cycle (template)
        ↓
Production Schedule (dated instance)
```

---

## Access

Production cycle operations are controlled by the same permissions as products:

```text
product_view    — read a product's production cycle
product_manage  — create/update a product's production cycle
```

---

## Error Handling

```text
not_found — the product, or its production cycle, does not exist
```

A product with no production cycle yet is a normal state, not an error condition, in the UI -
the frontend shows an empty form rather than surfacing the 404 to the user.
