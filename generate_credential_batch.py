# CELEX Credential System
# Ing. Jose Antonio Velazquez

import sqlite3
from PIL import Image, ImageDraw, ImageFont, ImageOps
import os
from datetime import datetime

# ===============================
# CONFIGURACIÓN
# ===============================
DB = "celex.db"
FOTOS = "fotos"
LAYOUT = "layouts/CredencialCELEXFinal.png"
OUT = "credenciales"
LOG_FILE = os.path.join(OUT, "errores_credenciales.log")
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

os.makedirs(OUT, exist_ok=True)

# ===============================
# FUNCIÓN LOG
# ===============================
def log_error(matricula, nombre, motivo):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {matricula} | {nombre} | {motivo}\n")

# ===============================
# CONEXIÓN DB
# ===============================
conn = sqlite3.connect(DB)
cur = conn.cursor()

cur.execute("""
SELECT
    apellido_paterno,
    apellido_materno,
    nombres,
    matricula,
    nivel_academico,
    turno_celex,
    no_foto
FROM alumnos
""")

rows = cur.fetchall()

if not rows:
    print("No se encontraron alumnos")
    exit(1)

print(f"▶ Generando {len(rows)} credenciales...\n")

# ===============================
# LOOP PRINCIPAL
# ===============================
for row in rows:
    ap, am, nom, matricula, nivel, turno, no_foto = row
    nombre_completo = f"{nom} {ap} {am}".upper()

    try:
        foto_path = f"{FOTOS}/{no_foto}.jpg"
        if not os.path.exists(foto_path):
            log_error(matricula, nombre_completo, f"Foto no encontrada ({foto_path})")
            print(f"⚠ Foto no encontrada: {matricula}")
            continue

        # ===============================
        # LAYOUT
        # ===============================
        base = Image.open(LAYOUT).convert("RGB")
        draw = ImageDraw.Draw(base)

        # ===============================
        # FUENTES
        # ===============================
        font_nombre = ImageFont.truetype(FONT_PATH, 34)
        font_apellidos = ImageFont.truetype(FONT_PATH, 32)
        font_datos = ImageFont.truetype(FONT_PATH, 26)
        font_ref = ImageFont.truetype(FONT_PATH, 11)

        # ===============================
        # FOTO (FIX EXIF)
        # ===============================
        foto = Image.open(foto_path)
        foto = ImageOps.exif_transpose(foto)   # 🔑 FIX
        foto = foto.resize((260, 330))
        base.paste(foto, (170, 304))

        # ===============================
        # TEXTO
        # ===============================
        CARD_WIDTH = base.width

        def draw_centered_text(y, text, font, fill="#4A4A4A"):
            w = draw.textlength(text, font=font)
            x = (CARD_WIDTH - w) // 2
            draw.text((x, y), text, fill=fill, font=font)

        draw_centered_text(670, nom.upper(), font_nombre)
        draw_centered_text(710, f"{ap} {am}".upper(), font_apellidos)
        draw_centered_text(760, f"MATRÍCULA: {matricula}", font_datos)

        # Etiqueta Foto ID
        draw.text(
            (CARD_WIDTH - 140, base.height - 14),
            f"Foto ID: {no_foto}",
            fill="#8A8A8A",
            font=font_ref
        )

        # ===============================
        # GUARDAR
        # ===============================
        out_file = f"{OUT}/{matricula}.png"
        base.save(out_file)

        print(f"✔ Generada: {matricula}")

    except Exception as e:
        log_error(matricula, nombre_completo, str(e))
        print(f"❌ Error en {matricula}")

