"""
RezeptBox – Demonstrator-Webseite (bewusst unsicher)
=====================================================

Schulungsprojekt. Diese App ist ABSICHTLICH unsicher programmiert, damit
Mitschüler:innen im Unterricht SQL-Injection praktisch ausprobieren können.
In einer späteren Phase wird die App abgesichert.

NICHT ins Internet stellen – nur lokal im Klassennetz betreiben.

Thema: Eine kleine Rezept-Community. Nutzer:innen melden sich an und
teilen Rezepte (Titel, Zutaten/Zubereitung, Autor:in, Status).

Datenbank:
  - Standard: MySQL (wie in der Anforderung).  -> DB_BACKEND=mysql
  - Zum schnellen Starten ohne MySQL-Server:   -> DB_BACKEND=sqlite
    (läuft sofort, erzeugt rezepte.db automatisch)
"""

import os
from flask import (
    Flask, request, redirect, url_for, session,
    render_template, flash, make_response
)

app = Flask(__name__)
app.secret_key = "__ENTFERNT_AUS_HISTORIE__"  # bewusst simpel, nur Demo

# ---------------------------------------------------------------------------
# Datenbank-Anbindung  (MySQL laut Anforderung, SQLite als Zero-Setup-Option)
# ---------------------------------------------------------------------------
DB_BACKEND = os.environ.get("DB_BACKEND", "mysql").lower()

if DB_BACKEND == "mysql":
    import mysql.connector

    DB_CONFIG = {
        "host": os.environ.get("DB_HOST", "127.0.0.1"),
        "port": int(os.environ.get("DB_PORT", "3306")),
        "user": os.environ.get("DB_USER", "root"),
        "password": os.environ.get("DB_PASSWORD", ""),
        "database": os.environ.get("DB_NAME", "rezeptbox"),
    }

    def get_db():
        return mysql.connector.connect(**DB_CONFIG)

else:  # sqlite
    import sqlite3

    DB_FILE = os.environ.get("DB_FILE", "rezepte.db")

    def get_db():
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        return conn


def init_db():
    """Erstellt Tabellen + Beispieldaten, falls noch nicht vorhanden."""
    conn = get_db()
    cur = conn.cursor()

    if DB_BACKEND == "mysql":
        cur.execute(
            "CREATE TABLE IF NOT EXISTS users ("
            " id INT AUTO_INCREMENT PRIMARY KEY,"
            " username VARCHAR(100),"
            " password VARCHAR(100))"
        )
        cur.execute(
            "CREATE TABLE IF NOT EXISTS rezepte ("
            " id INT AUTO_INCREMENT PRIMARY KEY,"
            " title VARCHAR(200),"
            " content TEXT,"
            " author VARCHAR(100),"
            " status VARCHAR(50))"
        )
    else:
        cur.execute(
            "CREATE TABLE IF NOT EXISTS users ("
            " id INTEGER PRIMARY KEY AUTOINCREMENT,"
            " username TEXT,"
            " password TEXT)"
        )
        cur.execute(
            "CREATE TABLE IF NOT EXISTS rezepte ("
            " id INTEGER PRIMARY KEY AUTOINCREMENT,"
            " title TEXT,"
            " content TEXT,"
            " author TEXT,"
            " status TEXT)"
        )

    # Beispieldaten nur einmal einfügen
    cur.execute("SELECT COUNT(*) FROM users")
    count = cur.fetchone()[0]
    if count == 0:
        seed_users = [
            ("admin", "__ENTFERNT__"),
            ("mia", "__ENTFERNT__"),
            ("ben", "__ENTFERNT__"),
        ]
        seed_rezepte = [
            ("Omas Apfelkuchen",
             "Zutaten: 4 Äpfel, 200 g Mehl, 150 g Zucker, 3 Eier, 1 Pck. "
             "Backpulver.\nZubereitung: Teig verrühren, Äpfel unterheben, "
             "bei 180 °C 40 Minuten backen.",
             "mia", "veröffentlicht"),
            ("Schnelle Tomatensuppe",
             "Zutaten: 1 Dose Tomaten, 1 Zwiebel, Gemüsebrühe, Sahne.\n"
             "Zubereitung: Zwiebel andünsten, Tomaten + Brühe zugeben, "
             "pürieren, mit Sahne verfeinern.",
             "ben", "veröffentlicht"),
            ("Geheimer Schokokuchen",
             "Zutaten: 200 g Schokolade, 200 g Butter, 4 Eier, 150 g Zucker.\n"
             "Zubereitung: Schokolade + Butter schmelzen, Rest unterrühren, "
             "bei 160 °C 35 Minuten backen.",
             "admin", "Entwurf"),
        ]
        ph = "%s" if DB_BACKEND == "mysql" else "?"
        cur.executemany(
            f"INSERT INTO users (username, password) VALUES ({ph}, {ph})",
            seed_users,
        )
        cur.executemany(
            f"INSERT INTO rezepte (title, content, author, status) "
            f"VALUES ({ph}, {ph}, {ph}, {ph})",
            seed_rezepte,
        )

    conn.commit()
    cur.close()
    conn.close()


# ---------------------------------------------------------------------------
# Routen
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    if session.get("user"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        # ===================================================================
        # !!! BEWUSST UNSICHER !!!  (Kernthema: SQL Injection)
        # Die Eingaben werden direkt in das SQL-Statement eingebaut.
        # Dadurch lässt sich die Abfrage manipulieren, z. B. mit:
        #     Benutzername:  admin' --
        #     Benutzername:  ' OR '1'='1
        # ===================================================================
        query = (
            "SELECT * FROM users "
            "WHERE username = '" + username + "' "
            "AND password = '" + password + "'"
        )

        conn = get_db()
        cur = conn.cursor()
        row = None
        error = None
        try:
            cur.execute(query)
            row = cur.fetchone()
        except Exception as e:
            # Fehlermeldung wird angezeigt -> erleichtert das Finden der Lücke
            error = str(e)
        finally:
            cur.close()
            conn.close()

        if error:
            flash("Datenbankfehler: " + error, "error")
            return render_template("login.html", debug_query=query)

        if row:
            session["user"] = username if username else "unbekannt"

            # ===============================================================
            # !!! BEWUSST UNSICHER !!!  Broken Access Control
            # Die "Rolle" wird in einem Cookie gespeichert, das der Client
            # beliebig ändern kann. Wer das Cookie auf role=admin setzt,
            # bekommt Admin-Rechte (siehe /admin). Kein Server-seitiger Check.
            # ===============================================================
            # ===============================================================
            # !!! BEWUSST UNSICHER !!!  Open Redirect
            # Nach dem Login wird ungeprüft auf ?next=... weitergeleitet,
            # z. B.  /login?next=https://phishing.example  -> Weiterleitung
            # auf eine fremde Seite.
            # ===============================================================
            next_url = request.form.get("next") or request.args.get("next", "")
            resp = make_response(
                redirect(next_url) if next_url else redirect(url_for("dashboard"))
            )
            resp.set_cookie("role", "user")
            return resp
        else:
            flash("Benutzername oder Passwort falsch.", "error")
            return render_template("login.html", debug_query=query)

    next_url = request.args.get("next", "")
    return render_template("login.html", next_url=next_url)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        password2 = request.form.get("password2", "")

        if not username or not password:
            flash("Bitte Benutzername und Passwort angeben.", "error")
            return render_template("register.html")

        if password != password2:
            flash("Die Passwörter stimmen nicht überein.", "error")
            return render_template("register.html")

        # ===================================================================
        # !!! BEWUSST UNSICHER !!!  Auch hier String-Verkettung statt
        # parametrisierter Query.
        # ===================================================================
        query = (
            "INSERT INTO users (username, password) VALUES ('"
            + username + "', '" + password + "')"
        )

        conn = get_db()
        cur = conn.cursor()
        try:
            cur.execute(query)
            conn.commit()
        except Exception as e:
            flash("Datenbankfehler: " + str(e), "error")
            cur.close()
            conn.close()
            return render_template("register.html", debug_query=query)
        cur.close()
        conn.close()

        flash("Registrierung erfolgreich! Du kannst dich jetzt anmelden.", "ok")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/dashboard")
def dashboard():
    if not session.get("user"):
        return redirect(url_for("login"))

    # ===================================================================
    # !!! BEWUSST UNSICHER !!!  Suchfeld mit SQL Injection (LIKE)
    # Der Suchbegriff wird direkt in die Query verkettet.
    # Der gleiche Begriff wird außerdem im Template ohne Escaping
    # ausgegeben -> zusätzlich Reflected XSS, z. B.:
    #   ?q=<script>alert(document.cookie)</script>
    # ===================================================================
    q = request.args.get("q", "")
    conn = get_db()
    cur = conn.cursor()
    if q:
        cur.execute(
            "SELECT id, title, author, status FROM rezepte "
            "WHERE title LIKE '%" + q + "%' ORDER BY id"
        )
    else:
        cur.execute("SELECT id, title, author, status FROM rezepte ORDER BY id")
    rezepte = cur.fetchall()
    cur.close()
    conn.close()

    # Einheitliches Format (Liste von Dicts) für beide Backends
    rezepte = [
        {"id": r[0], "title": r[1], "author": r[2], "status": r[3]}
        for r in rezepte
    ]
    return render_template(
        "dashboard.html", user=session["user"], rezepte=rezepte, q=q
    )


@app.route("/rezept/<rezept_id>")
def rezept(rezept_id):
    if not session.get("user"):
        return redirect(url_for("login"))

    # ===================================================================
    # !!! BEWUSST UNSICHER !!!  rezept_id wird direkt eingesetzt ->
    # UNION-basierte SQL Injection möglich, z. B.:
    #   /rezept/0 UNION SELECT 1,username,password,4,5 FROM users
    # ===================================================================
    query = "SELECT id, title, content, author, status FROM rezepte WHERE id = " + str(rezept_id)

    conn = get_db()
    cur = conn.cursor()
    row = None
    error = None
    try:
        cur.execute(query)
        row = cur.fetchone()
    except Exception as e:
        error = str(e)
    finally:
        cur.close()
        conn.close()

    if error:
        flash("Datenbankfehler: " + error, "error")
        return redirect(url_for("dashboard"))

    if not row:
        flash("Rezept nicht gefunden.", "error")
        return redirect(url_for("dashboard"))

    rezept_data = {
        "id": row[0], "title": row[1], "content": row[2],
        "author": row[3], "status": row[4],
    }
    return render_template("rezept.html", rezept=rezept_data)


@app.route("/rezept/new", methods=["GET", "POST"])
def new_rezept():
    if not session.get("user"):
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form.get("title", "")
        content = request.form.get("content", "")
        author = session["user"]

        ph = "%s" if DB_BACKEND == "mysql" else "?"
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            f"INSERT INTO rezepte (title, content, author, status) "
            f"VALUES ({ph}, {ph}, {ph}, {ph})",
            (title, content, author, "veröffentlicht"),
        )
        conn.commit()
        cur.close()
        conn.close()

        flash("Rezept wurde gespeichert.", "ok")
        return redirect(url_for("dashboard"))

    return render_template("new_rezept.html")


@app.route("/rezept/<rezept_id>/edit", methods=["GET", "POST"])
def edit_rezept(rezept_id):
    if not session.get("user"):
        return redirect(url_for("login"))

    ph = "%s" if DB_BACKEND == "mysql" else "?"
    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        title = request.form.get("title", "")
        content = request.form.get("content", "")
        # ===============================================================
        # !!! BEWUSST UNSICHER !!!  Broken Access Control (IDOR)
        # Es wird NICHT geprüft, ob das Rezept der angemeldeten Person
        # gehört. Jede:r kann über /rezept/<id>/edit fremde Rezepte
        # überschreiben.
        # ===============================================================
        cur.execute(
            f"UPDATE rezepte SET title = {ph}, content = {ph} WHERE id = {ph}",
            (title, content, rezept_id),
        )
        conn.commit()
        cur.close()
        conn.close()
        flash("Rezept wurde aktualisiert.", "ok")
        return redirect(url_for("rezept", rezept_id=rezept_id))

    cur.execute(
        f"SELECT id, title, content FROM rezepte WHERE id = {ph}", (rezept_id,)
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        flash("Rezept nicht gefunden.", "error")
        return redirect(url_for("dashboard"))

    rezept_data = {"id": row[0], "title": row[1], "content": row[2]}
    return render_template("edit_rezept.html", rezept=rezept_data)


@app.route("/rezept/<rezept_id>/delete")
def delete_rezept(rezept_id):
    if not session.get("user"):
        return redirect(url_for("login"))

    # ===================================================================
    # !!! BEWUSST UNSICHER !!!  CSRF + Broken Access Control
    # Löschen passiert per GET-Request ohne Token und ohne Besitzprüfung.
    # Ein eingebettetes <img src="/rezept/3/delete"> reicht, um fremde
    # Rezepte zu löschen (CSRF).
    # ===================================================================
    ph = "%s" if DB_BACKEND == "mysql" else "?"
    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM rezepte WHERE id = {ph}", (rezept_id,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Rezept wurde gelöscht.", "ok")
    return redirect(url_for("dashboard"))


@app.route("/admin")
def admin():
    if not session.get("user"):
        return redirect(url_for("login"))

    # ===================================================================
    # !!! BEWUSST UNSICHER !!!  Broken Access Control
    # Die Rolle wird aus einem vom Client manipulierbaren Cookie gelesen.
    # Mit  document.cookie = "role=admin"  (oder über die DevTools)
    # bekommt jede:r Zugriff auf diese Seite – inklusive aller
    # Benutzernamen und Klartext-Passwörter.
    # ===================================================================
    role = request.cookies.get("role", "user")
    if role != "admin":
        flash("Zugriff verweigert – nur für Admins (Cookie role=admin).", "error")
        return redirect(url_for("dashboard"))

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, username, password FROM users ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    users = [{"id": r[0], "username": r[1], "password": r[2]} for r in rows]
    return render_template("admin.html", users=users)


@app.route("/tools", methods=["GET", "POST"])
def tools():
    if not session.get("user"):
        return redirect(url_for("login"))

    output = None
    cmd = None
    if request.method == "POST":
        host = request.form.get("host", "")
        # ===============================================================
        # !!! BEWUSST UNSICHER !!!  OS Command Injection
        # Die Eingabe wird direkt an die System-Shell übergeben.
        # Mit einem Trenner lassen sich beliebige Befehle anhängen, z. B.:
        #   Windows:   127.0.0.1 & whoami
        #   Linux/Mac: 127.0.0.1; id
        # ===============================================================
        ping_count = "-n" if os.name == "nt" else "-c"
        cmd = "ping " + ping_count + " 1 " + host
        output = os.popen(cmd).read()

    return render_template("tools.html", output=output, cmd=cmd)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", "8000"))
    # host=0.0.0.0, damit Mitschüler:innen im Klassennetz zugreifen können
    app.run(host="0.0.0.0", port=port, debug=True)
