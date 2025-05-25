from flask import Flask, render_template, send_from_directory
import os
import json

sample = Flask(__name__)
sample.config["UPLOAD_FOLDER"] = "autorizados"

@sample.route('/')
def index():
    nombre = None
    imagen = None

    if os.path.exists("ultimo_acceso.json"):
        with open("ultimo_acceso.json", "r") as f:
            datos = json.load(f)
            nombre = datos.get("nombre")
            imagen = datos.get("imagen")

    return render_template('index.html', nombre=nombre, imagen=imagen)

@sample.route('/autorizados/<path:filename>')
def autorizados(filename):
    return send_from_directory(sample.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    sample.run(host="0.0.0.0", port=8080)
