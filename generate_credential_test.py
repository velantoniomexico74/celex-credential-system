import sqlite3
from PIL import Image, ImageDraw, ImageFont
import os

# ===============================
# CONFIGURACIÓN
# ===============================
DB = "celex.db"
FOTOS = "fotos"
LAYOUT = "layouts/CredencialCELEXFinal.png"
OUT = "credenciales"
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

os.makedirs(OUT, exist_ok=True)

# ===============================
# CONEXIÓN A BASE DE DATOS
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
LIMIT 1
""")

row = cur.fetchone()

if not row:
    print("No se encontró ningún alumno")
    exit(1)

ap, am, nom, matricula, nivel, turno, no_foto = row

# ===============================
# FOTO
# ===============================
foto_path = f"{FOTOS}/{no_foto}.jpg"
if not os.path.exists(foto_path):
    print(f"Foto no encontrada: {foto_path}")
    exit(1)

# ===============================
# LAYOUT BASE
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
# PROCESAR FOTO
# ===============================
foto = Image.open(foto_path)
foto = foto.rotate(-90, expand=True)
foto = foto.resize((260, 330))

# Posición final de la foto (YA AJUSTADA)
base.paste(foto, (170, 304))

# ===============================
# TEXTO
# ===============================
CARD_WIDTH = base.width

def draw_centered_text(draw, y, text, font, fill="#4A4A4A"):
    text_width = draw.textlength(text, font=font)
    x = (CARD_WIDTH - text_width) // 2
    draw.text((x, y), text, fill=fill, font=font)

nombre = nom.upper()
apellidos = f"{ap} {am}".upper()

# Coordenadas verticales (ajustables finamente)
y_nombre = 670
y_apellidos = 710
y_matricula = 760

draw_centered_text(draw, y_nombre, nombre, font_nombre)
draw_centered_text(draw, y_apellidos, apellidos, font_apellidos)
draw_centered_text(draw, y_matricula, f"MATRÍCULA: {matricula}", font_datos)
font_ref = ImageFont.truetype(FONT_PATH, 11)

# ===============================
# ETIQUETA DE REFERENCIA (NO_FOTO)
# ===============================
ref_text = f"Foto ID: {no_foto}"

# Coordenadas sugeridas (ajústalas si quieres)
ref_x = base.width - 140   # esquina inferior derecha
ref_y = base.height - 14

draw.text(
    (ref_x, ref_y),
    ref_text,
    fill="#8A8A8A",
    font=font_ref
)



# ===============================
# GUARDAR
# ===============================
out_file = f"{OUT}/TEST_{matricula}.png"
base.save(out_file)

print(f"✔ Credencial generada: {out_file}")
