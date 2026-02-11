import sqlite3

conn = sqlite3.connect("celex.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE alumnos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    apellido_paterno TEXT,
    apellido_materno TEXT,
    nombres TEXT,
    nivel_academico TEXT,
    turno_celex TEXT,
    telefono TEXT,
    correo TEXT,
    edad INTEGER,
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
    matricula TEXT UNIQUE,
    padecimiento TEXT,
    no_foto TEXT,
    fecha_registro TEXT
);
""")

conn.commit()
conn.close()

print("✅ Base de datos CELEX creada desde cero correctamente")
