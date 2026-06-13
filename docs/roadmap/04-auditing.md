# Schritt 4 – Auditing Layer

## Ziel

Eine eigene Schicht, die festhält, **welcher Agent wann welche Daten abgefragt hat** –
als Grundlage für Nachvollziehbarkeit und Compliance.

## Warum zuletzt

Auditing wird zuletzt angegangen, weil es zwei Voraussetzungen aus den vorherigen
Schritten braucht:

- Ein **lesendes Tool**, das echte Daten aus dem [Repository](02-repository-pattern.md)
  liefert ([Schritt 2](02-repository-pattern.md)) – vorher gibt es nichts Sinnvolles zu
  protokollieren.
- Eine **Agent-Identität** aus [Keycloak](03-keycloak-scopes.md)
  ([Schritt 3](03-keycloak-scopes.md)) – Audit-Logs sind erst aussagekräftig, wenn jede
  Anfrage einer externen, verlässlichen Identität (Claims aus dem Token) zugeordnet werden
  kann.

## Inhalt

- Protokollierung pro Anfrage: Agent-Identität, Zeitpunkt, aufgerufenes Tool und
  Abfrageparameter.
- Auditing als eigene Schicht (z.B. Decorator/Middleware um die Tool-Aufrufe), damit die
  Tool-Logik selbst schlank bleibt.
- Persistenz des Audit-Trails: im **POC** einfach ins Terminal (stdout). Im
  **AWS-Zielentwurf** wird der Trail in einen separaten, abgeschotteten (confidential)
  Account geschrieben – Details siehe [Nachvollziehbarkeit & Compliance](../topics/audit-compliance.md).

## Abgrenzung

- Setzt die über [Keycloak](03-keycloak-scopes.md) bereitgestellte Agent-Identität voraus.
- Berechtigungsentscheidungen selbst (wer darf was) liegen in
  [Schritt 3](03-keycloak-scopes.md); hier wird nur protokolliert.

Siehe auch [Nachvollziehbarkeit & Compliance](../topics/audit-compliance.md).

## Umsetzung

Das Auditing ist als **FastMCP-Middleware** (`AuditMiddleware`) umgesetzt, die sich um
jeden Tool-Aufruf legt (`on_call_tool`). Dadurch bleibt die Tool-Logik selbst frei von
Logging-Code, und jede künftige Tool-Funktion wird automatisch mit erfasst.

### Was protokolliert wird

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

### Wohin geloggt wird

Das Audit schreibt **server-seitig** über den FastMCP-Logger ins Terminal (stdout) – nicht
über den `Context`, denn dessen Log-Methoden senden Meldungen an den **aufrufenden
Client**. Audit-Einträge gehören jedoch ausschließlich auf die Server-Seite und nie zum
Agenten zurück. Das entspricht der POC-Vorgabe (einfaches Terminal-Logging); der
AWS-Zielentwurf leitet denselben Trail später in einen abgeschotteten Account um.
