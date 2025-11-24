
# Projeto Countdown

Este repositório contém um contador regressivo para landing pages e e-mails.

## Estrutura do Projeto
o ProjetoMostrar mais linhas
countdown_email/
├── app.py
├── requirements.txt

## Código principal (`app.py`)
```python
from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime

app = Flask(__name__)

@app.route('/countdown')
def countdown():
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

    img = Image.new('RGB', (400, 100), color=(30, 60, 120))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    draw.text((10, 40), text, font=font, fill=(255, 255, 255))

    buf = io.BytesIO()
    img.save(buf, format='PNG')
