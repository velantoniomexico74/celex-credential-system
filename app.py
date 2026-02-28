from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3
import pandas as pd
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
import os
import re
import zipfile
from generate_credential_batch import generar_credenciales

app = Flask(__name__)
app.secret_key = "CELEX_SECRET_KEY_2026"

# 🔐 Credenciales seguras (hash fijo)
#USERNAME = "admin"
#PASSWORD_HASH = "pbkdf2:sha256:600000$Zk2C$4b66b8d2c41b7e8e8f2b7d7c3c55dcd28dba6f1c4e42e2a62f1b59e2b3d9b5a8"

from werkzeug.security import generate_password_hash
USERNAME = "admin"
PASSWORD_HASH = generate_password_hash("Celex_2026_Seguro!")


UPLOAD_FOLDER = "uploads"
FOTOS_FOLDER = "fotos"
CRED_FOLDER = "credenciales"
DB_NAME = "celex.db"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(FOTOS_FOLDER, exist_ok=True)
os.makedirs(CRED_FOLDER, exist_ok=True)


# ==========================
# LOGIN
# ==========================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == USERNAME and check_password_hash(PASSWORD_HASH, password):
            session["user"] = USERNAME
            return redirect("/dashboard")

        return render_template("login.html", error="Credenciales incorrectas")

    return render_template("login.html")


# ==========================
# DASHBOARD
# ==========================
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    return render_template("dashboard.html")


# ==========================
# GENERACIÓN DE CREDENCIALES
# ==========================
@app.route("/credenciales", methods=["GET", "POST"])
def credenciales():

    if "user" not in session:
        return redirect("/")

    if request.method == "POST":

        # ==========================
        # REIMPRESIÓN INDIVIDUAL
        # ==========================
        if "matricula" in request.form and "excel" not in request.files:
            matricula = request.form["matricula"].strip()

            ruta_credencial = os.path.join(CRED_FOLDER, f"{matricula}.png")

            if os.path.exists(ruta_credencial):
                return send_file(ruta_credencial, as_attachment=True)
            else:
                return render_template("credenciales.html", error="Credencial no encontrada.")




        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()

        # Recrear tabla limpia
        cur.execute("DROP TABLE IF EXISTS alumnos")

        cur.execute("""
            CREATE TABLE alumnos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                apellido_paterno TEXT,
                apellido_materno TEXT,
                nombres TEXT,
                nivel_academico TEXT,
                turno TEXT,
                telefono TEXT,
                correo TEXT,
                edad TEXT,
                genero TEXT,
                tipo_alumno TEXT,
                no_boleta TEXT,
                semestre TEXT,
                no_empleado_docente TEXT,
                no_empleado_paae TEXT,
                nombre_emergencia TEXT,
                telefono_emergencia TEXT,
                correo_emergencia TEXT,
                firma_tutor TEXT,
                matricula TEXT,
                padecimiento TEXT,
                no_foto TEXT,
                fecha_registro TEXT
            )
        """)

        conn.commit()

        # Guardar Excel temporal
        excel = request.files["excel"]
        excel_path = os.path.join(UPLOAD_FOLDER, secure_filename(excel.filename))
        excel.save(excel_path)

        df = pd.read_excel(excel_path)
        df.columns = df.columns.str.strip()

        if "FechaRegistro" in df.columns:
            df["FechaRegistro"] = df["FechaRegistro"].astype(str)

        for _, row in df.iterrows():
            cur.execute("""
                INSERT INTO alumnos VALUES (NULL,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                row.get("Apellido Paterno"),
                row.get("Apellido Materno"),
                row.get("Nombre(s)"),
                row.get("Nivel Académico"),
                row.get("Turno CELEX"),
                str(row.get("Teléfono")),
                row.get("Correo"),
                str(row.get("Edad")),
                row.get("Género"),
                row.get("Tipo Alumno"),
                str(row.get("No. Boleta")),
                str(row.get("Semestre")),
                str(row.get("No. Empleado Docente")),
                str(row.get("No. Empleado PAAE")),
                row.get("Nombre Emergencia"),
                str(row.get("Teléfono Emergencia")),
                row.get("Correo Emergencia"),
                row.get("Firma Tutor"),
                str(row.get("Matricula")),
                row.get("padecimiento"),
                str(row.get("No. foto")),
                row.get("FechaRegistro")
            ))

        conn.commit()
        conn.close()
        os.remove(excel_path)

        # Limpiar fotos anteriores
        for f in os.listdir(FOTOS_FOLDER):
            os.remove(os.path.join(FOTOS_FOLDER, f))

        fotos = request.files.getlist("fotos")
        for foto in fotos:
            filename = secure_filename(foto.filename)
            match = re.search(r"\d+", filename)
            if match:
                numero = match.group()
                foto.save(os.path.join(FOTOS_FOLDER, f"{numero}.jpg"))

        # Limpiar credenciales anteriores
        for f in os.listdir(CRED_FOLDER):
            os.remove(os.path.join(CRED_FOLDER, f))

        generar_credenciales()

        # Crear ZIP
        zip_path = "credenciales.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file in os.listdir(CRED_FOLDER):
                zipf.write(os.path.join(CRED_FOLDER, file), file)

        return send_file(zip_path, as_attachment=True)

    return render_template("credenciales.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
