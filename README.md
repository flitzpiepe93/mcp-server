# MCP Database Server for AI Agents

An MCP server that gives AI agents **controlled, audited access** to a database
through business-level tools instead of raw SQL. Every call is authenticated,
authorized against tool-level scopes, and logged — so you always know which
agent read what, and when.

The public **Titanic** dataset (SQLite) stands in for *sensitive data* (think
insurance records): that sensitivity is what motivates the authentication,
access control, and auditability. The one implemented tool, `get_survival_rate`,
returns survival figures grouped by passenger class or sex.

**Full design, architecture & engineering decisions: [flitzpiepe93.github.io/mcp-server](https://flitzpiepe93.github.io/mcp-server/)**

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

## Dataset

The Titanic dataset (891 passengers) comes from seaborn's built-in `titanic`
dataset (BSD-licensed). It is checked in as a small SQLite file
(`data/titanic.db`) so the demo runs with zero setup.

---

*Originally built as a time-boxed coding challenge, then reworked into this
portfolio piece.*
