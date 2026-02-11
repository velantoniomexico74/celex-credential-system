import sqlite3
import pandas as pd
import os
import sys

BASE_DIR = "/home/antonio/celex"
DB_PATH = os.path.join(BASE_DIR, "celex.db")
EXCEL_PATH = os.path.join(BASE_DIR, "uploads", "BaseDatosCelexEnero.xlsx")

# Validaciones básicas
if not os.path.exists(DB_PATH):
    print("❌ Base de datos no encontrada:", DB_PATH)
    sys.exit(1)

if not os.path.exists(EXCEL_PATH):
    print("❌ Archivo Excel no encontrado:", EXCEL_PATH)
    sys.exit(1)

# Leer Excel
df = pd.read_excel(EXCEL_PATH)

# Convertir fechas a texto (SQLite no soporta Timestamp)
if "FechaRegistro" in df.columns:
    df["FechaRegistro"] = df["FechaRegistro"].astype(str)





# Mapeo Excel → Base de datos
column_map = {
    "Apellido Paterno": "apellido_paterno",
    "Apellido Materno": "apellido_materno",
    "Nombre(s)": "nombres",
    "Nivel Académico": "nivel_academico",
    "Turno CELEX": "turno_celex",
    "Teléfono": "telefono",
    "Correo": "correo",
    "Edad": "edad",
    "Género": "genero",
    "Tipo Alumno": "tipo_alumno",
    "No. Boleta": "no_boleta",
    "Semestre": "semestre",
    "No. Empleado Docente": "no_empleado_docente",
    "No. Empleado PAAE": "no_empleado_paae",
    "Nombre Emergencia": "nombre_emergencia",
    "Teléfono Emergencia": "telefono_emergencia",
    "Correo Emergencia": "correo_emergencia",
    "Firma Tutor": "firma_tutor",
    "Matricula": "matricula",
    "padecimiento": "padecimiento",
    "No. foto": "no_foto",
    "FechaRegistro": "fecha_registro"
}

# Verificar columnas requeridas
missing = [c for c in column_map if c not in df.columns]
if missing:
    print("❌ El Excel no contiene las siguientes columnas obligatorias:")
    for col in missing:
        print(" -", col)
    sys.exit(1)

# Renombrar columnas
df = df.rename(columns=column_map)

# Conectar a la base
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Insertar registros
for _, row in df.iterrows():
    cur.execute("""
        INSERT INTO alumnos (
            apellido_paterno, apellido_materno, nombres, nivel_academico,
            turno_celex, telefono, correo, edad, genero, tipo_alumno,
            no_boleta, semestre, no_empleado_docente, no_empleado_paae,
            nombre_emergencia, telefono_emergencia, correo_emergencia,
            firma_tutor, matricula, padecimiento, no_foto, fecha_registro
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, tuple(row[col] for col in column_map.values()))

conn.commit()
conn.close()

print(f"✅ Importación finalizada. Registros insertados: {len(df)}")
