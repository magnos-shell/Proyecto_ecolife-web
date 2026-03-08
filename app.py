import os
import json
import csv
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- CONFIGURACIÓN DE RUTAS Y BASE DE DATOS ---
# Basdir ayuda a localizar carpetas sin importar si es Windows o el servidor de Render
basedir = os.path.abspath(os.path.dirname(__file__))

# Configuración de SQLite (Base de Datos)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'ecolife.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODELO DE DATOS ---
class Producto(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Float, nullable=False)

# --- INICIALIZACIÓN ---
with app.app_context():
    # Creamos la carpeta instance si no existe
    instance_path = os.path.join(basedir, 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
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
        return f"<h1>¡Gracias {nombre}!</h1><p>Mensaje recibido.</p><a href='/'>Volver</a>"
    return render_template('contacto.html')

@app.route('/inventario')
def inventario():
    # 2.3 Leer datos de SQLite
    productos_db = Producto.query.all()
    return render_template('inventario.html', productos=productos_db)

# --- PERSISTENCIA MULTI-FORMATO (2.2) ---

@app.route('/agregar_producto', methods=['POST'])
def agregar_producto():
    nombre = request.form['nombre']
    cantidad = int(request.form['cantidad'])
    precio = float(request.form['precio'])
    
    # A. Guardar en SQLite
    nuevo_prod = Producto(nombre=nombre, cantidad=cantidad, precio=precio)
    db.session.add(nuevo_prod)
    db.session.commit()

    datos_dict = {"id": nuevo_prod.id, "nombre": nombre, "cantidad": cantidad, "precio": precio}

    # B. Persistencia en TXT
    with open('productos.txt', 'a', encoding='utf-8') as f:
        f.write(f"{nuevo_prod.id}|{nombre}|{cantidad}|{precio}\n")

    # C. Persistencia en JSON
    productos_lista = []
    if os.path.exists('productos.json'):
        with open('productos.json', 'r', encoding='utf-8') as f:
            try: productos_lista = json.load(f)
            except: productos_lista = []
    
    productos_lista.append(datos_dict)
    with open('productos.json', 'w', encoding='utf-8') as f:
        json.dump(productos_lista, f, indent=4)

    # D. Persistencia en CSV
    file_exists = os.path.isfile('productos.csv')
    with open('productos.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["id", "nombre", "cantidad", "precio"])
        if not file_exists: writer.writeheader()
        writer.writerow(datos_dict)

    return redirect(url_for('inventario'))

# --- RUTA PARA VISUALIZAR ARCHIVOS ---

@app.route('/leer/<formato>')
def leer_archivo(formato):
    datos = []
    formato = formato.lower()
    
    if formato == 'txt' and os.path.exists('productos.txt'):
        with open('productos.txt', 'r', encoding='utf-8') as f:
            datos = f.readlines()
    elif formato == 'json' and os.path.exists('productos.json'):
        with open('productos.json', 'r', encoding='utf-8') as f:
            datos = json.load(f)
    elif formato == 'csv' and os.path.exists('productos.csv'):
        with open('productos.csv', 'r', encoding='utf-8') as f:
            datos = list(csv.DictReader(f))
            
    return render_template('mostrar_archivos.html', formato=formato.upper(), datos=datos)

# --- INICIO DEL SERVIDOR (AJUSTADO PARA RENDER) ---
if __name__ == '__main__':
    # Render usa la variable de entorno PORT. Si no existe, usa el 5000.
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)