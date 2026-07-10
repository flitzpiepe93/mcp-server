# Database architecture

> **Question:** How do we design database access so that we can later support different
> database systems (e.g. PostgreSQL, DynamoDB)?

## Approach: Repository Pattern

Database access sits behind a **domain-oriented repository interface**
([step 2](../roadmap/02-repository-pattern.md)). The MCP server knows only the
interface, not the concrete database.

## Properties

- **Domain-oriented interface instead of SQL**: methods like `get_customer_by_id`, with no
  SQL passed through. This keeps DB details from leaking into the server.
- **Interface as `Protocol`/ABC**: concrete implementations are injected.
- **Swapping via implementations**:
  - **SQLite** (PoC) and **PostgreSQL** (later): a shared
    SQLAlchemy implementation, switched essentially via the connection URL.
  - **DynamoDB**: a *dedicated* repository implementation against the same interface –
    not mappable via SQLAlchemy, but supported by the pattern.
  - **MemoryRepository** (tests): a lean in-memory implementation of the interface.
    It enables fast, deterministic tests without a real database or external
    infrastructure.

## Connection pool & lifespan

Under load, opening and closing a DB connection per request is expensive. A
**connection pool** keeps connections open and hands them out again. This is an
implementation detail of the SQLAlchemy variant (relevant for PostgreSQL, practically
a non-issue with SQLite as a local file) and lives entirely behind the repository interface –
the MCP server never sees it.

For now the **SQLAlchemy default pool** deliberately runs without explicit configuration. A pool
already exists, but tuning parameters (`pool_size`, `max_overflow`, …) come only
with the PostgreSQL switch, when they are actually needed – with
SQLite they serve no purpose and would even disrupt the local pool.

The pool is created and released in the **lifespan of the MCP server**: FastMCP provides
a lifespan hook that runs once at startup and cleans up at shutdown. There the
engine and pool are set up **once**, held for the entire server runtime, and
disposed cleanly at shutdown (`engine.dispose()`). The lifespan instantiates the
repository with this pool and injects it into the server.

This fits the stateless server described in
[Infrastructure & operations](infrastructure-operations.md): "stateless" means
no state *per request* – a resource held for the lifespan, like the pool,
is unaffected and even desirable.

## Where the pattern's limit shows

The repository interface is honest about swapping *implementations*, but it does
not pretend that every database is equally suited to every query. The current
tool is an aggregation (`GROUP BY ... avg(survived)`) — a natural fit for SQL. A
key-value store like DynamoDB has no `GROUP BY`, so the same tool would mean
either pre-aggregating the figures on write, maintaining a secondary structure,
or scanning and aggregating in the implementation. That is a data-modeling
decision, not a code-porting one.

So the pattern keeps the *server* independent of the database, but choosing a
fundamentally different store still requires rethinking how the data is shaped —
the interface contains that decision to one implementation rather than removing
it.

## Consequence

A database switch touches only the relevant repository implementation, never the
MCP server or tool code.
