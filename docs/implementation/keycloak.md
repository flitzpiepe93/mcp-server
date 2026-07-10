# Implementation: Keycloak & scopes

Concretizes [Step 3 – Keycloak & Scopes](../roadmap/03-keycloak-scopes.md).

## Docker setup

The stack runs via `docker-compose.yml`: **Keycloak**, the **MCP server** and a
**client** (for the token flow). All three communicate through **Docker service names**
(`keycloak:8080`, `mcp-server:8000`), so client and server see Keycloak under the **same**
URL. Keycloak imports a versioned realm at startup
(`keycloak/realm-export.json`).

The client is a short-lived script (fetch token, call tool, exit), so it runs on
demand rather than as a permanent service:

```bash
cp .env.example .env          # one-time: local configuration
docker compose up -d          # Keycloak + MCP server
docker compose run --rm client
```

## Authentication

The server validates incoming tokens itself with FastMCP's **`KeycloakAuthProvider`**
(PoC without a gateway). The provider checks signature (JWKS), **issuer** and
**audience** (`titanic-mcp`). The audience check ensures the server accepts only
tokens issued for *this* server, not for another service in the same realm.

## Authorization (scopes)

The scopes are namespaced to the Titanic MCP:

- **`titanic:access`** — base scope that every agent must carry (enforced globally at the
  provider). It keeps a tool without its own scope check from being accidentally open.
- **`titanic:survival:read`** — tool scope, enforced per tool via `require_scopes(...)`
  (`get_survival_rate`).

The agent authenticates via the **client credentials flow** (service account
`example-agent`), which suits an agent that has no human login.

## Configuration

Shared values (service account secret, admin credentials) live centrally in a
**`.env`** (template: `.env.example`, committed; the real `.env` is git-ignored).
`docker-compose` resolves from it. There are **no** hardcoded secrets in the repo
and no silent defaults; if a variable is missing, startup aborts with an error.

## Open / later

- **Audience granularity & more clients**: once multiple agents/clients exist,
  audiences and scopes should be checked per client.
- **`start-dev`** is deliberately development mode (no HTTPS enforcement, in-memory DB). In the
  AWS target design, Cognito and the gateway take over (see
  [Security & access control](../topics/security-access-control.md)).
