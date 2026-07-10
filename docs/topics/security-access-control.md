# Security & access control

> **Question:** How do we ensure that agents can only access the data they are
> authorized for?

## Approach

Access control runs through **Keycloak (OAuth2/OIDC)**. Each agent authenticates and
receives a token with scopes/claims. The MCP server validates the token and uses it
to decide which tools the agent may call (tool level first, finer enforcement later).

## Layers

1. **Authentication**: Who is the agent? → A token from Keycloak, validated by the server.
   Identity arrives with [Keycloak (step 3)](../roadmap/03-keycloak-scopes.md);
   before that ([steps 1–2](../roadmap/01-fastmcp.md)) there is no identity.
2. **Authorization**: What may the agent do? → The token's scopes are enforced per tool via
   FastMCP's built-in `require_scopes(...)`; no dedicated mapping layer was needed.
3. **Enforcement**: The scopes initially govern only the **tool level** – which
   tools and actions an agent may call at all. Finer enforcement at the
   [Repository](../roadmap/02-repository-pattern.md) (e.g. filtering the permitted
   rows or columns) is a later expansion step.

## Where AuthN and AuthZ take place

Authentication and authorization are deliberately kept separate:

- **Authentication (AuthN) at the edge**: *Who are you?* This check belongs at the
  central entry point. In the AWS target design the **API Gateway** handles it, validating
  the token before a request reaches the server – see
  [Infrastructure & operations](infrastructure-operations.md). The **PoC** has no
  gateway, so the **server itself** validates the token.
- **Authorization (AuthZ) in the server**: *What may you do?* This decision **always**
  stays in the server, because only the server knows the tools and data. The gateway cannot
  know that a particular agent may not call a particular tool.

To keep the PoC → AWS transition from becoming a rewrite, the server always reads the identity
from the **verified claims in the request** – regardless of *who* validated them
(the server in the PoC, the gateway on AWS). The later switch then just drops the
local token validation; it does not rebuild the AuthZ logic.
