from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os


from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

# 🔹 AQUÍ puedes poner constantes
ROLES_VALIDOS = ["admin", "operador", "profesor"]

# 🔹 AQUÍ va la función requiere_rol
def requiere_rol(*roles):
    from functools import wraps
    def wrapper(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            if "user" not in session:
                return redirect(url_for("login"))
            if session.get("role") not in roles:
                return "No autorizado", 403
            return func(*args, **kwargs)
        return decorated
    return wrapper

app = Flask(__name__)
app.secret_key = "celex_secret_key"

# ===============================
# RUTAS
# ===============================




app = Flask(__name__)
app.secret_key = "celex_secret_key"

# ===============================
# CARPETAS
# ===============================
UPLOAD_FOLDER = "uploads"
FOTOS_FOLDER = "fotos"
CRED_FOLDER = "credenciales"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(FOTOS_FOLDER, exist_ok=True)
os.makedirs(CRED_FOLDER, exist_ok=True)

# ===============================
# LOGIN
# ===============================

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("celex.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM usuarios WHERE username = ?", (username,))
        user = cur.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session["user"] = username
            session["role"] = user[3]
            return redirect(url_for("dashboard"))


    #    if user and check_password_hash(user[2], password):
    #        session["user"] = username
    #        return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Credenciales incorrectas")

    return render_template("login.html")


# ===============================
# DASHBOARD
# ===============================
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("dashboard.html", user=session["user"])


# ===============================
# LOGOUT
# ===============================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ===============================
# MAIN
# ===============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
