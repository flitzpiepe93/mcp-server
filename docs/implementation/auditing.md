# Implementation: Auditing

Concretizes [Step 4 – Auditing Layer](../roadmap/04-auditing.md).

Auditing is implemented as **FastMCP middleware** (`AuditMiddleware`) that wraps
every tool call (`on_call_tool`). This keeps the tool logic free of logging code,
and every future tool function is captured automatically.

## What gets logged

One line per call with:

- **Agent**: the identity from the validated Keycloak token — in the client credentials flow
  the `client_id` (via `get_access_token()`).
- **Tool**: the tool name that was called.
- **Args**: the query parameters.
- **Duration**: the execution time in milliseconds.

If the call fails, the middleware writes a `tool_error` line with the error message
instead and re-raises the exception (the audit does not swallow errors).

The **result content and size** are deliberately **not** logged: the audit trail
records *who requested what*, not *what came back*.

There is an honest limit here worth naming: the query parameters themselves can be
sensitive. A filter value — say a customer ID passed to narrow a query — reveals
*which* record was of interest, even though the result stays out of the log. For
the PoC this is acceptable, since the parameters are what make the audit trail
useful in the first place. In production the answer is per-argument handling:
mask or hash the values that identify a subject while keeping the ones needed for
accountability.

## Where it logs to

The audit writes **server-side** through the FastMCP logger to the terminal (stdout).
This matches the PoC requirement (simple terminal logging); the AWS target design
later routes the same trail into an isolated account.
