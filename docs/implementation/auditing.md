# Umsetzung: Auditing

Konkretisiert [Schritt 4 – Auditing Layer](../roadmap/04-auditing.md).

Das Auditing ist als **FastMCP-Middleware** (`AuditMiddleware`) umgesetzt, die sich um
jeden Tool-Aufruf legt (`on_call_tool`). Dadurch bleibt die Tool-Logik selbst frei von
Logging-Code, und jede künftige Tool-Funktion wird automatisch mit erfasst.

## Was protokolliert wird

Pro Aufruf eine Zeile mit:

- **Agent**: die Identität aus dem geprüften Keycloak-Token – im Client-Credentials-Flow
  die `client_id` (via `get_access_token()`). Ohne Token (z.B. Tests) `anonymous`.
- **Tool**: der aufgerufene Tool-Name.
- **Args**: die Abfrageparameter.
- **Dauer**: die Ausführungszeit in Millisekunden.

Schlägt der Aufruf fehl, wird stattdessen eine `tool_error`-Zeile mit der Fehlermeldung
geschrieben und die Ausnahme weitergereicht (das Audit verschluckt keine Fehler).

Bewusst **nicht** protokolliert wird der **Ergebnis-Inhalt oder -Umfang** – der
Audit-Trail hält fest, *wer was angefragt* hat, nicht *was zurückkam*.

## Wohin geloggt wird

Das Audit schreibt **server-seitig** über den FastMCP-Logger ins Terminal (stdout).
Das entspricht der POC-Vorgabe (einfaches Terminal-Logging); der
AWS-Zielentwurf leitet denselben Trail später in einen abgeschotteten Account um.
