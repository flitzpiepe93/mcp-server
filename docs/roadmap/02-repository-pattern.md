# Step 2 – Repository Pattern

## Goal

Database access sits behind a **domain-level repository interface**, so
the database can later be swapped out without touching the MCP server's code.

## Why

This is the key lever for "SQLite now, PostgreSQL later". The MCP server knows
only the interface, not the concrete database.

A second benefit is **testability**: because the server codes against the interface,
tests can inject a lightweight in-memory implementation (e.g.
`MemoryRepository`) instead of spinning up a real database. This keeps tests
fast, deterministic, and free of external infrastructure.

## Design decisions

- **Domain-level interface, no pass-through SQL**: The repository offers domain-level
  methods (e.g. `get_customer_by_id`) rather than generic SQL execution. Otherwise
  DB details would leak back into the MCP server.
- **Interface as `Protocol`/ABC**: An abstract definition that the server
  codes against. Concrete implementations are injected.
- **SQLAlchemy as the default implementation**: SQLAlchemy Core/ORM covers SQLite **and**
  PostgreSQL. Switching between the two is mostly a matter of the
  connection URL.

## Scope relative to other databases

- **PostgreSQL**: covered by the same SQLAlchemy implementation.
- **DynamoDB**: *not* covered by SQLAlchemy. That would be a separate
  repository implementation against the same interface. The pattern supports this, but
  deliberately as a separate implementation.

See also [Database architecture](../topics/database-architecture.md). How this step
was concretely implemented is described under [Implementation: Repository & first tool](../implementation/repository.md).
