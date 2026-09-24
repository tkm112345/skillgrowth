---
name: schema-migration
description: Add a column to an existing SQLModel table in skillgrowth (app/models.py) without crashing self-hosted installs that already have that table on disk. Use whenever a change adds a field to an existing model — not needed for a brand-new table.
---

# Adding a column to an existing table

skillgrowth has no migration tool (no Alembic, nothing else).
`SQLModel.metadata.create_all()` (called from `app/db.py::init_db()`) only
creates *tables* that don't exist yet — it never alters a table that's
already on disk.

**A brand-new table needs nothing extra**: `create_all()` gives a fresh
install the full current schema for free.

**A new column on an existing model does need extra work**, or every
self-hosted instance that already has that table crashes the moment the
column is first written to — a fresh install is fine, an upgraded one is
not.

## What actually happened

This is not a hypothetical: `ExportSnapshot.edited_at` was added without
this step once. Fresh installs were fine, but any instance that had
already generated a resume crashed the next time it tried to, with
`no such column`. Full incident writeup:
`docs/ARCHITECTURE.md`, "Schema changes with no migration tool" section.

## The fix: `_ensure_column`

Add a matching call inside `app/db.py::init_db()`:

```python
def init_db() -> None:
    ...
    SQLModel.metadata.create_all(engine)
    _ensure_column(engine, "exportsnapshot", "edited_at", "TIMESTAMP")
    _ensure_column(engine, "selfpr", "is_selected", "BOOLEAN DEFAULT 0")
    _ensure_column(engine, "skill", "include_in_resume", "BOOLEAN DEFAULT 1")
    _ensure_column(engine, "settings", "skill_extraction_enabled", "BOOLEAN DEFAULT 0")
    _ensure_column(engine, "reflectionlog", "note", "TEXT DEFAULT ''")
    # add your new column here, same pattern
```

`_ensure_column(engine, table, column, ddl_type)`:
- Checks via `PRAGMA table_info(table)` whether the column already exists.
- Only runs `ALTER TABLE ... ADD COLUMN` if it's actually missing — a
  no-op on a fresh install, a real fix on an upgraded one.

Arguments:
- `table`: the SQLModel table name, lowercase (e.g. `"exportsnapshot"`,
  not `"ExportSnapshot"`).
- `column`: the new column's name, matching the model field.
- `ddl_type`: raw SQLite DDL type, e.g. `"TIMESTAMP"`, `"TEXT"`, or
  `"BOOLEAN DEFAULT 0"` / `"BOOLEAN DEFAULT 1"`.

If you give it a SQL `DEFAULT`, SQLite backfills that value onto every
existing row when the column is added — useful when the new column needs
a sensible value on rows that already exist (e.g. `include_in_resume`
defaulting to `1` so every skill someone already has keeps showing on
their resume, with no separate backfill step needed).

## Checklist

1. Add the field to the SQLModel class in `app/models.py`.
2. Add a matching `_ensure_column(...)` call in `app/db.py::init_db()`.
3. If the column needs a non-null value for existing rows, give it a SQL
   `DEFAULT` in `ddl_type` rather than writing a separate backfill.
4. Follow the project `CLAUDE.md`'s "Before committing" step 2: if the
   `app` container is running, rebuild it and smoke-test with `curl` —
   this exact bug class only shows up against a database that already
   has the table, which a fresh `pytest` run against an in-memory/fresh
   DB won't catch.
