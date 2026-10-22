# 🔓 Sicherheitslücken – RezeptBox

> **Lernprojekt für die Vorlesung „Hacking mit Python".**
> Diese App ist **absichtlich unsicher**. Diese Datei listet **alle** bewusst
> eingebauten Schwachstellen auf – jeweils mit einer **Schritt-für-Schritt-Anleitung,
> wie man die Lücke ausnutzt**. Jede neue Lücke wird hier ergänzt.
>
> ⚠️ **Nur lokal im Klassennetz betreiben – niemals ins öffentliche Internet stellen.**

In den Beispielen ist die App unter `http://localhost:8000` erreichbar.
„DevTools" = Entwicklerwerkzeuge des Browsers, zu öffnen mit **F12**.

---

## Test-Accounts

| Benutzername | Passwort        |
|--------------|-----------------|
| admin        | KuechenChef2024 |
| mia          | pommes123       |
| ben          | nudelsalat      |

---

## Übersicht

| #  | Lücke                       | Ort / Route              | Typ (OWASP)                  |
|----|-----------------------------|--------------------------|------------------------------|
| 1  | SQL-Injection Login         | `/login`                 | A03 Injection                |
| 2  | SQL-Injection Registrierung | `/register`              | A03 Injection                |
| 3  | UNION-SQLi Rezept-Detail    | `/rezept/<id>`           | A03 Injection                |
| 4  | Stored XSS                  | Rezept Titel/Inhalt      | A03 Injection (XSS)          |
| 5  | Reflected XSS               | `/dashboard?q=`          | A03 Injection (XSS)          |
| 6  | SQL-Injection Suchfeld      | `/dashboard?q=`          | A03 Injection                |
| 7  | OS Command Injection        | `/tools`                 | A03 Injection                |
| 8  | Broken Access Control Cookie| `/admin`                 | A01 Broken Access Control    |
| 9  | IDOR Bearbeiten             | `/rezept/<id>/edit`      | A01 Broken Access Control    |
| 10 | CSRF + Löschen per GET      | `/rezept/<id>/delete`    | A01 Broken Access Control    |
| 11 | Open Redirect               | `/login?next=`           | A01 Broken Access Control    |
| 12 | Klartext-Passwörter         | DB-Tabelle `users`       | A02 Cryptographic Failures   |
| 13 | Schwacher secret_key        | `app.py`                 | A02 Cryptographic Failures   |
| 14 | Debug-Modus / Debugger-RCE  | `app.run(debug=True)`    | A05 Security Misconfiguration|

---

## Details

### 1. SQL-Injection im Login
- **Route:** `/login`
- **Ursache:** Benutzername/Passwort werden direkt in die SQL-Query verkettet.
- **Folge:** Anmeldung ohne gültiges Passwort.
- **So nutzt man es aus:**
  1. Login-Seite öffnen: `http://localhost:8000/login`.
  2. Ins Feld **Benutzername** `admin' --` eintragen.
  3. Ins Feld **Passwort** irgendetwas eintragen (wird durch `--` auskommentiert).
  4. Auf **Anmelden** klicken → man ist als `admin` eingeloggt.
  5. Variante ohne Benutzer zu kennen: Benutzername `' OR '1'='1` eingeben.

### 2. SQL-Injection bei der Registrierung
- **Route:** `/register`
- **Ursache:** String-Verkettung im `INSERT`-Statement.
- **Folge:** Query-Manipulation; die Fehlermeldung verrät die DB-Struktur.
- **So nutzt man es aus:**
  1. Registrierungsseite öffnen: `http://localhost:8000/register`.
  2. Als **Benutzername** `hacker', 'pw'); --` eingeben.
  3. Passwort und Passwort-Wiederholung auf `pw` setzen.
  4. Absenden. Entweder wird ein zusätzlicher Benutzer angelegt, oder es
     erscheint eine SQL-Fehlermeldung, die man für weitere Angriffe nutzt.

### 3. UNION-basierte SQL-Injection im Rezept-Detail
- **Route:** `/rezept/<id>`
- **Ursache:** Die `id` wird ungeprüft in die Query eingesetzt (Abfrage hat 5 Spalten).
- **Folge:** Auslesen beliebiger Tabellen, z. B. Benutzernamen + Passwörter.
- **So nutzt man es aus:**
  1. Einloggen (z. B. mit Lücke #1).
  2. In die Adressleiste folgende URL eingeben:
     `http://localhost:8000/rezept/0 UNION SELECT 1,username,password,4,5 FROM users`
  3. Die Rezept-Seite zeigt statt eines Rezepts den **Benutzernamen als Titel**
     und das **Passwort als Inhalt** an.
  4. Tipp: `id=0` gibt es nicht, daher stammt die angezeigte Zeile komplett aus
     dem UNION-Teil. Spalte 2 = Titel, Spalte 3 = Inhalt.

### 4. Stored XSS (persistent)
- **Ort:** Rezept-Titel und -Inhalt (`/rezept/new`), Ausgabe mit `|safe`.
- **Folge:** Der eingeschleuste Code läuft bei **jedem**, der das Rezept oder das Dashboard öffnet.
- **So nutzt man es aus:**
  1. Einloggen und auf **+ Neues Rezept** klicken.
  2. In **Titel** oder **Inhalt** ein Skript eintragen, z. B.
     `<script>alert(document.cookie)</script>` oder `<img src=x onerror=alert(1)>`.
  3. **Speichern**.
  4. Das Rezept (oder schon das Dashboard) öffnen – der Code wird ausgeführt.
     Öffnet ein **anderer** Nutzer das Rezept, läuft der Code auch bei ihm.
  5. Tipp fürs Vorführen ohne nervige Popups: `<b style=color:red>GEHACKT</b>` nehmen.

### 5. Reflected XSS
- **Route:** `/dashboard?q=`
- **Ursache:** Der Suchbegriff wird ohne Escaping wieder ausgegeben (`|safe`).
- **Folge:** Code aus der URL wird im Browser des Opfers ausgeführt.
- **So nutzt man es aus:**
  1. Einloggen.
  2. In die Adressleiste eingeben:
     `http://localhost:8000/dashboard?q=<script>alert(42)</script>`
  3. Die Seite führt das Skript aus (Popup `42`).
  4. Für einen echten Angriff schickt man einem eingeloggten Opfer genau diesen Link.

### 6. SQL-Injection im Suchfeld
- **Route:** `/dashboard?q=`
- **Ursache:** `q` wird direkt in ein `LIKE '%...%'` verkettet.
- **Folge:** Man kann die Suche manipulieren oder ein UNION anhängen.
- **So nutzt man es aus:**
  1. Einloggen, Dashboard öffnen.
  2. Ins **Suchfeld** eingeben: `xxx%' OR '1'='1`
  3. Suchen → es werden **alle** Rezepte angezeigt, obwohl „xxx" nirgends vorkommt.
  4. Fortgeschritten: wie bei #3 ein `UNION SELECT ...` anhängen, um andere Tabellen auszulesen.

### 7. OS Command Injection
- **Route:** `/tools`
- **Ursache:** Die Eingabe wird direkt an die System-Shell (`os.popen`) übergeben.
- **Folge:** Ausführung beliebiger Betriebssystem-Befehle auf dem Server.
- **So nutzt man es aus:**
  1. Einloggen und oben auf **🔧 Tools** klicken.
  2. Ins Feld **Host / IP** nicht nur eine IP, sondern einen angehängten Befehl eingeben:
     - Windows: `127.0.0.1 & whoami`
     - Linux/Mac: `127.0.0.1; id`
  3. Auf **Ping** klicken.
  4. Unter der Ping-Ausgabe erscheint das Ergebnis des angehängten Befehls
     (z. B. der Benutzername des Servers).
  5. Weiter probieren: `& dir` (Windows) bzw. `; ls -la` (Linux) zum Dateien auflisten.

### 8. Broken Access Control über Client-Cookie
- **Route:** `/admin`
- **Ursache:** Die Rolle wird aus dem Cookie `role` gelesen, das der Client ändern kann.
- **Folge:** Zugriff auf alle Benutzer inkl. **Klartext-Passwörter**.
- **So nutzt man es aus:**
  1. Einloggen (als normaler Nutzer).
  2. DevTools öffnen (**F12**) → Reiter **Konsole**.
  3. Eingeben und Enter: `document.cookie = "role=admin"`
  4. `http://localhost:8000/admin` aufrufen.
  5. Die Admin-Seite listet alle Konten mit Klartext-Passwörtern.
  - Alternativ in den DevTools unter **Anwendung/Application → Cookies** das Cookie
    `role` manuell auf `admin` setzen.

### 9. IDOR beim Bearbeiten
- **Route:** `/rezept/<id>/edit`
- **Ursache:** Es wird nicht geprüft, ob das Rezept der angemeldeten Person gehört.
- **Folge:** Man kann fremde Rezepte überschreiben.
- **So nutzt man es aus:**
  1. Einloggen (egal mit welchem Konto).
  2. In die Adressleiste die ID eines **fremden** Rezepts eingeben, z. B.
     `http://localhost:8000/rezept/1/edit`.
  3. Titel/Inhalt ändern und **Speichern** – obwohl das Rezept jemand anderem gehört.

### 10. CSRF + Löschen per GET
- **Route:** `/rezept/<id>/delete`
- **Ursache:** Löschen passiert per einfachem GET-Aufruf, ohne Token und ohne Besitzprüfung.
- **Folge:** Fremde Rezepte löschen – ein Link oder ein eingebettetes Bild genügt.
- **So nutzt man es aus:**
  1. Einfach: eingeloggt die URL `http://localhost:8000/rezept/3/delete` aufrufen → Rezept #3 ist weg.
  2. Als echter CSRF-Angriff: auf einer **fremden** Webseite folgendes einbauen:
     ```html
     <img src="http://localhost:8000/rezept/3/delete">
     ```
  3. Öffnet ein eingeloggtes Opfer diese Seite, lädt der Browser das „Bild" –
     und löscht dabei Rezept #3, ohne dass das Opfer etwas tut.

### 11. Open Redirect
- **Route:** `/login?next=...`
- **Ursache:** Das Weiterleitungsziel nach dem Login wird nicht geprüft.
- **Folge:** Phishing – ein Link der echten Seite leitet nach Login auf eine fremde Seite.
- **So nutzt man es aus:**
  1. Opfer bekommt einen vertrauenswürdig aussehenden Link:
     `http://localhost:8000/login?next=https://example.com`
  2. Opfer loggt sich auf der **echten** RezeptBox ein.
  3. Direkt nach dem Login wird es auf `https://example.com` weitergeleitet
     (dort könnte eine nachgebaute Login-Seite stehen, die das Passwort abfängt).

### 12. Passwörter im Klartext
- **Ort:** DB-Tabelle `users`.
- **Folge:** Sobald man an die DB kommt (via SQLi #3 oder `/admin` #8), sind alle Passwörter sofort lesbar.
- **So nutzt man es aus:**
  1. Lücke #3 oder #8 ausnutzen.
  2. Die Passwörter stehen direkt im Klartext da – kein Knacken eines Hashes nötig.

### 13. Schwacher, hartkodierter secret_key
- **Ort:** `app.py` → `app.secret_key = "schulung-nicht-geheim"`.
- **Folge:** Session-Cookies lassen sich selbst erzeugen → man kann sich als beliebiger Nutzer ausgeben.
- **So nutzt man es aus:**
  1. Den (im Quellcode sichtbaren) Schlüssel `schulung-nicht-geheim` notieren.
  2. Werkzeug `flask-unsign` installieren: `pip install flask-unsign`.
  3. Ein eigenes gültiges Session-Cookie bauen, z. B. als `admin`:
     `flask-unsign --sign --cookie "{'user': 'admin'}" --secret "schulung-nicht-geheim"`
  4. In den DevTools das `session`-Cookie durch diesen Wert ersetzen → man ist admin,
     ohne je ein Passwort gekannt zu haben.

### 14. Debug-Modus / Werkzeug-Debugger-RCE
- **Ort:** `app.run(host="0.0.0.0", port=port, debug=True)`.
- **Folge:** Interaktive Debugger-Konsole im Browser → Ausführung von Python-Code; im ganzen Netz erreichbar.
- **So nutzt man es aus:**
  1. Einen Fehler (eine Exception) auslösen – dann zeigt Flask eine Traceback-Seite.
  2. Auf der Traceback-Seite rechts neben einer Code-Zeile auf das **Konsolen-Symbol** klicken.
  3. Nach der **Debugger-PIN** fragt die Konsole – die steht im Server-Log beim Start.
  4. In der Konsole beliebigen Python-Code ausführen, z. B.:
     ```python
     import os; os.popen("whoami").read()
     ```

---

## 📝 Vorlage für neue Lücken

> Beim Einbauen einer neuen Lücke: Zeile in die **Übersichtstabelle** oben
> ergänzen UND hier einen Detail-Block anhängen.

```markdown
### <Nr>. <Name der Lücke>
- **Ort / Route:** 
- **Ursache:** 
- **Folge:** 
- **So nutzt man es aus:**
  1. 
  2. 
  3. 
- **Datum eingebaut:** 
```

---

## Changelog

- **2026-10-15** – Exploit-Beschreibungen in Schritt-für-Schritt-Anleitungen umgewandelt.
- **2026-10-15** – Lücken 4–11 ergänzt (XSS, Command Injection, Access Control,
  CSRF, Open Redirect). Lücken 1–3, 12–14 waren bereits vorhanden.
