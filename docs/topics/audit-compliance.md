# Nachvollziehbarkeit & Compliance

> **Frage:** Wie halten wir fest, welcher Agent wann welche Daten abgefragt hat?

## Ansatz

Ein eigener **Auditing Layer** ([Schritt 4](../roadmap/04-auditing.md)) protokolliert
jede Anfrage. Voraussetzung ist eine Agent-Identität, die mit
[Keycloak (Schritt 3)](../roadmap/03-keycloak-scopes.md) eingeführt wird – vorher
existiert keine Identität.

## Was wird protokolliert

- Agent-Identität (aus den Keycloak-Claims)
- Zeitpunkt
- Aufgerufenes Tool und Abfrageparameter

## Designentscheidung

Auditing ist eine **eigene Schicht** (z.B. Decorator/Middleware um Tool-Aufrufe), damit
die Tool-Logik schlank bleibt und das Logging zentral und konsistent erfolgt.

Die Reihenfolge in der [Roadmap](../index.md) ist bewusst: erst Grundgerüst und ein
lesendes Tool, dann mit Keycloak (Schritt 3) die Identität und Berechtigungen, und zuletzt
das Audit (Schritt 4). So steht jedem Log-Eintrag von Anfang an eine konkrete Identität
zur Verfügung.

## Wohin geloggt wird & Manipulationssicherheit

Zu unterscheiden sind zwei Dinge: die **Integrität beim Schreiben** (die geprüfte
Identität stellt sicher, dass der geloggte Agent echt ist – das ist gegeben) und die
**Manipulationssicherheit nach dem Schreiben** (kann ein Eintrag nachträglich geändert
oder gelöscht werden?).

- **POC**: einfaches Logging ins **Terminal (stdout)**. Bewusst minimal – keine
  Persistenz, keine Härtung.
- **AWS-Zielentwurf**: Der Audit-Trail wird in einen **separaten, abgeschotteten
  (confidential) Account** geschrieben und dort **append-only** abgelegt. Die eigentliche
  Stärke ist die Trennung der Zugriffsrechte – selbst ein kompromittierter Server-Account
  (oder ein Insider mit Rechten auf die Nutzdaten) kann die Logs dann nicht nachträglich
  verändern. Siehe [Infrastruktur & Betrieb](infrastructure-operations.md).
