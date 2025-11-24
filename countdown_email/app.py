from flask import Flask, request, send_file, send_from_directory
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime
import pytz
import os

app = Flask(__name__)

# Servir HTML na rota raiz
@app.route("/")
def home():
    return send_from_directory(os.getcwd(), "index.html")

@app.route("/countdown")
def countdown():
    # Parâmetro obrigatório: data final
    end_date_str = request.args.get("end")
    if not end_date_str:
        return "Parâmetro 'end' é obrigatório. Exemplo: ?end=2025-12-31T23:59:59", 400

    # Fuso horário fixo America/Sao_Paulo
    tz = pytz.timezone("America/Sao_Paulo")
    now = datetime.now(tz)

    try:
        # Converter data final para timezone correto
        end_date = datetime.fromisoformat(end_date_str)
        if end_date.tzinfo is None:
            end_date = tz.localize(end_date)
        else:
            end_date = end_date.astimezone(tz)
    except ValueError:
        return "Formato inválido. Use: YYYY-MM-DDTHH:MM:SS", 400

    diff = end_date - now

    # Validação do limite (30 dias)
    if diff.days > 30:
        return "O limite máximo é 30 dias.", 400

    # Texto do contador em português
    if diff.total_seconds() <= 0:
        text = "Oferta encerrada!"
    else:
        dias = diff.days
        horas = diff.seconds // 3600
        minutos = (diff.seconds % 3600) // 60
        segundos = diff.seconds % 60
        text = f"{dias} dias {horas} horas {minutos} minutos {segundos} segundos"

    # Cores dinâmicas via query string
    bg_color = request.args.get("bg", "#1E3C78")
    digit_color = request.args.get("digit", "#FFD700")

    # Criar imagem
    img = Image.new("RGB", (500, 120), color=bg_color)
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    # Desenhar texto
    draw.text((10, 50), text, font=font, fill=digit_color)

    # Retornar imagem como PNG
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")
