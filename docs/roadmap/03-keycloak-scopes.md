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

## Scope-Durchsetzung

Keycloak liefert Scopes/Claims im Token; der Server setzt daraus durch, welche Tools ein
Agent aufrufen darf. Ursprünglich war hier eine selbst gebaute **Mapping-Schicht**
(Scope → Berechtigung) eingeplant – in der Umsetzung stellte sich heraus, dass **FastMCP
das mit `require_scopes` bereits eingebaut mitbringt**. Ein eigenes Mapping war damit
nicht nötig.

Der reale Aufwand lag stattdessen woanders: beim **Container-Networking/Issuer** (Client
und Server müssen Keycloak unter derselben URL sehen) und beim **Realm-Setup** (Scopes,
Audience, Service-Account).

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

## Umsetzung

### Docker-Setup

Der Stack läuft über `docker-compose.yml`: **Keycloak**, der **MCP-Server** und ein
**Client** (für den Token-Flow). Alle drei kommunizieren über **Docker-Servicenamen**
(`keycloak:8080`, `mcp-server:8000`), damit Client und Server Keycloak unter **derselben**
URL sehen – das hält den Token-Issuer konsistent, ohne `/etc/hosts`-Einträge oder
Netzwerk-Hacks. Keycloak importiert beim Start einen versionierten Realm
(`keycloak/realm-export.json`).

Der Client ist ein kurzlebiges Skript (Token holen, Tool aufrufen, beenden), daher läuft
er nicht als Dauerdienst, sondern auf Abruf:

```bash
cp .env.example .env          # einmalig: lokale Konfiguration
docker compose up -d          # Keycloak + MCP-Server
docker compose run --rm client
```

### Authentifizierung

Der Server validiert eingehende Tokens selbst mit dem **`KeycloakAuthProvider`** von
FastMCP (POC ohne Gateway). Der Provider prüft Signatur (JWKS), **Issuer** und
**Audience** (`titanic-mcp`) – Letztere stellt sicher, dass nur Tokens akzeptiert werden,
die für *diesen* Server ausgestellt wurden, nicht für einen anderen Dienst im selben
Realm.

### Autorisierung (Scopes)

Die Scopes sind auf den Titanic-MCP namespaced:

- **`titanic:access`** – Basis-Scope, den jeder Agent tragen muss (global am Provider
  erzwungen). Verhindert, dass ein Tool ohne eigene Scope-Prüfung versehentlich offen ist.
- **`titanic:survival:read`** – Tool-Scope, pro Tool über `require_scopes(...)` erzwungen
  (`get_survival_rate`).

Der Agent authentifiziert sich per **Client-Credentials-Flow** (Service-Account
`mcp-agent`), passend zu einem Agenten ohne menschlichen Login.

### Konfiguration

Geteilte Werte (Service-Account-Secret, Admin-Credentials) liegen zentral in einer
**`.env`** (Vorlage: `.env.example`, committet; die echte `.env` ist git-ignoriert).
`docker-compose` löst daraus auf; es gibt **keine** hartkodierten Secrets im Repo und
keine stillen Default-Werte – fehlt eine Variable, bricht der Start mit einem Fehler ab.

### Offen / später

- **Audience-Granularität & weitere Clients**: Sobald mehrere Agenten/Clients existieren,
  sollten Audiences/Scopes pro Client geprüft werden.
- **`start-dev`** ist bewusst Entwicklungs-Modus (kein HTTPS-Zwang, In-Memory-DB). Im
  AWS-Zielentwurf übernimmt ohnehin Cognito + Gateway (siehe
  [Sicherheit & Zugriffskontrolle](../topics/security-access-control.md)).
