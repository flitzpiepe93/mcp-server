# Step 4 – Auditing Layer

## Goal

A dedicated layer that records **which agent queried which data and when**,
as a foundation for auditability and compliance.

## Why last

Auditing comes last because it depends on two prerequisites from the previous
steps:

- A **read-only tool** that delivers real data from the [Repository](02-repository-pattern.md)
  ([Step 2](02-repository-pattern.md)). Before that there is nothing meaningful to
  log.
- An **agent identity** from [Keycloak](03-keycloak-scopes.md)
  ([Step 3](03-keycloak-scopes.md)). Audit logs are meaningful only when every
  request can be attributed to an external, reliable identity (claims from the token).

## Contents

- Per-request logging: agent identity, timestamp, invoked tool, and
  query parameters.
- Auditing as a dedicated layer (e.g. a decorator/middleware around the tool calls), so the
  tool logic itself stays lean.
- Persistence of the audit trail: in the **PoC** simply to the terminal (stdout). In the
  **AWS target design** the trail is written to a separate, isolated (confidential)
  account; for details see [Auditability & compliance](../topics/audit-compliance.md).

## Out of scope

- Authorization decisions themselves (who may do what) live in
  [Step 3](03-keycloak-scopes.md); this layer only logs.

See also [Auditability & compliance](../topics/audit-compliance.md). How this
step was concretely implemented is described under [Implementation: Auditing](../implementation/auditing.md).
