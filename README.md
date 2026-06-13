# MCP-Datenbankserver für KI-Agenten

Ein MCP-Server, der eine Datenbank über standardisierte **MCP-Tools** für KI-Agenten
bereitstellt. Mehrere Agenten können den Server als Werkzeug nutzen, um Daten abzufragen –
authentifiziert über **Keycloak**, autorisiert über **Scopes** auf Tool-Ebene und lückenlos
**auditiert** (wer hat wann welches Tool mit welchen Parametern aufgerufen).

Als Beispiel-Datensatz dient der bekannte **Titanic-Datensatz**; das erste Tool
(`get_survival_rate`) liefert Überlebensraten gruppiert nach Klasse oder Geschlecht. Das
Design ist von Anfang an datenbank-agnostisch (SQLite jetzt, PostgreSQL später) –
ausführliche Architektur- und Roadmap-Dokumentation unter [`docs/`](docs/index.md).

## Komponenten

Der Stack besteht aus drei Diensten, die über `docker-compose` orchestriert werden:

- **Keycloak** – Identity Provider (OAuth2/OIDC). Stellt Tokens für Agenten aus; der Realm
  wird beim Start aus [`keycloak/realm-export.json`](keycloak/realm-export.json) importiert.
- **MCP-Server** – FastMCP-Server über HTTP. Validiert die Tokens selbst, setzt Scopes pro
  Tool durch und protokolliert jeden Aufruf.
- **Client** – ein Beispiel-Agent, der per Client-Credentials-Flow ein Token holt und das
  Tool aufruft. Läuft auf Abruf, nicht dauerhaft.

## Repo-Struktur

```
.
├── server/              # MCP-Server (FastMCP)
│   ├── src/server/      # app.py, repository/, auth.py, audit.py
│   └── Dockerfile
├── client/              # Beispiel-Agent (Client-Credentials-Flow)
│   ├── main.py
│   └── Dockerfile
├── keycloak/            # Realm-Import (Realm, Client, Scopes)
├── data/                # Beispiel-Datenbank (Titanic, SQLite)
├── docs/                # Architektur & Roadmap (mkdocs-tauglich)
├── docker-compose.yml   # Orchestrierung aller Dienste
├── Makefile             # Entwickler-Kommandos (make help)
└── .env.example         # Vorlage für die lokale Konfiguration
```

## Voraussetzungen

- **Docker** (inkl. Docker Compose v2) – führt alle Dienste aus.
- **make** – für die Helfer-Kommandos (optional, sonst direkt `docker compose ...`).

> Für die Entwicklung am Code außerhalb der Container zusätzlich
> [**uv**](https://docs.astral.sh/uv/) und **Python 3.11**. Zum reinen Starten nicht nötig.

## Installation & Start

```bash
# 1. Konfiguration anlegen (Dev-Defaults, keine echten Secrets)
cp .env.example .env

# 2. Keycloak + MCP-Server im Hintergrund starten (baut die Images)
make up

# 3. Den Beispiel-Agenten einmal gegen den Server laufen lassen
make client
```

Der Client loggt das geholte Token (nur den Scope), die verfügbaren Tools und das Ergebnis
von `get_survival_rate`.

### Weitere Kommandos

`make` (ohne Argument) listet alle verfügbaren Kommandos:

- `make up` – Keycloak + MCP-Server im Hintergrund starten (mit Build)
- `make refresh` – kompletter Neustart inkl. Volumes (erzwingt Realm-Reimport)
- `make client` – den Beispiel-Agenten einmal ausführen

## Konfiguration

Alle geteilten Werte liegen zentral in der `.env` (Vorlage: `.env.example`). Die echte
`.env` ist git-ignoriert; im Repo stehen nur Platzhalter/Dev-Defaults, keine echten
Secrets. Fehlt eine benötigte Variable, bricht der Start mit einem klaren Fehler ab.
