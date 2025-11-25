from flask import Flask, send_from_directory
import os

app = Flask(__name__)

# Rota principal para servir o HTML
@app.route("/")
def home():
    return send_from_directory(os.path.dirname(__file__), "index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

