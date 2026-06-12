# MCP Server – Architektur & Roadmap

Dieser MCP-Server stellt eine Datenbank über standardisierte MCP-Tools für KI-Agenten
bereit. Verschiedene Agents nutzen den Server als Tool. Die Daten kommen testweise aus
einer SQLite-Datenbank; das Design ist von Anfang an so angelegt, dass später ohne
Änderung der MCP-Server-Logik andere Datenbanksysteme (z.B. PostgreSQL) genutzt werden
können.

## Leitprinzipien

- **Austauschbare Datenbank**: Der MCP-Server kennt keine konkrete Datenbank, nur ein
  fachliches Repository-Interface. SQLite heute, PostgreSQL morgen – ohne Tool-Code zu
  ändern.
- **Inkrementeller Aufbau**: Jede Schicht baut auf der vorherigen auf, ohne sie
  umzuschreiben. Schritt 1 ist bewusst nur Client + Server über HTTP; die Identität kommt
  mit Keycloak (Schritt 3) und steht damit dem Auditing (Schritt 4) bereits zur Verfügung.
- **Nachvollziehbarkeit**: Datenabfragen werden mit Agent-Identität (sobald über Keycloak
  verfügbar), Zeitpunkt, aufgerufenem Tool und Abfrageparametern protokolliert.
- **Standardkonforme Sicherheit**: Zugriffskontrolle über OAuth2/OIDC (Keycloak), zunächst
  auf Tool-Ebene (welche Tools ein Agent aufrufen darf); feinere Durchsetzung später.

## Roadmap (4 Schritte)

Die Reihenfolge ist bewusst gewählt: Jeder Schritt liefert für sich Mehrwert und legt
die Grundlage für den nächsten.

| Schritt | Thema | Ergebnis |
|--------|-------|----------|
| 1 | [FastMCP: Client + Server über HTTP](roadmap/01-fastmcp.md) | Lauffähige Grundstruktur: MCP-Client und -Server über HTTP |
| 2 | [Repository Pattern](roadmap/02-repository-pattern.md) | Datenbankzugriff hinter fachlichem Interface, DB austauschbar, erstes lesendes Tool |
| 3 | [Keycloak & Scopes](roadmap/03-keycloak-scopes.md) | OAuth2/OIDC-Zugriffskontrolle, Scopes zunächst auf Tool-Ebene, führt die Agent-Identität ein |
| 4 | [Auditing Layer](roadmap/04-auditing.md) | Protokollierung aller Anfragen pro Agent (nutzt die Keycloak-Identität) |

## Themenbereiche

Die fachlichen Fragestellungen hinter der Roadmap:

- [Sicherheit & Zugriffskontrolle](topics/security-access-control.md)
- [Nachvollziehbarkeit & Compliance](topics/audit-compliance.md)
- [Infrastruktur & Betrieb](topics/infrastructure-operations.md)
- [Datenbankarchitektur](topics/database-architecture.md)
- [Agent-Lifecycle-Management](topics/agent-lifecycle.md)

## Stack

- **Sprache**: Python
- **MCP-Framework**: FastMCP (offizielles Python-MCP-SDK)
- **DB-Abstraktion**: Repository Pattern, darunter SQLAlchemy (SQLite → PostgreSQL)
- **AuthN/AuthZ**: Keycloak (OAuth2/OIDC), Scopes zunächst auf Tool-Ebene
- **Doku**: Markdown unter `docs/`, später als Website über mkdocs publiziert
