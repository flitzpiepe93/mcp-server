# Sicherheit & Zugriffskontrolle

> **Frage:** Wie stellen wir sicher, dass Agents nur auf die Daten zugreifen können, für
> die sie berechtigt sind?

## Ansatz

Zugriffskontrolle über **Keycloak (OAuth2/OIDC)**. Jeder Agent authentifiziert sich und
erhält ein Token mit Scopes/Claims. Der MCP-Server validiert das Token und leitet daraus
ab, welche Tools der Agent aufrufen darf (Tool-Ebene zuerst; feinere Durchsetzung später).

## Schichten

1. **Authentifizierung**: Wer ist der Agent? → Token von Keycloak, validiert vom Server.
   Eine Identität wird mit [Keycloak (Schritt 3)](../roadmap/03-keycloak-scopes.md)
   eingeführt; davor ([Schritt 1–2](../roadmap/01-fastmcp.md)) existiert keine Identität.
2. **Autorisierung**: Was darf der Agent? → Scopes/Claims aus dem Token werden über eine
   **Mapping-Schicht** auf konkrete Berechtigungen übersetzt.
3. **Durchsetzung**: Die Scopes regeln zunächst nur die **Tool-Ebene** – also welche
   Tools/Aktionen ein Agent überhaupt aufrufen darf. Eine feinere Durchsetzung am
   [Repository](../roadmap/02-repository-pattern.md) (z.B. Filterung der erlaubten
   Zeilen/Spalten) ist ein späterer Ausbauschritt.

## Wo AuthN und AuthZ stattfinden

Authentifizierung und Autorisierung werden bewusst getrennt platziert:

- **Authentifizierung (AuthN) am Rand**: *Wer bist du?* Diese Prüfung gehört an den
  zentralen Eingangspunkt. Im AWS-Zielentwurf übernimmt das das **API Gateway** (validiert
  das Token, bevor eine Anfrage den Server erreicht) – siehe
  [Infrastruktur & Betrieb](infrastructure-operations.md). Im **POC** gibt es kein
  Gateway, daher übernimmt der **Server selbst** die Token-Validierung.
- **Autorisierung (AuthZ) im Server**: *Was darfst du?* Diese Entscheidung bleibt
  **immer** im Server, weil nur er die Tools und Daten kennt. Das Gateway kann nicht
  wissen, dass ein bestimmter Agent ein bestimmtes Tool nicht aufrufen darf.

Damit der Wechsel POC → AWS kein Umschreiben bedeutet, liest der Server die Identität
stets aus den **geprüften Claims im Request** – unabhängig davon, *wer* sie validiert hat
(Server im POC, Gateway auf AWS). Der spätere Umstieg ist dann nur das Weglassen der
lokalen Token-Validierung, kein Umbau der AuthZ-Logik.
