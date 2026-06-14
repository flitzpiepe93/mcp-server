# Schritt 1 – Client + Server über HTTP

## Ziel

Eine lauffähige Grundstruktur aus **MCP-Client und MCP-Server** auf Basis von FastMCP,
die über **Streamable HTTP** kommuniziert. In diesem Schritt geht es ausschließlich um
das Grundgerüst: Client spricht Server, Server stellt MCP bereit.

## Warum HTTP von Anfang an

Das Ziel sind mehrere Remote-Agents über einen zentralen Server. Startet man direkt mit
Streamable HTTP, entfällt ein späterer Transport-Wechsel. FastMCP unterstützt HTTP
direkt; für lokale Tests läuft der Server einfach gegen `localhost`. Der Mehraufwand
gegenüber `stdio` ist minimal (Host/Port/Pfad statt Prozess-Pipe).

## Inhalt

- FastMCP-Server mit HTTP-Transport.
- MCP-Client, der sich gegen den Server verbindet.
- Grundstruktur des Projekts (wird vom Nutzer angelegt; die Implementierung orientiert
  sich daran).

## Abgrenzung

- **Keine Identität / keine Authentifizierung** in diesem Schritt – die Identität kommt
  mit [Keycloak (Schritt 3)](03-keycloak-scopes.md) und steht damit dem
  [Auditing (Schritt 4)](04-auditing.md) zur Verfügung.
- Noch keine Datenbankabstraktion (→ [Schritt 2](02-repository-pattern.md)).
- Noch keine lesenden Tools mit echten Daten – diese folgen mit dem
  [Repository](02-repository-pattern.md).
