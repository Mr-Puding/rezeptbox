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

## Starten / Stoppen
- **Starten (empfohlen, Zero-Setup):**
  ```bash
  DB_BACKEND=sqlite python app.py
  ```
  Läuft auf `http://0.0.0.0:5000` mit `debug=True` (Auto-Reload an).
  `DB_BACKEND` ist standardmäßig `mysql`; für MySQL siehe `README.md`.
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
  Danach prüfen, dass Port 5000 frei ist (`Get-NetTCPConnection -LocalPort 5000`).

## Umgebung
- **Windows 11**, primäre Shell **PowerShell** (Bash-Tool vorhanden, eigene Syntax).
- `taskkill` ist im Bash-PATH nicht verfügbar → zum Prozessbeenden PowerShell nutzen.
- Server-IP im Klassen-WLAN zuletzt `141.87.60.99:5000` (WLAN-Adapter). Die anderen
  IPs (`192.168.56.1`, `172.17.*`, …) sind virtuelle Adapter von VirtualBox/Hyper-V.
  IP kann je Netz wechseln → aktuelle holen mit `Get-NetIPAddress -AddressFamily IPv4`.

## Wichtige Dateien
- `app.py` – alle Routen + DB-Anbindung (MySQL/SQLite umschaltbar).
- `templates/` – Jinja-Templates; XSS-Lücken entstehen durch `|safe` in der Ausgabe
  (die Speicherung selbst läuft über parametrisierte Queries).
- `LUECKEN.md` – **vollständige Liste aller Lücken** mit Schritt-für-Schritt-Lösungen.
- `CHALLENGES.md` – Aufgabenblatt für die Tester:innen (nur Aufgaben, **keine** Lösungen),
  jede Challenge mit Server-Adresse (IP:Port).
- `README.md` – Setup (SQLite & MySQL), Test-Accounts, Cheat-Sheet.
- `rezepte.db` – Laufzeit-DB, **gitignored** (wird neu erzeugt).

## Beim Einbauen einer neuen Lücke IMMER mitpflegen
1. `app.py` (oder Template) ändern + `!!! BEWUSST UNSICHER !!!`-Kommentar.
2. `LUECKEN.md`: Zeile in die Übersichtstabelle **und** einen Detail-Block
   (Ursache, Folge, „So nutzt man es aus"-Schritte) ergänzen.
3. `CHALLENGES.md`: passende Challenge mit Adresse (`http://<IP>:5000/...`) ergänzen.
4. Changelog-Eintrag in `LUECKEN.md` mit Datum.

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
- **Echte Gefahr lokal:** Command Injection (`/tools`) und der Werkzeug-Debugger
  (`debug=True`) führen echten Code auf dem Host aus. Nur im Klassennetz, nie öffentlich.
- `curl` führt **zwei** `-b`-Optionen nicht zusammen; für Cookie + Session gemeinsam
  einen kombinierten String nutzen (`-b "session=...; role=admin"`).

## Git
- Commit-Messages auf Deutsch, am Ende:
  `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`
- Noch kein Remote konfiguriert → nichts wird hochgeladen, bis bewusst ein
  `git remote` gesetzt wird. Push nur auf ausdrücklichen Wunsch.
