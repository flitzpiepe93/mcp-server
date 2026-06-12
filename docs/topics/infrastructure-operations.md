# Infrastruktur & Betrieb

> **Frage:** Wie stellen wir sicher, dass der Server auch bei hoher Last verfügbar
> bleibt?

> **Hinweis:** Hochverfügbarkeit und der konkrete Deployment-Aufbau sind eine **spätere
> Ausbaustufe**. In den ersten Schritten läuft der Server lokal bzw. als einzelne
> Instanz. Hier wird nur der angestrebte Zielentwurf festgehalten.

## Voraussetzung im Design

Der Server wird von Anfang an so gestaltet, dass er später **horizontal skalierbar** ist:

- **Zustandsloser Server**: Der MCP-Server hält keinen Sitzungszustand lokal. Identität
  kommt pro Anfrage aus dem Token (Keycloak), sodass mehrere Instanzen parallel betrieben
  werden können.
- **Datenbank als getrennte, skalierbare Ressource**: Durch das
  [Repository Pattern](../roadmap/02-repository-pattern.md) ist die DB entkoppelt und kann
  unabhängig skaliert/ausgetauscht werden (z.B. PostgreSQL mit Connection-Pooling und
  Read-Replicas). Der Pool wird im Lifespan des Servers gehalten – Details siehe
  [Datenbankarchitektur](database-architecture.md#connection-pool--lifespan).

## Zielentwurf (spätere Ausbaustufe): containerbasiert auf AWS

Für den hochverfügbaren Betrieb ist ein **containerbasierter Ansatz** vorgesehen:

- MCP-Server als Container auf **ECS**.
- Ein **Load Balancer** davor, intern bereitgestellt über ein **API Gateway**.
- **Health-Checks** und **automatische Skalierung** sorgen für Hochverfügbarkeit.
- Die **ECS-Tasks** müssen über **mehrere Availability Zones (AZs)** verteilt laufen,
  damit der Ausfall einer AZ den Dienst nicht beeinträchtigt.
- Die **Datenbank** würde man hier höchstwahrscheinlich als **managed Service über RDS**
  betreiben (PostgreSQL) – statt die SQLite-Datei aus dem POC. RDS übernimmt Backups,
  Patching, Failover und Multi-AZ und passt zum zustandslosen, mehrinstanzigen Betrieb,
  für den eine lokale SQLite-Datei ohnehin nicht geeignet ist.
- **Authentifizierung** würde hier voraussichtlich über **Cognito** laufen, durchgesetzt
  bereits am **API Gateway** – der Server erhält nur authentifizierte Anfragen. Cognito
  übernimmt damit im AWS-Zielentwurf die IdP-Rolle, die im POC
  [Keycloak](../roadmap/03-keycloak-scopes.md) innehat. Die **Autorisierung** bleibt
  weiterhin im Server (Scope-/Claim-Mapping, Durchsetzung am
  [Repository](../roadmap/02-repository-pattern.md)).
- **Rate-Limits** wären langfristig ebenfalls denkbar, naheliegend am API Gateway.
- Der **Audit-Trail** wird in einen separaten, abgeschotteten (confidential) Account
  weitergeleitet und dort **append-only** abgelegt – getrennte Zugriffsrechte machen die
  Logs manipulationssicher. Im POC wird stattdessen nur ins Terminal geloggt. Siehe
  [Nachvollziehbarkeit & Compliance](audit-compliance.md#wohin-geloggt-wird--manipulationssicherheit).

> Dies skizziert nur, wie der Betrieb in der Praxis auf AWS aussehen könnte. Der POC wird
> **lokal** umgesetzt, nicht auf AWS.
