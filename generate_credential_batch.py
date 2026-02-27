import sqlite3
from PIL import Image, ImageDraw, ImageFont, ImageOps
import os
from datetime import datetime

DB = "celex.db"
FOTOS = "fotos"
LAYOUT = "layouts/CredencialCELEXFinal.png"
OUT = "credenciales"
LOG_FILE = os.path.join(OUT, "errores_credenciales.log")
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

os.makedirs(OUT, exist_ok=True)


def log_error(matricula, nombre, motivo):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {matricula} | {nombre} | {motivo}\n")


def generar_credenciales():

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
        SELECT apellido_paterno,
               apellido_materno,
               nombres,
               matricula,
               no_foto
        FROM alumnos
    """)

    rows = cur.fetchall()
    conn.close()

    for ap, am, nom, matricula, no_foto in rows:

        nombre_completo = f"{nom} {ap} {am}".upper()
        foto_path = f"{FOTOS}/{no_foto}.jpg"

        if not os.path.exists(foto_path):
            log_error(matricula, nombre_completo, "Foto no encontrada")
            continue

        try:
            base = Image.open(LAYOUT).convert("RGB")
            draw = ImageDraw.Draw(base)

            font_nombre = ImageFont.truetype(FONT_PATH, 34)
            font_apellidos = ImageFont.truetype(FONT_PATH, 32)
            font_datos = ImageFont.truetype(FONT_PATH, 26)

            foto = Image.open(foto_path)
            foto = ImageOps.exif_transpose(foto)
            foto = foto.resize((260, 330))
            base.paste(foto, (170, 304))

            CARD_WIDTH = base.width

            def draw_centered(y, text, font):
                w = draw.textlength(text, font=font)
                x = (CARD_WIDTH - w) // 2
                draw.text((x, y), text, fill="#4A4A4A", font=font)

            draw_centered(670, nom.upper(), font_nombre)
            draw_centered(710, f"{ap} {am}".upper(), font_apellidos)
            draw_centered(760, f"MATRÍCULA: {matricula}", font_datos)

            base.save(f"{OUT}/{matricula}.png")

        except Exception as e:
            log_error(matricula, nombre_completo, str(e))
