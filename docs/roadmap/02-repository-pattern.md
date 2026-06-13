# Schritt 2 – Repository Pattern

## Ziel

Der Datenbankzugriff wird hinter ein **fachliches Repository-Interface** gezogen, sodass
die Datenbank später ausgetauscht werden kann, ohne den Code des MCP-Servers zu ändern.

## Warum

Das ist der zentrale Hebel für "SQLite jetzt, PostgreSQL später". Der MCP-Server kennt
nur das Interface, nicht die konkrete Datenbank.

Ein zweiter Vorteil ist die **Testbarkeit**: Weil der Server nur gegen das Interface
programmiert, kann man in Tests eine schlanke In-Memory-Implementierung (z.B.
`MemoryRepository`) injizieren, statt eine echte Datenbank hochzufahren. Tests werden
dadurch schneller, deterministisch und kommen ohne externe Infrastruktur aus.

## Designentscheidungen

- **Fachliches Interface, kein durchgereichtes SQL**: Das Repository bietet fachliche
  Methoden an (z.B. `get_customer_by_id`), nicht generische SQL-Ausführung. Sonst leaken
  DB-Details doch wieder in den MCP-Server.
- **Interface als `Protocol`/ABC**: Eine abstrakte Definition, gegen die der Server
  programmiert. Konkrete Implementierungen werden injiziert.
- **SQLAlchemy als Default-Implementierung**: SQLAlchemy Core/ORM deckt SQLite **und**
  PostgreSQL ab. Ein Wechsel zwischen beiden ist im Wesentlichen eine Frage der
  Connection-URL.

## Abgrenzung zu anderen Datenbanken

- **PostgreSQL**: über dieselbe SQLAlchemy-Implementierung abgedeckt.
- **DynamoDB**: *nicht* über SQLAlchemy abgedeckt – das wäre eine eigene
  Repository-Implementierung gegen dasselbe Interface. Das Pattern trägt das, ist aber
  bewusst eine separate Implementierung.

Siehe auch [Datenbankarchitektur](../topics/database-architecture.md).

## Umsetzung

Der hier umgesetzte Stand konkretisiert die obigen Prinzipien:

### Interface und Schema

- **`TitanicRepository`** (`Protocol`): das fachliche Interface über das Titanic-Dataset.
  Der Server hängt nur an diesem Protocol, nie an einer konkreten Datenbank.
- **`SurvivalRate`** (Pydantic-Model): das Ergebnis einer Abfrage – pro Gruppe die
  Felder `passenger_class`/`sex` (nur das gruppierte Feld ist gesetzt), `count` und
  `survival_rate` (0.0–1.0).
- **`dispose()`** ist Teil des Interface, damit der Server jede Implementierung
  einheitlich abbauen kann (Implementierungen ohne Ressourcen sind ein No-op).

### Erstes lesendes Tool

`get_survival_rate(group_by)` gibt die Überlebensrate je Gruppe zurück. `group_by` ist
ein `StrEnum` (`SurvivalGroupBy`) mit den erlaubten Werten `passenger_class` und `sex`.
Der Enum-Typ sorgt zugleich für die Whitelist (kein durchgereichtes SQL) und dafür, dass
FastMCP dem Agenten die erlaubten Werte im Tool-Schema anzeigt.

### Repository-Injektion über den Lifespan

Der Server wird über eine Factory `build_server(build_repository)` gebaut. Übergeben wird
eine **Factory** (kein fertiges Repository), damit das Repository – und sein
Connection-Pool – **im Lifespan** bei Server-Start erzeugt und beim Shutdown
(`dispose()`) wieder abgebaut wird. So sind Auf- und Abbau symmetrisch an den
Server-Lebenszyklus gebunden; zugleich kann ein Test eine andere Implementierung
injizieren.

### Konfiguration

Die Datenbank-URL ist **verpflichtend** über die Umgebungsvariable
`TITANIC_DATABASE_URL` zu setzen (kein stiller Default); fehlt sie, bricht der Start mit
einem Fehler ab. Lokaler Start gegen die Beispiel-SQLite-DB z.B.:

```bash
TITANIC_DATABASE_URL="sqlite:///$(pwd)/data/titanic.db" uv run server
```

### Bewusst (noch) nicht umgesetzt

- **`MemoryRepository`**: wird erst mit dem ersten Test eingeführt (gemeinsam mit seinem
  Nutzer), nicht auf Vorrat.
- **Connection-Pool-Tuning**: es läuft der SQLAlchemy-Default-Pool; explizite Parameter
  (`pool_size` etc.) kommen erst mit der PostgreSQL-Umstellung, wenn sie real gebraucht
  werden.
