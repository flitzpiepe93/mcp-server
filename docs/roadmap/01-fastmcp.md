# Step 1 – Client + Server over HTTP

## Goal

A working baseline: an **MCP client and MCP server** built on FastMCP,
communicating over **Streamable HTTP**. This step covers only
the scaffolding: the client talks to the server, and the server exposes MCP.

## Why HTTP from the start

The target is multiple remote agents talking to a central server. Starting with
Streamable HTTP avoids a later transport switch. FastMCP supports HTTP
directly, and for local tests the server just runs against `localhost`. The extra effort
over `stdio` is minimal: host/port/path instead of a process pipe.

## Contents

- FastMCP server with HTTP transport.
- MCP client that connects to the server.
- Basic project structure (created by the user; the implementation builds
  on it).

## Out of scope

- **No identity, no authentication** in this step. Identity arrives
  with [Keycloak (Step 3)](03-keycloak-scopes.md) and then feeds into
  [Auditing (Step 4)](04-auditing.md).
- No database abstraction yet (→ [Step 2](02-repository-pattern.md)).
- No read tools with real data yet; those come with the
  [Repository](02-repository-pattern.md).
