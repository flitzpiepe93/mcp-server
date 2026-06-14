# Umsetzung: Keycloak & Scopes

Konkretisiert [Schritt 3 – Keycloak & Scopes](../roadmap/03-keycloak-scopes.md).

## Docker-Setup

Der Stack läuft über `docker-compose.yml`: **Keycloak**, der **MCP-Server** und ein
**Client** (für den Token-Flow). Alle drei kommunizieren über **Docker-Servicenamen**
(`keycloak:8080`, `mcp-server:8000`), damit Client und Server Keycloak unter **derselben**
URL sehen. Keycloak importiert beim Start einen versionierten Realm
(`keycloak/realm-export.json`).

Der Client ist ein kurzlebiges Skript (Token holen, Tool aufrufen, beenden), daher läuft
er nicht als Dauerdienst, sondern auf Abruf:

```bash
cp .env.example .env          # einmalig: lokale Konfiguration
docker compose up -d          # Keycloak + MCP-Server
docker compose run --rm client
```

## Authentifizierung

Der Server validiert eingehende Tokens selbst mit dem **`KeycloakAuthProvider`** von
FastMCP (POC ohne Gateway). Der Provider prüft Signatur (JWKS), **Issuer** und
**Audience** (`titanic-mcp`) – Letztere stellt sicher, dass nur Tokens akzeptiert werden,
die für *diesen* Server ausgestellt wurden, nicht für einen anderen Dienst im selben
Realm.

## Autorisierung (Scopes)

Die Scopes sind auf den Titanic-MCP namespaced:

- **`titanic:access`** – Basis-Scope, den jeder Agent tragen muss (global am Provider
  erzwungen). Verhindert, dass ein Tool ohne eigene Scope-Prüfung versehentlich offen ist.
- **`titanic:survival:read`** – Tool-Scope, pro Tool über `require_scopes(...)` erzwungen
  (`get_survival_rate`).

Der Agent authentifiziert sich per **Client-Credentials-Flow** (Service-Account
`example-agent`), passend zu einem Agenten ohne menschlichen Login.

## Konfiguration

Geteilte Werte (Service-Account-Secret, Admin-Credentials) liegen zentral in einer
**`.env`** (Vorlage: `.env.example`, committet; die echte `.env` ist git-ignoriert).
`docker-compose` löst daraus auf; es gibt **keine** hartkodierten Secrets im Repo und
keine stillen Default-Werte – fehlt eine Variable, bricht der Start mit einem Fehler ab.

## Offen / später

- **Audience-Granularität & weitere Clients**: Sobald mehrere Agenten/Clients existieren,
  sollten Audiences/Scopes pro Client geprüft werden.
- **`start-dev`** ist bewusst Entwicklungs-Modus (kein HTTPS-Zwang, In-Memory-DB). Im
  AWS-Zielentwurf übernimmt ohnehin Cognito + Gateway (siehe
  [Sicherheit & Zugriffskontrolle](../topics/security-access-control.md)).
