# Auditability & compliance

> **Question:** How do we record which agent queried which data and when?

## Approach

A dedicated **Auditing Layer** ([step 4](../roadmap/04-auditing.md)) logs
every request. It requires an agent identity, which arrives with
[Keycloak (step 3)](../roadmap/03-keycloak-scopes.md) – before that
there is no identity.

## What is logged

- Agent identity (from the Keycloak claims; the `client_id` in the PoC)
- Timestamp and execution duration
- The tool called and its query parameters

The result content and scope are **not** logged: we record *who requested what*,
not *what came back*. For implementation details, see
[Implementation: Auditing](../implementation/auditing.md).

## Design decision

Auditing is a **dedicated layer** (e.g. a decorator or middleware around tool calls), so
the tool logic stays lean and logging happens centrally and consistently.

The order in the [Roadmap](../index.md) is deliberate: first the scaffolding and a
read tool, then identity and permissions with Keycloak (step 3), and finally
the audit (step 4). This way a concrete identity is available for every log entry
from the start.

## Where logging goes & tamper-resistance

Two things need to be distinguished: **integrity at write time** (the verified
identity guarantees that the logged agent is genuine – this holds) and
**tamper-resistance after writing** (can an entry be changed or deleted
later?).

- **PoC**: simple logging to the **terminal (stdout)**. Deliberately minimal – no
  persistence, no hardening.
- **AWS target design**: the audit trail is written to a **separate, isolated
  (confidential) account** and stored there **append-only**. Its real
  strength is the separation of access rights – even a compromised server account
  (or an insider with access to the payload data) then cannot alter the logs
  after the fact. See [Infrastructure & operations](infrastructure-operations.md).
