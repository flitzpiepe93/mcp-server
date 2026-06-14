# Datenbankarchitektur

> **Frage:** Wie gestalten wir den Datenbankzugriff so, dass wir später unterschiedliche
> Datenbanksysteme (z.B. PostgreSQL, DynamoDB) unterstützen können?

## Ansatz: Repository Pattern

Der Datenbankzugriff liegt hinter einem **fachlichen Repository-Interface**
([Schritt 2](../roadmap/02-repository-pattern.md)). Der MCP-Server kennt nur das
Interface, nicht die konkrete Datenbank.

## Eigenschaften

- **Fachliches Interface statt SQL**: Methoden wie `get_customer_by_id`, kein
  durchgereichtes SQL. Verhindert, dass DB-Details in den Server leaken.
- **Interface als `Protocol`/ABC**: Konkrete Implementierungen werden injiziert.
- **Austausch über Implementierungen**:
  - **SQLite** (POC) und **PostgreSQL** (später): eine gemeinsame
    SQLAlchemy-Implementierung, Wechsel im Wesentlichen über die Connection-URL.
  - **DynamoDB**: eine *eigene* Repository-Implementierung gegen dasselbe Interface –
    nicht über SQLAlchemy abbildbar, aber vom Pattern getragen.
  - **MemoryRepository** (Tests): eine schlanke In-Memory-Implementierung des Interfaces.
    Erlaubt schnelle, deterministische Tests ohne echte Datenbank oder externe
    Infrastruktur.

## Connection-Pool & Lifespan

Unter Last ist das Öffnen/Schließen einer DB-Verbindung pro Anfrage teuer. Ein
**Connection-Pool** hält Verbindungen offen und verteilt sie wieder. Das ist ein
Implementierungsdetail der SQLAlchemy-Variante (für PostgreSQL relevant, bei SQLite als
lokaler Datei praktisch kein Thema) und lebt komplett hinter dem Repository-Interface –
der MCP-Server merkt nichts davon.

Aktuell läuft bewusst der **SQLAlchemy-Default-Pool** ohne explizite Konfiguration. Pool
existiert also bereits, aber Tuning-Parameter (`pool_size`, `max_overflow`, …) werden
erst mit der PostgreSQL-Umstellung eingeführt, wenn sie real gebraucht werden – bei
SQLite haben sie keinen Nutzen und würden den lokalen Pool sogar stören.

Erzeugt und freigegeben wird der Pool im **Lifespan des MCP-Servers**: FastMCP bietet
einen Lifespan-Hook, der beim Start einmalig läuft und beim Shutdown aufräumt. Dort wird
die Engine/der Pool **einmal** aufgesetzt, über die gesamte Server-Laufzeit gehalten und
beim Shutdown sauber disposed (`engine.dispose()`). Der Lifespan instanziiert das
Repository mit diesem Pool und injiziert es in den Server.

Das fügt sich mit dem zustandslosen Server aus
[Infrastruktur & Betrieb](infrastructure-operations.md) zusammen: "zustandslos" meint
keinen Zustand *pro Anfrage* – eine über den Lifespan gehaltene Ressource wie der Pool
ist davon unberührt und sogar erwünscht.

## Konsequenz

Ein Datenbankwechsel berührt nur die jeweilige Repository-Implementierung, nie den
MCP-Server- oder Tool-Code.
