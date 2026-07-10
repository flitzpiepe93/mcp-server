# Infrastructure & operations

> **Question:** How do we ensure that the server remains available even under high
> load?

> **Note:** High availability and the concrete deployment setup are a **later
> expansion stage**. In the first steps the server runs locally or as a single
> instance. Only the intended target design is recorded here.

## Prerequisite in the design

The server is designed from the start to scale **horizontally** later:

- **Stateless server**: the MCP server holds no session state locally. Identity
  comes per request from the token (Keycloak), so multiple instances can run
  in parallel.
- **Database as a separate, scalable resource**: the
  [Repository Pattern](../roadmap/02-repository-pattern.md) decouples the DB so it can be
  scaled or swapped independently (e.g. PostgreSQL with connection pooling and
  read replicas). The pool is held in the server's lifespan – for details, see
  [Database architecture](database-architecture.md#connection-pool-lifespan).

## Target design (later expansion stage): container-based on AWS

High-availability operation calls for a **container-based approach**:

- MCP server as a container on **ECS**.
- A **Load Balancer** in front, exposed internally through an **API Gateway**.
- **Health checks** and **automatic scaling** ensure high availability.
- The **ECS tasks** run distributed across **multiple Availability Zones (AZs)**,
  so the failure of one AZ does not affect the service.
- The **database** would most likely run as a **managed service via RDS**
  (PostgreSQL) – instead of the SQLite file from the PoC. RDS handles backups,
  patching, failover and multi-AZ, and fits stateless, multi-instance operation,
  which a local SQLite file is not suited to anyway.
- **Authentication** would presumably run via **Cognito**, enforced
  already at the **API Gateway** – the server receives only authenticated requests. Cognito
  thus takes on the IdP role in the AWS target design that
  [Keycloak](../roadmap/03-keycloak-scopes.md) plays in the PoC. **Authorization** stays
  in the server (scope/claim mapping, enforcement at the
  [Repository](../roadmap/02-repository-pattern.md)).
- **Rate limits** are also conceivable in the long term, again at the API Gateway.
- The **audit trail** is forwarded to a separate, isolated (confidential) account
  and stored there **append-only** – separate access rights make the
  logs tamper-proof. The PoC uses terminal logging instead. See
  [Auditability & compliance](audit-compliance.md#where-logging-goes-tamper-resistance).

> This only sketches how operation could look in practice on AWS. The PoC is
> implemented **locally**, not on AWS.
