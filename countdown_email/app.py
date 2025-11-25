
from flask import Flask, request, send_file, send_from_directory, make_response
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime
import pytz
import os

app = Flask(__name__)

# ---------- Utilidades ----------
def load_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    """
    Carrega uma fonte TrueType segura. Tenta vários caminhos comuns em
    ambientes Linux/Render e faz fallback para ImageFont.load_default()
    se nada for encontrado.
    """
    candidates = [
        "arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
    ]
    for path in candidates:
        try:
            if os.path.exists(path) or path.endswith(".ttf"):
                return ImageFont.truetype(path, size)
        except OSError:
            continue
    # Fallback seguro
    return ImageFont.load_default()

def parse_end_iso(end_str: str, tz):
    """
    Aceita 'YYYY-MM-DDTHH:MM' ou 'YYYY-MM-DDTHH:MM:SS' (com/sem timezone).
    Se faltar segundos, adiciona ':00'. Converte para timezone America/Sao_Paulo.
    """
    if not end_str:
        raise ValueError("Parâmetro 'end' ausente")
    # adiciona segundos se vier sem
    if len(end_str) == 16:  # YYYY-MM-DDTHH:MM
        end_str = end_str + ":00"
    # fromisoformat aceita offset; cuidamos de tz
    dt = datetime.fromisoformat(end_str)
    if dt.tzinfo is None:
        dt = tz.localize(dt)
    else:
        dt = dt.astimezone(tz)
    return dt

def measure(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont):
    """
    Mede texto com textbbox quando disponível (mais preciso).
    """
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        return w, h
    except Exception:
        # Fallback para versões antigas
        return draw.textsize(text, font=font)

@app.route("/")
def home():
    # Servir o gerador
    return send_from_directory(os.path.dirname(__file__), "index.html")

@app.route("/countdown-image")
def countdown_image():
    # --- Parâmetros obrigatórios e opcionais ---
    end_date_str = request.args.get("end")
    bg_color  = request.args.get("bg", "#000000")
    digit_color = request.args.get("digit", "#FFFFFF")
    box_color   = request.args.get("box", "#1E1E1E")

    # --- Dimensões fixas (igual Sendtric) ---
    largura, altura = 900, 250

    # --- Timezone ---
    tz = pytz.timezone("America/Sao_Paulo")
    now = datetime.now(tz)

    # --- Parse seguro da data ---
    try:
        end_date = parse_end_iso(end_date_str, tz)
    except Exception:
        return ("Formato inválido. Use: YYYY-MM-DDTHH:MM ou YYYY-MM-DDTHH:MM:SS", 400)

    # --- Cálculo do tempo restante (corrigido para negativos) ---
    total_seconds = int((end_date - now).total_seconds())
    if total_seconds <= 0:
        dias = horas = minutos = segundos = 0
    else:
        dias = total_seconds // 86400
        rem = total_seconds % 86400
        horas = rem // 3600
        rem = rem % 3600
        minutos = rem // 60
        segundos = rem % 60

    # --- Carregar fontes com fallback ---
    fonte_num   = load_font(80, bold=True)
    fonte_label = load_font(28, bold=True)

    # --- Criar imagem ---
    img = Image.new("RGB", (largura, altura), color=bg_color)
    draw = ImageDraw.Draw(img)

    valores = [dias, horas, minutos, segundos]
    labels  = ["DIAS", "HORAS", "MINUTOS", "SEGUNDOS"]
    bloco_largura = largura // 4

    # Desenho dos blocos
    for i, valor in enumerate(valores):
        x_center = i * bloco_largura + bloco_largura // 2
        box_width = bloco_largura - 40
        box_height = 150
        box_x0 = x_center - box_width // 2
        box_y0 = 40
        box_x1 = box_x0 + box_width
        box_y1 = box_y0 + box_height

        # Caixa com canto arredondado (fallback para rectangle em Pillow antigo)
        if hasattr(draw, "rounded_rectangle"):
            draw.rounded_rectangle([box_x0, box_y0, box_x1, box_y1], radius=20, fill=box_color)
        else:
            draw.rectangle([box_x0, box_y0, box_x1, box_y1], fill=box_color)

        # Número centralizado
        num_text = str(valor).zfill(2)
        num_w, num_h = measure(draw, num_text, fonte_num)
        num_x = x_center - num_w // 2
        # Centralizar verticalmente dentro da caixa (um pouco acima do label)
        num_y = box_y0 + 30
        draw.text((num_x, num_y), num_text, font=fonte_num, fill=digit_color)

        # Label centralizada no rodapé da caixa
        label_text = labels[i]
        label_w, label_h = measure(draw, label_text, fonte_label)
        label_x = x_center - label_w // 2
        label_y = box_y1 - label_h - 10
        draw.text((label_x, label_y), label_text, font=fonte_label, fill=digit_color)

    # --- Buffer e resposta com cabeçalhos anti-cache (e-mail tende a cachear) ---
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    buf.seek(0)

    resp = make_response(send_file(buf, mimetype="image/png"))
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp

if __name__ == "__main__":
    # Em ambientes locais
