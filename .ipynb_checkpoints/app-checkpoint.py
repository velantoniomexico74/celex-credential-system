from flask import Flask, render_template, request, redirect, session, jsonify, send_file
from flask_socketio import SocketIO
import sqlite3
import pandas as pd
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = "CELEX2025"
socketio = SocketIO(app)

# --- UPLOADS ----
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ---- DB CONNECTION ----
def get_db():
    return sqlite3.connect("grades.db")


# ---- LOGIN ----
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cur.fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect("/home")

        return render_template("login.html", error="Usuario o contraseña incorrectos")

    return render_template("login.html")


# ---- HOME ----
@app.route("/home")
def home():
    if "user" not in session:
        return redirect("/")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT students.id, students.name, COALESCE(grades.grade, '')
        FROM students
        LEFT JOIN grades ON students.id = grades.student_id
    """)
    students = cur.fetchall()
    conn.close()

    return render_template("index.html", students=students)


# ---- SAVE GRADES ----
@app.route("/save", methods=["POST"])
def save():
    data = request.get_json()
    conn = get_db()
    cur = conn.cursor()

    for row in data:
        cur.execute("INSERT OR REPLACE INTO grades (student_id, grade) VALUES (?,?)",
                    (row["id"], row["grade"]))

    conn.commit()
    conn.close()

    return "OK"


# ---- EXPORT TO EXCEL ----
@app.route("/export/excel")
def export_excel():
    conn = get_db()
    df = pd.read_sql_query("""
        SELECT s.name AS Alumno, COALESCE(g.grade,'') AS Calificación
        FROM students s
        LEFT JOIN grades g ON s.id = g.student_id
    """, conn)
    conn.close()

    filename = "calificaciones.xlsx"
    df.to_excel(filename, index=False)

    return send_file(filename, as_attachment=True)


# ---- PRINT VIEW ----
@app.route("/print")
def print_view():
    import datetime
    fecha = datetime.datetime.now().strftime("%d/%m/%Y")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT students.name, COALESCE(grades.grade, '')
        FROM students
        LEFT JOIN grades ON students.id = grades.student_id
    """)
    records = cur.fetchall()

    return render_template("print.html", data=records, fecha=fecha)


# ---- UPLOAD STUDENTS FROM EXCEL ----
@app.route("/upload-students", methods=["GET", "POST"])
def upload_students():
    if request.method == "POST":
        if "file" not in request.files:
            return "No se envió archivo", 400

        file = request.files["file"]

        if file.filename == "":
            return "Archivo vacío", 400

        filename = secure_filename(file.filename)
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(path)

        df = pd.read_excel(path)

        if "Nombre" not in df.columns:
            return "ERROR: El Excel debe contener una columna llamada 'Nombre'", 400

        conn = get_db()
        cur = conn.cursor()

        for name in df["Nombre"]:
            cur.execute("INSERT INTO students (name) VALUES (?)", (name,))

        conn.commit()
        conn.close()

        return "Alumnos cargados correctamente."

    return render_template("upload_students.html")


# ---- LOGOUT ----
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---- RUN ----
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)
