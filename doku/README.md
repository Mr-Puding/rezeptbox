# RezeptBox – bewusst unsichere Demo-Webseite (SQL-Injection-Übung)

Eine kleine Rezept-Community in **Python / Flask / MySQL**. Die App ist
**absichtlich unsicher** programmiert, damit Mitschüler:innen im Unterricht
**SQL-Injection** praktisch ausprobieren können. In einer späteren Phase
wird die App abgesichert.

> ⚠️ **Nur lokal im Klassennetz betreiben – niemals ins öffentliche Internet stellen.**
> Die Lücken sind echt und ausnutzbar.

> 📄 Die vollständige Lückenliste und die Challenge-Lösungen werden **bewusst nicht**
> in diesem Repository veröffentlicht. Sie liegen nur lokal (siehe `CLAUDE.md`,
> Abschnitt „Lösungen bleiben lokal").

Thema und Oberfläche sind anders als beim Ticketsystem, die Schwachstellen
sind aber dieselben.

---

## 1. Schnellstart (ohne MySQL, läuft sofort)

Alle Server-Dateien liegen im Unterordner `server/`. Vom Projekt-Wurzelordner aus:

```bash
pip install Flask
cd server
set DB_BACKEND=sqlite        # Windows (cmd)
# export DB_BACKEND=sqlite   # macOS / Linux
python app.py
```

Empfohlen für die Schulung (im Netz erreichbar, Firewall automatisch):
`powershell -ExecutionPolicy Bypass -File .\server\start.ps1`

Dann im Browser öffnen: <http://localhost:8000>

Die Datei `rezepte.db` wird automatisch mit Tabellen und Beispieldaten angelegt.
Mit `set PORT=8001` lässt sich ein anderer Port wählen (z. B. um parallel zum
Ticketsystem zu laufen).

---

## 2. Start mit MySQL

Vom Projekt-Wurzelordner aus (`schema.sql` liegt in `doku/`):

```bash
mysql -u root -p < doku/schema.sql
cd server
pip install -r requirements.txt
set DB_BACKEND=mysql
set DB_HOST=127.0.0.1
set DB_USER=root
set DB_PASSWORD=deinPasswort
set DB_NAME=rezeptbox
python app.py
```

---

## 3. Test-Accounts, SQL-Cheat-Sheet & Fundorte der Lücken

> Aus Sicherheitsgründen **nicht** in diesem Repository. Test-Passwörter, das
> SQL-Injection-Cheat-Sheet und die Tabelle der Lücken-Fundorte stehen nur lokal
> in `doku/CHALLENGE-LOESUNGEN.md` (gitignored). Siehe `CLAUDE.md`,
> Abschnitt „Lösungen bleiben lokal".

---

## 4. Projektstruktur

```
rezeptbox/
├── CLAUDE.md            # Hinweise für Claude Code (Projekt-Wurzel)
├── server/             # NUR Betrieb – daraus wird der Server gestartet
│   ├── app.py          # Flask-App (enthält die bewussten Lücken)
│   ├── requirements.txt
│   ├── start.ps1       # Start im Netz (öffnet Firewall-Port 8000)
│   ├── stop.ps1        # Server beenden + Port schließen
│   ├── rezepte.db      # Laufzeit-DB (wird automatisch erzeugt, gitignored)
│   ├── static/
│   │   └── style.css
│   └── templates/
│       ├── login.html
│       ├── register.html
│       ├── dashboard.html
│       ├── rezept.html
│       └── new_rezept.html
└── doku/               # Doku + LÖSUNGEN – nicht im Server-Verzeichnis,
    ├── README.md       #   damit sie über die RCE-Lücken nicht einsehbar sind
    ├── schema.sql      # MySQL-Schema + Beispieldaten
    ├── CHALLENGES.md   # Aufgabenblatt (ohne Lösungen)
    ├── CHALLENGE-LOESUNGEN.md
    └── LUECKEN.md      # vollständige Lückenliste mit Lösungen
```
