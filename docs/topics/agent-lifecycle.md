# Agent lifecycle management

> **Question:** How do we design the onboarding and offboarding process for agents, so that
> new agents gain access quickly and decommissioned agents are reliably blocked?

## Approach

**Keycloak** handles lifecycle management as the identity provider
([step 3](../roadmap/03-keycloak-scopes.md)).

- **Onboarding**: a new agent is created as a client/identity in Keycloak and given
  the appropriate scopes and roles. Access follows from the issued token –
  the MCP server itself needs no change.
- **Offboarding**: when an agent is decommissioned, it is deactivated in Keycloak or its
  tokens are invalidated. The MCP server validates tokens against Keycloak and thus
  reliably denies access.

## Benefit

Permissions and lifecycle are managed **centrally in Keycloak**, not scattered across the
MCP server. This keeps onboarding and offboarding fast and traceable, and
fits with [Security & access control](security-access-control.md).

## Emergency / incident response

The lifecycle is also where an emergency concept for **revoking access**
applies:

- **Immediate blocking (Kill Switch)**: if an agent is compromised or runs amok, it
  is deactivated in Keycloak or its tokens are revoked. How fast this takes effect depends on the
  **token lifetime**: with long-lived tokens the block takes effect only after a delay. Short
  token TTLs (or token introspection per request) shorten the window – a
  deliberate trade-off between response time and load.
- **Traceability during an incident**: for the follow-up, the
  [Audit Layer](../roadmap/04-auditing.md) applies – lifecycle (who was active when) and audit (what
  was queried) complement each other.
