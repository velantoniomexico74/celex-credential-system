from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3
import pandas as pd
from werkzeug.utils import secure_filename
import os
import re
import zipfile
from generate_credential_batch import generar_credenciales, generar_credencial_individual

app = Flask(__name__)
app.secret_key = "CELEX2025"

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
        if request.form["username"] == "admin" and request.form["password"] == "celex":
            session["user"] = "admin"
            return redirect("/dashboard")
        return render_template("login.html", error="Credenciales incorrectas")
    return render_template("login.html")

# ===============================
# DASHBOARD
# ===============================
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    return render_template("dashboard.html")

# ===============================
# MÓDULO CREDENCIALES
# ===============================
@app.route("/credenciales", methods=["GET", "POST"])
def credenciales():

    if "user" not in session:
        return redirect("/")

    # ---------------------------------
    # GENERACIÓN MASIVA
    # ---------------------------------
    if request.method == "POST" and "excel" in request.files:

        # 1️⃣ Limpiar tabla alumnos
        conn = sqlite3.connect("celex.db")
        cur = conn.cursor()
        cur.execute("DELETE FROM alumnos")
        conn.commit()
        conn.close()

        # 2️⃣ Guardar Excel
        excel = request.files["excel"]
        excel_path = os.path.join(UPLOAD_FOLDER, secure_filename(excel.filename))
        excel.save(excel_path)

        df = pd.read_excel(excel_path)
        df.columns = df.columns.str.strip()

        df = df.rename(columns={
            "Nombre(s)": "Nombres"
        })

        conn = sqlite3.connect("celex.db")
        cur = conn.cursor()

        for _, row in df.iterrows():
            cur.execute("""
                INSERT INTO alumnos (
                    apellido_paterno,
                    apellido_materno,
                    nombres,
                    matricula,
                    nivel_academico,
                    turno_celex,
                    no_foto
                ) VALUES (?,?,?,?,?,?,?)
            """, (
                row["Apellido Paterno"],
                row["Apellido Materno"],
                row["Nombres"],
                row["Matricula"],
                row["Nivel Académico"],
                row["Turno CELEX"],
                row["No. foto"]
            ))

        conn.commit()
        conn.close()
        os.remove(excel_path)

        # 3️⃣ Limpiar fotos
        for f in os.listdir(FOTOS_FOLDER):
            os.remove(os.path.join(FOTOS_FOLDER, f))

        # 4️⃣ Guardar fotos
        fotos = request.files.getlist("fotos")

        for foto in fotos:
            filename = secure_filename(foto.filename)
            match = re.search(r"\d+", filename)

            if match:
                numero = match.group()
                new_name = f"{numero}.jpg"
                foto.save(os.path.join(FOTOS_FOLDER, new_name))

        # 5️⃣ Limpiar credenciales previas
        for f in os.listdir(CRED_FOLDER):
            os.remove(os.path.join(CRED_FOLDER, f))

        # 6️⃣ Generar credenciales
        generar_credenciales()

        # 7️⃣ Crear ZIP
        zip_path = "credenciales.zip"

        with zipfile.ZipFile(zip_path, "w") as zipf:
            for file in os.listdir(CRED_FOLDER):
                zipf.write(os.path.join(CRED_FOLDER, file), file)

        return send_file(zip_path, as_attachment=True)

    # ---------------------------------
    # REIMPRESIÓN INDIVIDUAL
    # ---------------------------------
    if request.method == "POST" and "matricula" in request.form:

        matricula = request.form["matricula"]
        archivo = generar_credencial_individual(matricula)

        if not archivo:
            return render_template(
                "credenciales.html",
                error="Matrícula no encontrada o sin foto."
            )

        return send_file(archivo, as_attachment=True)

    return render_template("credenciales.html")

# ===============================
# LOGOUT
# ===============================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ===============================
# MAIN
# ===============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
