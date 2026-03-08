import os
import json
import csv
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- CONFIGURACIÓN DE RUTAS Y BASE DE DATOS (2.3) ---
# Usamos ruta absoluta para evitar errores de "unable to open database file" en Windows
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'ecolife.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODELO DE DATOS (2.4) ---
class Producto(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Float, nullable=False)

# --- INICIALIZACIÓN DE CARPETAS Y TABLAS ---
with app.app_context():
    # Asegura que la carpeta 'instance' exista para la base de datos
    if not os.path.exists(os.path.join(basedir, 'instance')):
        os.makedirs(os.path.join(basedir, 'instance'))
    db.create_all()

# --- RUTAS DE NAVEGACIÓN ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        # Aquí puedes procesar el mensaje del formulario de contacto
        return f"<h1>¡Gracias {nombre}!</h1><p>Hemos recibido tu mensaje.</p><a href='/'>Volver al inicio</a>"
    return render_template('contacto.html')

@app.route('/inventario')
def inventario():
    # Leer datos de SQLite para mostrarlos en la tabla (2.3)
    productos_db = Producto.query.all()
    return render_template('inventario.html', productos=productos_db)

# --- PERSISTENCIA MULTI-FORMATO (2.2) ---

@app.route('/agregar_producto', methods=['POST'])
def agregar_producto():
    nombre = request.form['nombre']
    cantidad = int(request.form['cantidad'])
    precio = float(request.form['precio'])
    
    # 1. Guardar en SQLite (SQLAlchemy)
    nuevo_prod = Producto(nombre=nombre, cantidad=cantidad, precio=precio)
    db.session.add(nuevo_prod)
    db.session.commit()

    # Preparar datos para archivos físicos
    datos_dict = {
        "id": nuevo_prod.id,
        "nombre": nombre,
        "cantidad": cantidad,
        "precio": precio
    }

    # 2. Persistencia en TXT (usando open() en modo append 'a')
    with open('productos.txt', 'a', encoding='utf-8') as f:
        f.write(f"{nuevo_prod.id}|{nombre}|{cantidad}|{precio}\n")

    # 3. Persistencia en JSON (librería json)
    productos_lista = []
    if os.path.exists('productos.json'):
        with open('productos.json', 'r', encoding='utf-8') as f:
            try:
                productos_lista = json.load(f)
            except json.JSONDecodeError:
                productos_lista = []
    
    productos_lista.append(datos_dict)
    with open('productos.json', 'w', encoding='utf-8') as f:
        json.dump(productos_lista, f, indent=4)

    # 4. Persistencia en CSV (librería csv)
    archivo_existe = os.path.isfile('productos.csv')
    with open('productos.csv', 'a', newline='', encoding='utf-8') as f:
        campos = ["id", "nombre", "cantidad", "precio"]
        writer = csv.DictWriter(f, fieldnames=campos)
        if not archivo_existe:
            writer.writeheader()
        writer.writerow(datos_dict)

    return redirect(url_for('inventario'))

# --- LECTURA DE ARCHIVOS (2.2) ---

@app.route('/leer/<formato>')
def leer_archivo(formato):
    datos = []
    formato = formato.lower()
    
    if formato == 'txt' and os.path.exists('productos.txt'):
        with open('productos.txt', 'r', encoding='utf-8') as f:
            datos = f.readlines()
            
    elif formato == 'json' and os.path.exists('productos.json'):
        with open('productos.json', 'r', encoding='utf-8') as f:
            try:
                datos = json.load(f)
            except:
                datos = []
                
    elif formato == 'csv' and os.path.exists('productos.csv'):
        with open('productos.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            datos = list(reader)
            
    return render_template('mostrar_archivos.html', formato=formato.upper(), datos=datos)

if __name__ == '__main__':
    app.run(debug=True)