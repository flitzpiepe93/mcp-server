# MCP-Datenbankserver für KI-Agenten

Dieses Repository stellt einen MCP-Server bereit, der kontrollierten Datenbankzugriff für
KI-Agenten über standardisierte **MCP-Tools** ermöglicht. Agenten rufen fachliche Werkzeuge
auf, statt direkten Datenbankzugriff zu erhalten – jeder Zugriff ist authentifiziert,
autorisiert und protokolliert.

> **Hinweis:** Proof-of-Concept – zeigt das Zusammenspiel der Bausteine lokal (Docker,
> Keycloak, SQLite), nicht für den Produktiveinsatz gehärtet. Der angedachte AWS-Zielentwurf
> ist in [`docs/`](docs/index.md) beschrieben.

- **Authentifizierung** über Keycloak (OAuth2/OIDC); der Server validiert jedes Token.
- **Autorisierung** über Scopes auf Tool-Ebene – ein Agent ruft nur die Tools auf, für die
  er berechtigt ist.
- **Auditing** jedes Aufrufs: welcher Agent wann welches Tool mit welchen Parametern nutzt.
- **Klare Trennung von Logik und Datenbankzugriff** durch ein Repository-Interface – das
  Backend ist austauschbar (SQLite, PostgreSQL, sogar DynamoDB), ohne die Server-Logik zu ändern.

Als Beispiel dient der **Titanic-Datensatz**; das erste Tool (`get_survival_rate`) liefert
Überlebensraten gruppiert nach Klasse oder Geschlecht. Vollständige Architektur- und
Roadmap-Dokumentation unter [`docs/`](docs/index.md).

## Aufbau

Drei Dienste, über `docker-compose` orchestriert:

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

**Voraussetzungen:** Docker (inkl. Compose v2) und `make`. Für Code-Entwicklung außerhalb
der Container zusätzlich [uv](https://docs.astral.sh/uv/) und
[pre-commit](https://pre-commit.com/) (Hooks einmalig per `pre-commit install` aktivieren).

```bash
cp .env.example .env   # lokale Konfiguration (Dev-Defaults, keine echten Secrets)
make up                # Keycloak + MCP-Server im Hintergrund starten (mit Build)
make client            # Beispiel-Agent einmal gegen den Server laufen lassen
```

`make` (ohne Argument) listet alle Kommandos (u.a. `refresh` für einen kompletten
Neustart). Die echte `.env` ist git-ignoriert; fehlt eine benötigte Variable, bricht der
Start mit einem klaren Fehler ab.
