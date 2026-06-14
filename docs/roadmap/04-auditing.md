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

Siehe auch [Nachvollziehbarkeit & Compliance](../topics/audit-compliance.md). Wie dieser
Schritt konkret umgesetzt wurde, steht unter [Umsetzung: Auditing](../implementation/auditing.md).
