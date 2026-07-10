# MCP Database Server for AI Agents

> **Proof of concept.** A time-boxed exploration of secure agent–data
> boundaries — designed to run locally, not a production service. Cloud
> deployment and agent lifecycle are designed in the
> [docs](https://flitzpiepe93.github.io/mcp-server/) but intentionally left
> unimplemented; the PoC's job is to prove the boundaries work end to end.

An MCP server that gives AI agents **controlled, audited access** to a database
through business-level tools instead of raw SQL. Every call is authenticated,
authorized against tool-level scopes, and logged — so you always know which
agent read what, and when.

The public **Titanic** dataset (SQLite) stands in for *sensitive data* (think
insurance records): that sensitivity is what motivates the authentication,
access control, and auditability. The one implemented tool, `get_survival_rate`,
returns survival figures grouped by passenger class or sex.

## Run it locally

**Requirements:** Docker (incl. Compose v2) and `make`.

```bash
cp .env.example .env   # local config (dev defaults, no real secrets)
make up                # start Keycloak + MCP server
make run-client        # run the example agent once against the server
```

The client fetches a token from Keycloak, calls the tool, and prints the result
— while the server's audit middleware logs every call with agent, tool, and
parameters. Run `make` with no argument to list every command.

## Repository layout

```
server/     MCP server: the tool, auth, audit middleware, and the
            repository layer that isolates it from the database
client/     Example agent that fetches a token and calls the tool once
keycloak/   Realm export (client, scopes, audience mapper) imported on startup
data/       Checked-in SQLite Titanic dataset, so the demo needs zero setup
docs/       Full design write-up, published to GitHub Pages via mkdocs
```

Inside `server/src/server/`, `app.py` wires everything together, `auth.py`
and `audit.py` cover authentication and the audit trail, and `repository/`
holds the swappable data-access layer (`sql.py` for real use, `memory.py`
for tests). Root-level files (`docker-compose.yml`, `Makefile`, `.env.example`)
orchestrate the local stack.

## Dataset

The Titanic dataset (891 passengers) comes from seaborn's built-in `titanic`
dataset (BSD-licensed). It is checked in as a small SQLite file
(`data/titanic.db`) so the demo runs with zero setup.

---

*Originally built as a time-boxed coding challenge, then reworked into this
portfolio piece.*
