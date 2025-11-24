
from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime

app = Flask(__name__)

@app.route('/countdown')
def countdown():
    # Recebe a data final via query string
    end_date_str = request.args.get('end')
    if not end_date_str:
        return "Parâmetro 'end' é obrigatório. Exemplo: ?end=2025-12-31T23:59:59", 400

    try:
        end_date = datetime.fromisoformat(end_date_str)
    except ValueError:
        return "Formato inválido. Use: YYYY-MM-DDTHH:MM:SS", 400

    now = datetime.now()
    diff = end_date - now

    if diff.total_seconds() <= 0:
        text = "Oferta encerrada!"
    else:
        days = diff.days
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60
        seconds = diff.seconds % 60
        text = f"{days}d {hours}h {minutes}m {seconds}s"

    # Criar imagem
    img = Image.new('RGB', (400, 100), color=(30, 60, 120))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    draw.text((10, 40), text, font=font, fill=(255, 255, 255))

    # Retornar imagem
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
