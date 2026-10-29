# CLAUDE.md – RezeptBox

Hinweise für Claude Code zum Arbeiten an diesem Projekt.

## Was das ist
**RezeptBox** ist eine **absichtlich unsichere** Flask-Web-App (Rezept-Community)
für die Vorlesung **„Hacking mit Python"**. Mitschüler:innen sollen die
Schwachstellen praktisch finden und ausnutzen.

> ⚠️ **Die Lücken sind GEWOLLT. Niemals „aus Versehen absichern".**
> Wenn Code unsicher aussieht (String-Konkatenation in SQL, `|safe`, `os.popen`,
> `debug=True`), ist das Absicht. Nur absichern, wenn ausdrücklich danach gefragt wird.

## Sprache & Stil
- **Alles auf Deutsch**: Code-Kommentare, Docs, Commit-Messages, Antworten.
- Neue Lücken im Code mit dem bestehenden Muster markieren:
  ```python
  # ===================================================================
  # !!! BEWUSST UNSICHER !!!  <Typ> – <kurze Erklärung + Beispiel-Payload>
  # ===================================================================
  ```

## Projektstruktur (seit 2026-10-29 getrennt)
- `server/` – **nur Betriebsdateien** (`app.py`, `templates/`, `static/`,
  `requirements.txt`, `start.ps1`, `stop.ps1`, Laufzeit-`rezepte.db`). Der Server
  wird **aus diesem Ordner** gestartet; sein Arbeitsverzeichnis ist `server/`.
- `doku/` – **Doku + Lösungen** (`LUECKEN.md`, `CHALLENGE-LOESUNGEN.md`,
  `CHALLENGES.md`, `README.md`, `schema.sql`). Bewusst **außerhalb** von `server/`,
  damit die Lösungen über die RCE-Lücken (`/tools`, Debugger) nicht im
  Server-Arbeitsverzeichnis liegen und per `dir`/`type` sofort lesbar sind.
- `CLAUDE.md` bleibt im Projekt-Wurzelordner.

## Starten / Stoppen
- **Starten im Netz (empfohlen für die Schulung):** `server/start.ps1`
  ```powershell
  powershell -ExecutionPolicy Bypass -File .\server\start.ps1
  ```
  Öffnet automatisch die Windows-Firewall-Regel für TCP 8000 (ein UAC-„Ja"),
  startet den Server (SQLite) und **entfernt die Regel beim Beenden (Strg+C)
  wieder** (nochmal UAC-„Ja"). Der Server läuft dabei bewusst **ohne** Admin-Rechte;
  nur das Firewall-Kommando wird kurz elevated. Danach erreichbar im Klassen-WLAN
  unter `http://<WLAN-IP>:8000`.
- **Starten nur lokal (Zero-Setup, ohne Firewall):**
  ```bash
  cd server
  DB_BACKEND=sqlite python app.py
  ```
  Läuft auf `http://0.0.0.0:8000` mit `debug=True` (Auto-Reload an). Bindet zwar an
  alle Interfaces, ist aber ohne Firewall-Regel von außen meist nicht erreichbar.
  `DB_BACKEND` ist standardmäßig `mysql`; für MySQL siehe `doku/README.md`.
- **SQLite-DB** `rezepte.db` wird von `init_db()` automatisch angelegt (Seed-Daten).
  Löschen = kompletter Reset auf Startzustand.
- **Stoppen (Windows):** Der Flask-Debug-Reloader läuft als **zwei** Prozesse
  (Parent + Child) und startet sich sonst neu. Darum **alle** `app.py`-Python-Prozesse
  beenden, nicht nur einen – per PowerShell:
  ```powershell
  Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
    Where-Object { $_.CommandLine -like '*app.py*' } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
  ```
  Danach prüfen, dass Port 8000 frei ist (`Get-NetTCPConnection -LocalPort 8000`).

## Umgebung
- **Windows 11**, primäre Shell **PowerShell** (Bash-Tool vorhanden, eigene Syntax).
- `taskkill` ist im Bash-PATH nicht verfügbar → zum Prozessbeenden PowerShell nutzen.
- Server-IP im Klassen-WLAN zuletzt `141.87.60.197:8000` (WLAN-Adapter). Die anderen
  IPs (`192.168.56.1`, `172.17.*`, …) sind virtuelle Adapter von VirtualBox/Hyper-V.
  IP kann je Netz wechseln → aktuelle holen mit `Get-NetIPAddress -AddressFamily IPv4`.

## Wichtige Dateien
- `server/app.py` – alle Routen + DB-Anbindung (MySQL/SQLite umschaltbar).
- `server/templates/` – Jinja-Templates; XSS-Lücken entstehen durch `|safe` in der Ausgabe
  (die Speicherung selbst läuft über parametrisierte Queries).
- `doku/LUECKEN.md` – **vollständige Liste aller Lücken** mit Schritt-für-Schritt-Lösungen.
- `doku/CHALLENGES.md` – Aufgabenblatt für die Tester:innen (nur Aufgaben, **keine** Lösungen),
  jede Challenge mit Server-Adresse (IP:Port).
- `doku/README.md` – Setup (SQLite & MySQL), Test-Accounts, Cheat-Sheet.
- `server/rezepte.db` – Laufzeit-DB, **gitignored** (wird neu erzeugt).

## Beim Einbauen einer neuen Lücke IMMER mitpflegen
1. `server/app.py` (oder Template) ändern + `!!! BEWUSST UNSICHER !!!`-Kommentar.
2. `doku/LUECKEN.md`: Zeile in die Übersichtstabelle **und** einen Detail-Block
   (Ursache, Folge, „So nutzt man es aus"-Schritte) ergänzen.
3. `doku/CHALLENGES.md`: passende Challenge mit Adresse (`http://<IP>:8000/...`) ergänzen.
4. Changelog-Eintrag in `doku/LUECKEN.md` mit Datum.

## Test-Accounts
| Benutzer | Passwort        |
|----------|-----------------|
| admin    | __ENTFERNT__ |
| mia      | __ENTFERNT__       |
| ben      | __ENTFERNT__      |

## Fallstricke
- **XSS-Payloads bleiben in der DB.** Nach eigenen Tests angelegte Rezepte mit
  `<script>`/`onerror` wieder löschen – sonst feuern sie bei **jedem** Laden Popups.
  Beim Vorführen lieber sichtbare, stille Payloads wie `<b style=color:red>GEHACKT</b>`.
- **`/tools` ist seit 2026-10-29 SIMULIERT:** Die Command-Injection-Challenge führt
  **keinen** echten Befehl mehr aus (`_simuliere_shell()` in `app.py` täuscht die
  Ausgabe nur vor). Die Challenge bleibt lösbar, der Host ist aber geschützt. Wer die
  Lücke wieder „scharf" will, muss `os.popen(cmd)` bewusst zurückbauen.
- **Echte Gefahr lokal:** Der Werkzeug-Debugger (`debug=True`) führt weiterhin echten
  Code auf dem Host aus. Nur im Klassennetz, nie öffentlich.
- **Andere kommen nicht drauf, obwohl der Server läuft?** Meist gibt es Windows-Firewall-
  **Block**-Regeln für `python.exe` (entstehen, wenn der „Zugriff zulassen?"-Dialog
  weggeklickt wird). Block schlägt Allow, die Port-Regel aus `server/start.ps1` hilft dann nicht.
  Prüfen/abschalten in einer **Admin-PowerShell** (nicht cmd!):
  ```powershell
  Get-NetFirewallRule -Direction Inbound -Action Block |
    Where-Object { ($_ | Get-NetFirewallApplicationFilter).Program -match 'python' } |
    Disable-NetFirewallRule
  ```
  Zuletzt am 2026-10-29 deaktiviert. Hilft das nicht, blockiert evtl. das WLAN selbst
  (Client Isolation) → eigenen Hotspot nutzen.
- **Port nach der Session zu:** Der SessionEnd-Hook in `.claude/settings.local.json` ruft
  `server/stop.ps1` auf (Server beenden + Firewall-Regel entfernen, ggf. ein UAC-„Ja").
- `curl` führt **zwei** `-b`-Optionen nicht zusammen; für Cookie + Session gemeinsam
  einen kombinierten String nutzen (`-b "session=...; role=admin"`).

## Git
- Commit-Messages auf Deutsch, am Ende:
  `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`
- Noch kein Remote konfiguriert → nichts wird hochgeladen, bis bewusst ein
  `git remote` gesetzt wird. Push nur auf ausdrücklichen Wunsch.
