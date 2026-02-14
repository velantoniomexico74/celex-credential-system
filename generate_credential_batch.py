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
def generar_credenciales():

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
        return "No se encontraron alumnos"

    for row in rows:
        ap, am, nom, matricula, nivel, turno, no_foto = row
        nombre_completo = f"{nom} {ap} {am}".upper()

        try:
            foto_path = f"{FOTOS}/{no_foto}.jpg"
            if not os.path.exists(foto_path):
                log_error(matricula, nombre_completo, f"Foto no encontrada ({foto_path})")
                continue

            base = Image.open(LAYOUT).convert("RGB")
            draw = ImageDraw.Draw(base)

            font_nombre = ImageFont.truetype(FONT_PATH, 34)
            font_apellidos = ImageFont.truetype(FONT_PATH, 32)
            font_datos = ImageFont.truetype(FONT_PATH, 26)
            font_ref = ImageFont.truetype(FONT_PATH, 11)

            foto = Image.open(foto_path)
            foto = ImageOps.exif_transpose(foto)
            foto = foto.resize((260, 330))
            base.paste(foto, (170, 304))

            CARD_WIDTH = base.width

            def draw_centered_text(y, text, font, fill="#4A4A4A"):
                w = draw.textlength(text, font=font)
                x = (CARD_WIDTH - w) // 2
                draw.text((x, y), text, fill=fill, font=font)

            draw_centered_text(670, nom.upper(), font_nombre)
            draw_centered_text(710, f"{ap} {am}".upper(), font_apellidos)
            draw_centered_text(760, f"MATRÍCULA: {matricula}", font_datos)

            draw.text(
                (CARD_WIDTH - 140, base.height - 14),
                f"Foto ID: {no_foto}",
                fill="#8A8A8A",
                font=font_ref
            )

            out_file = f"{OUT}/{matricula}.png"
            base.save(out_file)

        except Exception as e:
            log_error(matricula, nombre_completo, str(e))

    conn.close()
    return "Credenciales generadas correctamente"

def generar_credencial_individual(matricula_busqueda):

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
        WHERE matricula = ?
    """, (matricula_busqueda,))

    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    ap, am, nom, matricula, nivel, turno, no_foto = row
    nombre_completo = f"{nom} {ap} {am}".upper()

    foto_path = f"{FOTOS}/{no_foto}.jpg"
    if not os.path.exists(foto_path):
        return None

    base = Image.open(LAYOUT).convert("RGB")
    draw = ImageDraw.Draw(base)

    font_nombre = ImageFont.truetype(FONT_PATH, 34)
    font_apellidos = ImageFont.truetype(FONT_PATH, 32)
    font_datos = ImageFont.truetype(FONT_PATH, 26)
    font_ref = ImageFont.truetype(FONT_PATH, 11)

    foto = Image.open(foto_path)
    foto = ImageOps.exif_transpose(foto)
    foto = foto.resize((260, 330))
    base.paste(foto, (170, 304))

    CARD_WIDTH = base.width

    def draw_centered_text(y, text, font, fill="#4A4A4A"):
        w = draw.textlength(text, font=font)
        x = (CARD_WIDTH - w) // 2
        draw.text((x, y), text, fill=fill, font=font)

    draw_centered_text(670, nom.upper(), font_nombre)
    draw_centered_text(710, f"{ap} {am}".upper(), font_apellidos)
    draw_centered_text(760, f"MATRÍCULA: {matricula}", font_datos)

    draw.text(
        (CARD_WIDTH - 140, base.height - 14),
        f"Foto ID: {no_foto}",
        fill="#8A8A8A",
        font=font_ref
    )

    out_file = f"{OUT}/{matricula}_reimpresion.png"
    base.save(out_file)

    return out_file



