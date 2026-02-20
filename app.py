import os
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuración Base de Datos
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///ecolife.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- RUTAS ---

@app.route('/')
def home():
    return render_template('index.html')

# NUEVA RUTA: Acerca de
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/productos')
def productos():
    lista_productos = [
        {"nombre": "Cepillo de Bambú", "precio": 3.50, "descripcion": "Biodegradable y libre de plástico."},
        {"nombre": "Botella Térmica", "precio": 15.00, "descripcion": "Mantiene el frío por 24 horas."},
        {"nombre": "Bolsa de Tela", "precio": 2.00, "descripcion": "Algodón orgánico reutilizable."},
        {"nombre": "Kit Solar", "precio": 45.00, "descripcion": "Cargador solar portátil para móviles."}
    ]
    return render_template('productos.html', productos=lista_productos)

@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        mensaje = request.form['mensaje']
        print(f"Nuevo mensaje de {nombre} ({email}): {mensaje}")
        return f"<h1>¡Gracias {nombre}!</h1><p>Hemos recibido tu mensaje correctamente.</p><a href='/'>Volver al inicio</a>"
    return render_template('contacto.html')

@app.route('/usuario/<nombre>')
def usuario(nombre):
    return f'<h1>Bienvenido, {nombre}!</h1>'

if __name__ == '__main__':
    app.run(debug=True)