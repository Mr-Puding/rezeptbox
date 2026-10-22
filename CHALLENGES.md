# 🏴 RezeptBox – Hacking-Challenges

> Übungsaufgaben für die Vorlesung **„Hacking mit Python"**.
> Ziel: In der absichtlich unsicheren Web-App **RezeptBox** die versteckten
> Schwachstellen finden und ausnutzen.
>
> 🌐 **Server-Adresse (im Klassen-WLAN):** `http://141.87.60.99:5000`
> _(Läuft der Server auf einem anderen Rechner, dort die IP anpassen –
> `http://<SERVER-IP>:5000`. „localhost" funktioniert nur auf dem Server selbst.)_

**Test-Account zum Einloggen:** `mia` / `pommes123`
_(Challenge 1 schafft man auch ganz ohne gültiges Passwort.)_

---

## Challenge 1 – Türsteher austricksen 🔑

- **Ziel:** Logge dich ein, **ohne das Passwort zu kennen**.
- **Adresse:** `http://141.87.60.99:5000/login`
- **Aufgabe:** Finde eine Eingabe im Benutzername-Feld, die die Anmeldung
  immer durchwinkt. Stichwort: Das Feld landet direkt in einer Datenbank-Abfrage.
- **Geschafft, wenn:** du im Dashboard landest, obwohl du kein echtes Passwort eingegeben hast.

## Challenge 2 – Blick in die Datenbank 🗄️

- **Ziel:** Lies **Benutzernamen und Passwörter** anderer Konten aus.
- **Adresse:** `http://141.87.60.99:5000/rezept/1`
- **Aufgabe:** Die Rezept-Seite lädt ein Rezept anhand einer Nummer in der URL.
  Manipuliere diese Nummer so, dass statt eines Rezepts Daten aus der
  Benutzer-Tabelle angezeigt werden.
- **Geschafft, wenn:** ein Benutzername + Passwort als „Rezept" auf dem Bildschirm steht.

## Challenge 3 – Code einschleusen (sichtbar für alle) 💥

- **Ziel:** Bringe die Seite dazu, bei **jedem Besucher** ein Popup / eigenen Code auszuführen.
- **Adresse:** `http://141.87.60.99:5000/rezept/new`
- **Aufgabe:** Lege ein neues Rezept an und schmuggle in Titel oder Inhalt
  HTML/JavaScript ein. Öffne danach das Rezept – und überlege, was passiert,
  wenn es jemand anderes öffnet.
- **Geschafft, wenn:** beim Öffnen des Rezepts dein Code ausgeführt wird.

## Challenge 4 – Code über einen Link 🔗

- **Ziel:** Führe Code aus, indem du nur eine **präparierte URL** aufrufst.
- **Adresse:** `http://141.87.60.99:5000/dashboard`
- **Aufgabe:** Das Suchfeld zeigt den Suchbegriff wieder an. Baue eine URL,
  die statt eines Suchworts Code enthält.
- **Geschafft, wenn:** allein das Öffnen deiner URL den Code auslöst.

## Challenge 5 – Befehle auf dem Server ausführen 🖥️

- **Ziel:** Lass den **Server einen Betriebssystem-Befehl** ausführen.
- **Adresse:** `http://141.87.60.99:5000/tools`
- **Aufgabe:** Die Diagnose-Funktion „pingt" eine eingegebene Adresse.
  Hänge an die Adresse einen zweiten Befehl an.
- **Geschafft, wenn:** in der Ausgabe das Ergebnis deines Befehls (z. B. der Server-Benutzer) steht.

## Challenge 6 – Admin werden 👑

- **Ziel:** Öffne die **Admin-Seite**, obwohl du nur ein normaler Nutzer bist.
- **Adresse:** `http://141.87.60.99:5000/admin`
- **Aufgabe:** Mach dich zum Admin.
- **Geschafft, wenn:** die Admin-Seite dir alle Konten inkl. Passwörter zeigt.

## Challenge 7 – Fremdes Rezept übernehmen ✏️

- **Ziel:** Ändere ein Rezept, das **dir nicht gehört**.
- **Adresse:** `http://141.87.60.99:5000/rezept`
- **Aufgabe:** Versuche, ein Rezept eines anderen Autors zu überschreiben
- **Geschafft, wenn:** ein fremdes Rezept deinen geänderten Text zeigt.

## Challenge 8 – Rezept per Falle löschen 🗑️

- **Ziel:** Lösche ein Rezept **ohne den normalen Löschen-Knopf**.
- **Adresse:** `http://141.87.60.99:5000/rezept`
- **Aufgabe:** Finde heraus, wie man die Adresse manipulieren kann.
  Überlege, wie man ein eingeloggtes Opfer dazu bringt, diesen Aufruf
  unbemerkt auszulösen.
- **Geschafft, wenn:** ein Rezept verschwindet, ohne dass bewusst „Löschen" geklickt wurde.

## Challenge 9 – Weiterleitung auf fremde Seite 🪝

- **Ziel:** Bringe den Login dazu, dich nach der Anmeldung auf eine **fremde Seite** zu schicken.
- **Adresse:** `http://141.87.60.99:5000/login`
- **Aufgabe:** Manipuliere die Adresse um ein Redirect zu erreichen.
- **Geschafft, wenn:** du nach dem Login auf der fremden Adresse landest.

---

## 🏆 Bonus-Challenges (schwerer)

## Challenge 10 – Neuen Benutzer einschmuggeln

- **Ziel:** Nutze die **Registrierung**, um die Datenbank-Abfrage zu manipulieren.
- **Adresse:** `http://141.87.60.99:5000/register`
- **Aufgabe:** Provoziere eine Fehlermeldung oder einen zusätzlichen Eintrag.
- **Geschafft, wenn:** eine DB-Fehlermeldung erscheint oder ein unerwarteter Benutzer existiert.

## Challenge 11 – Sitzung fälschen

- **Ziel:** Gib dich als `admin` aus, **ohne** dessen Passwort – über ein gefälschtes Session-Cookie.
- **Adresse:** `http://141.87.60.99:5000/`
- **Aufgabe:** Der geheime Schlüssel der App ist sehr schwach. Mit einem Tool wie
  `flask-unsign` lässt sich ein eigenes gültiges Cookie erzeugen.
- **Geschafft, wenn:** du als `admin` angezeigt wirst, ohne dich je korrekt angemeldet zu haben.
