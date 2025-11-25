
from flask import Flask, request, send_file, send_from_directory
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime
import pytz
import os

app = Flask(__name__)

@app.route("/")
def home():
    return send_from_directory(os.path.dirname(__file__), "index.html")

@app.route("/countdown-image")
def countdown_image():
    end_date_str = request.args.get("end")
    if not end_date_str:
        return "Parâmetro 'end' é obrigatório. Exemplo: ?end=2025-12-31T23:59:59", 400

    tz = pytz.timezone("America/Sao_Paulo")
    now = datetime.now(tz)

    try:
        end_date = datetime.fromisoformat(end_date_str)
        if end_date.tzinfo is None:
            end_date = tz.localize(end_date)
        else:
            end_date = end_date.astimezone(tz)
    except ValueError:
        return "Formato inválido. Use: YYYY-MM-DDTHH:MM:SS", 400

    diff = end_date - now
    dias = max(diff.days, 0)
    horas = max(diff.seconds // 3600, 0)
    minutos = max((diff.seconds % 3600) // 60, 0)
    segundos = max(diff.seconds % 60, 0)

    largura, altura = 900, 250
    bg_color = request.args.get("bg", "#000000")
    digit_color = request.args.get("digit", "#FFFFFF")
    box_color = "#1E1E1E"

    fonte_num = ImageFont.load_default()
    fonte_label = ImageFont.load_default()

    img = Image.new("RGB", (largura, altura), color=bg_color)
    draw = ImageDraw.Draw(img)

    valores = [dias, horas, minutos, segundos]
    labels = ["DIAS", "HORAS", "MINUTOS", "SEGUNDOS"]
    bloco_largura = largura // 4

    for i, valor in enumerate(valores):
        x = i * bloco_largura + bloco_largura // 2
        box_width = bloco_largura - 40
        box_height = 150
        box_x0 = x - box_width // 2
        box_y0 = 40
        box_x1 = box_x0 + box_width
        box_y1 = box_y0 + box_height
        draw.rounded_rectangle([box_x0, box_y0, box_x1, box_y1], radius=20, fill=box_color)
        draw.text((x - 20, 80), str(valor).zfill(2), font=fonte_num, fill=digit_color)
        draw.text((x - 30, 150), labels[i], font=fonte_label, fill=digit_color)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
