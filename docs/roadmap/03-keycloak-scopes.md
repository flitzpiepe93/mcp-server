# Step 3 – Scope-based access control

## Goal

Access control via **Keycloak (OAuth2/OIDC)**: agents receive tokens with
scopes/claims, and the MCP server uses these to restrict which tools an agent
may call (tool level first, finer enforcement later).

## Why Keycloak

A standards-compliant, established solution for OAuth2/OIDC. MCP officially supports
OAuth-based authentication. As an identity provider, Keycloak also handles the
[agent lifecycle management](../topics/agent-lifecycle.md) (onboarding/offboarding).

## Scope enforcement

Keycloak delivers scopes/claims in the token, and the server uses these to enforce which tools an
agent may call. We originally planned a self-built **mapping layer**
(scope → permission), but during implementation it turned out that **FastMCP
provides this built in via `require_scopes`**. A custom mapping was therefore
unnecessary.

The real effort lay elsewhere: in **container networking/issuer** (the client
and server must see Keycloak under the same URL) and in the **realm setup** (scopes,
audience, service account).

Initially the scopes apply only at the **tool level**, meaning which tools/actions an agent
may call at all. Finer enforcement (which tables/rows/columns an
agent may see) is a later expansion step.

## Integration with the previous steps

- Introduces an **agent identity** for the first time: real token validation and claims against
  Keycloak. Up to this point ([Steps 1–2](01-fastmcp.md)) there is no identity.
- This lays the foundation for the [audit layer](04-auditing.md) that follows: per-agent logging becomes meaningful only with
  this reliable, external identity.
- Enforces permissions initially at the tool level (which tools an agent may call). Finer enforcement at the [Repository](02-repository-pattern.md)
  (e.g. row-level filtering based on the scopes) is a later expansion step.

See also [Security & access control](../topics/security-access-control.md). How
this step was concretely implemented is described under
[Implementation: Keycloak & Scopes](../implementation/keycloak.md).
