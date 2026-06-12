# Schritt 3 – Keycloak & Scope-basierte Zugriffskontrolle

## Ziel

Zugriffskontrolle über **Keycloak (OAuth2/OIDC)**: Agents erhalten Tokens mit
Scopes/Claims, und der MCP-Server schränkt darüber ein, welche Tools ein Agent aufrufen
darf (Tool-Ebene zuerst; feinere Durchsetzung später).

## Warum Keycloak

Standardkonforme, etablierte Lösung für OAuth2/OIDC. MCP unterstützt OAuth-basierte
Authentifizierung offiziell. Keycloak übernimmt außerdem das
[Agent-Lifecycle-Management](../topics/agent-lifecycle.md) (Onboarding/Offboarding) als
Identity Provider.

## Der eigentliche Aufwand: das Mapping

Keycloak liefert Scopes/Claims im Token. Der Knackpunkt ist die **Mapping-Schicht**, die
diese auf konkrete Berechtigungen übersetzt. Die Keycloak-Anbindung selbst ist Standard;
das Mapping ist der Teil, der Sorgfalt braucht.

Zunächst greifen die Scopes nur auf **Tool-Ebene** – also welche Tools/Aktionen ein Agent
überhaupt aufrufen darf. Eine feinere Durchsetzung (welche Tabellen/Zeilen/Spalten ein
Agent sehen darf) ist ein späterer Ausbauschritt.

## Integration mit den vorherigen Schritten

- Führt erstmals eine **Agent-Identität** ein: echte Token-Validierung und Claims gegen
  Keycloak. Bis hierhin ([Schritt 1–2](01-fastmcp.md)) gibt es keine Identität.
- Legt damit die Grundlage für den nachfolgenden [Audit-Layer](04-auditing.md): erst mit
  dieser verlässlichen, externen Identität wird das Logging pro Agent sinnvoll.
- Setzt die Berechtigungen zunächst auf Tool-Ebene durch (welche Tools ein Agent aufrufen
  darf). Eine feinere Durchsetzung am [Repository](02-repository-pattern.md)
  (z.B. Row-Level-Filterung anhand der Scopes) ist ein späterer Ausbauschritt.

Siehe auch [Sicherheit & Zugriffskontrolle](../topics/security-access-control.md).
