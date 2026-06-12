# Agent-Lifecycle-Management

> **Frage:** Wie gestalten wir den Onboarding- und Offboarding-Prozess für Agents, sodass
> neue Agents schnell Zugriff erhalten und abgekündigte Agents zuverlässig gesperrt
> werden?

## Ansatz

Das Lifecycle-Management übernimmt **Keycloak** als Identity Provider
([Schritt 3](../roadmap/03-keycloak-scopes.md)).

- **Onboarding**: Ein neuer Agent wird als Client/Identität in Keycloak angelegt und mit
  den passenden Scopes/Rollen versehen. Zugriff entsteht über das ausgestellte Token –
  der MCP-Server selbst muss dafür nicht geändert werden.
- **Offboarding**: Wird ein Agent abgekündigt, wird er in Keycloak deaktiviert bzw. seine
  Tokens werden ungültig. Der MCP-Server validiert Tokens gegen Keycloak und verweigert
  damit zuverlässig den Zugriff.

## Vorteil

Berechtigungen und Lebenszyklus werden **zentral in Keycloak** verwaltet, nicht im
MCP-Server verstreut. Das hält Onboarding/Offboarding schnell und nachvollziehbar und
fügt sich mit der [Sicherheit & Zugriffskontrolle](security-access-control.md) zusammen.

## Notfall / Incident Response

Der Lifecycle ist auch die Stelle, an der ein Notfallkonzept zum **Entzug von Zugriff**
ansetzt:

- **Sofort-Sperrung (Kill Switch)**: Ist ein Agent kompromittiert oder läuft er Amok, wird
  er in Keycloak deaktiviert bzw. seine Tokens werden widerrufen. Wirksamkeit hängt an der
  **Token-Lebensdauer**: Bei langlebigen Tokens greift die Sperrung erst verzögert. Kurze
  Token-TTLs (oder Token-Introspection pro Anfrage) verkürzen das Zeitfenster – eine
  bewusste Abwägung zwischen Reaktionszeit und Last.
- **Nachvollziehbarkeit im Incident**: Zur Aufarbeitung greift der
  [Audit-Layer](../roadmap/04-auditing.md) – Lifecycle (wer war wann aktiv) und Audit (was
  wurde abgefragt) ergänzen sich.
