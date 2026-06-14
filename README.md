# MCP-Datenbankserver für KI-Agenten

Dieses Repository stellt einen MCP-Server bereit, der kontrollierten Datenbankzugriff für
KI-Agenten über standardisierte **MCP-Tools** ermöglicht. Agenten rufen fachliche Werkzeuge
auf, statt direkten Datenbankzugriff zu erhalten – jeder Zugriff ist authentifiziert,
autorisiert und protokolliert.

Das Repository ist im Rahmen einer **Coding Challenge** entstanden und ist ein lokaler
**Proof-of-Concept**: Es zeigt das Zusammenspiel der Bausteine (Docker, Keycloak, SQLite),
ist aber nicht für den Produktiveinsatz gehärtet. Produktive Bereitstellung auf AWS und
Agent-Lifecycle sind bewusst nur konzeptionell ausgearbeitet (siehe [`docs/`](docs/index.md)).

Als Beispiel dient der **Titanic-Datensatz** (als SQLite-Datenbank). Er steht hier
stellvertretend für **sensible Daten** (z.B. Versichertendaten) – daraus ergibt sich
überhaupt erst der Bedarf an Authentifizierung, Zugriffskontrolle und Nachvollziehbarkeit.
Das erste Tool (`get_survival_rate`) liefert Überlebensraten gruppiert nach Klasse oder
Geschlecht.

- **Authentifizierung** über Keycloak (OAuth2/OIDC); der Server validiert jedes Token.
- **Autorisierung** über Scopes auf Tool-Ebene – ein Agent ruft nur die Tools auf, für die
  er berechtigt ist.
- **Auditing** jedes Aufrufs: welcher Agent wann welches Tool mit welchen Parametern nutzt.
- **Klare Trennung von Logik und Datenbankzugriff** durch ein Repository-Interface – das
  Backend ist austauschbar (SQLite, PostgreSQL, sogar DynamoDB), ohne die Server-Logik zu ändern.

## Aufbau

Über `docker-compose` orchestriert – zwei dauerhafte Dienste (Server, Keycloak) plus den
einmalig laufenden Beispiel-Client:

```
.
├── server/              # MCP-Server: validiert Tokens, setzt Scopes durch, auditiert
│   └── src/server/      # app.py, repository/, auth.py, audit.py
├── client/              # Beispiel-Agent: holt ein Token (Client-Credentials) und ruft das Tool
├── keycloak/            # Identity Provider; Realm-Import (Realm, Client, Scopes)
├── data/                # Beispiel-Datenbank (Titanic, SQLite)
├── docs/                # Architektur & Roadmap (mkdocs-tauglich)
├── docker-compose.yml   # Orchestrierung aller Dienste
├── Makefile             # Entwickler-Kommandos (make help)
└── .env.example         # Vorlage für die lokale Konfiguration
```

## Setup

**Voraussetzungen:** Docker (inkl. Compose v2) und `make`. Für das Generieren der
[Dokumentation](#dokumentation) sowie für Code-Entwicklung außerhalb der Container
zusätzlich [uv](https://docs.astral.sh/uv/) und [pre-commit](https://pre-commit.com/)
(Hooks einmalig per `pre-commit install` aktivieren).

```bash
cp .env.example .env   # lokale Konfiguration (Dev-Defaults, keine echten Secrets)
make up                # Keycloak + MCP-Server starten (mit Build); Logs laufen in der Konsole
make run-client        # Beispiel-Agent einmal gegen den Server laufen lassen
```

`make` (ohne Argument) listet alle Kommandos (u.a. `refresh` für einen kompletten
Neustart, `down` zum Stoppen). Die echte `.env` ist git-ignoriert; fehlt eine benötigte
Variable, bricht der Start mit einem klaren Fehler ab.

Der Client holt ein Token bei Keycloak, ruft das Tool auf und gibt das Ergebnis aus:

```text
Token received (scope='titanic:survival:read titanic:access')
Calling get_survival_rate(group_by='sex')
  sex='female' count=314 survival_rate=0.742
  sex='male'   count=577 survival_rate=0.189
```

Parallel protokolliert die Audit-Middleware des Servers jeden Aufruf – mit Agent, Tool
und Parametern:

```text
INFO  tool_call agent=example-agent tool=get_survival_rate args={'group_by': 'sex'} duration_ms=8.7
```

## Tests

Die Tests des Servers laufen über das `server/`-Paket – sie nutzen ein In-Memory-Repository
und brauchen weder Docker noch Keycloak:

```bash
cd server && uv run pytest
```

## Dienste & Ports

`make up` startet zwei Dienste, jeweils nur an `127.0.0.1` gebunden (nicht nach außen
exponiert):

| Dienst         | Adresse                 | Zweck                                      |
| -------------- | ----------------------- | ------------------------------------------ |
| **MCP-Server** | `http://127.0.0.1:8000` | MCP-Endpunkt (`/mcp/`), Health (`/health`) |
| **Keycloak**   | `http://127.0.0.1:8080` | Identity Provider (Token-Ausgabe, Realm)   |

Der Beispiel-Client läuft nicht dauerhaft, sondern nur einmalig über `make run-client`.

## Dokumentation

Die Architektur- und Roadmap-Doku unter [`docs/`](docs/index.md) wird mit
[mkdocs-material](https://squidfunk.github.io/mkdocs-material/) als Website generiert:

```bash
make docs-serve        # Doku lokal mit Live-Reload servieren
```

> **Achtung – Port-Konflikt:** mkdocs serviert standardmäßig ebenfalls auf Port **8000** –
> demselben Port wie der MCP-Server. Beide also **nicht gleichzeitig** starten, oder die Doku
> auf einem anderen Port servieren: `uv run --group docs mkdocs serve -a 127.0.0.1:8001`.
