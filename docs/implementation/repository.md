# Umsetzung: Repository & erstes Tool

Konkretisiert [Schritt 2 – Repository Pattern](../roadmap/02-repository-pattern.md).

## Interface und Schema

- **`TitanicRepository`** (`Protocol`): das fachliche Interface über das Titanic-Dataset.
  Der Server hängt nur an diesem Protocol, nie an einer konkreten Datenbank.
- **`SurvivalRate`** (Pydantic-Model): das Ergebnis einer Abfrage – pro Gruppe die
  Felder `passenger_class`/`sex` (nur das gruppierte Feld ist gesetzt), `count` und
  `survival_rate` (0.0–1.0).
- **`dispose()`** ist Teil des Interface, damit der Server jede Implementierung
  einheitlich abbauen kann (Implementierungen ohne Ressourcen sind ein No-op).

## Erstes lesendes Tool

`get_survival_rate(group_by)` gibt die Überlebensrate je Gruppe zurück. `group_by` ist
ein `StrEnum` (`SurvivalGroupBy`) mit den erlaubten Werten `passenger_class` und `sex`.
Der Enum-Typ sorgt zugleich für die Whitelist (kein durchgereichtes SQL) und dafür, dass
FastMCP dem Agenten die erlaubten Werte im Tool-Schema anzeigt.

## Repository-Injektion über den Lifespan

Der Server wird über eine Factory `build_server(build_repository)` gebaut. Übergeben wird
eine **Factory** (kein fertiges Repository), damit das Repository – und sein
Connection-Pool – **im Lifespan** bei Server-Start erzeugt und beim Shutdown
(`dispose()`) wieder abgebaut wird. So sind Auf- und Abbau symmetrisch an den
Server-Lebenszyklus gebunden; zugleich kann ein Test eine andere Implementierung
injizieren.

## Konfiguration

Die Datenbank-URL ist **verpflichtend** über die Umgebungsvariable
`TITANIC_DATABASE_URL` zu setzen (kein stiller Default); fehlt sie, bricht der Start mit
einem Fehler ab. Lokaler Start gegen die Beispiel-SQLite-DB z.B.:

```bash
TITANIC_DATABASE_URL="sqlite:///$(pwd)/data/titanic.db" uv run server
```

## Testbarkeit

Weil der Server nur gegen das `TitanicRepository`-Interface programmiert, lässt sich für
Tests ein **`MemoryTitanicRepository`** injizieren – ein schlankes Test-Double, das
vorgegebene Ergebnisse liefert, statt eine echte Datenbank zu nutzen. Über
`build_server(...)` wird es anstelle der SQL-Implementierung in den Server gegeben, sodass
der Tool-Pfad mit dem In-Memory-Client deterministisch und ohne Infrastruktur getestet
werden kann.

## Bewusst (noch) nicht umgesetzt

- **Connection-Pool-Tuning**: es läuft der SQLAlchemy-Default-Pool; explizite Parameter
  (`pool_size` etc.) kommen erst mit der PostgreSQL-Umstellung, wenn sie real gebraucht
  werden.
