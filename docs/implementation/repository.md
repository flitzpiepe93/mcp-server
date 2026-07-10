# Implementation: Repository & first tool

Concretizes [Step 2 – Repository Pattern](../roadmap/02-repository-pattern.md).

## Interface and schema

- **`TitanicRepository`** (`Protocol`): the domain-level interface over the Titanic dataset.
  The server depends only on this protocol, never on a concrete database.
- **`SurvivalRate`** (Pydantic model): the result of a query. Per group it holds
  the fields `passenger_class`/`sex` (only the grouped field is set), `count` and
  `survival_rate` (0.0–1.0).
- **`dispose()`** is part of the interface so the server can tear down every
  implementation the same way (implementations without resources are a no-op).

## First read-only tool

`get_survival_rate(group_by)` returns the survival rate per group. `group_by` is
a `StrEnum` (`SurvivalGroupBy`) with the allowed values `passenger_class` and `sex`.
The enum type acts as the whitelist (no pass-through SQL) and lets FastMCP show the
agent the allowed values in the tool schema.

## Repository injection via the lifespan

The server is built through a factory, `build_server(build_repository)`. It takes
a **factory** rather than a ready-made repository, so the repository — and its
connection pool — are created **in the lifespan** at server startup and torn down
at shutdown (`dispose()`). Setup and teardown are therefore bound symmetrically to
the server lifecycle, and a test can inject a different implementation.

## Configuration

The database URL **must** be set via the environment variable
`TITANIC_DATABASE_URL` (no silent default); if it is missing, startup aborts with
an error. For example, to start locally against the example SQLite DB:

```bash
TITANIC_DATABASE_URL="sqlite:///$(pwd)/data/titanic.db" uv run server
```

## Testability

Because the server programs only against the `TitanicRepository` interface, tests
can inject a **`MemoryTitanicRepository`** — a lean test double that returns
predefined results instead of hitting a real database. `build_server(...)` passes
it into the server in place of the SQL implementation, so the tool path can be
tested deterministically and without infrastructure using the in-memory client.

## Why no separate domain layer

A common next instinct is to add a domain layer on top of the repository: have the
repository return raw observations and let Python compute the survival rate. I
chose not to. The only business logic here is a single aggregation
(`GROUP BY ... avg(survived)`), and that is exactly what a database does best —
pushing it into Python would throw away the database's strength and add a layer
with nothing genuinely DB-independent to test. `MemoryTitanicRepository` is
deliberately just a test double, not a second aggregation engine.

The point at which a domain layer *would* earn its place is when real
DB-independent logic appears — multi-step calculations, rules spanning several
entities, normalization. Building it before then would be speculative structure,
so it waits for that trigger.

## Deliberately not (yet) implemented

- **Connection pool tuning**: the SQLAlchemy default pool is in use; explicit parameters
  (`pool_size` etc.) will come with the PostgreSQL migration, once they are actually
  needed.
