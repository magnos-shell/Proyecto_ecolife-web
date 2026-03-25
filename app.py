import os
import json
import csv
from flask import Flask, render_template, request, redirect, url_for
# Importamos tu nueva carpeta de conexión
from Conexion.conexion import obtener_conexion

app = Flask(__name__)

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

# --- CONSULTA A MYSQL (Punto 4 de la tarea) ---
@app.route('/inventario')
def inventario():
    conexion = obtener_conexion()
    productos_db = []
    
    if conexion:
        cursor = conexion.cursor(dictionary=True) # Trae datos como diccionarios
        cursor.execute("SELECT * FROM productos")
        productos_db = cursor.fetchall()
        conexion.close()
        
    return render_template('inventario.html', productos=productos_db)

# --- OPERACIONES CRUD (Insertar, Eliminar, Modificar) ---

@app.route('/agregar_producto', methods=['POST'])
def agregar_producto():
    nombre = request.form['nombre']
    cantidad = int(request.form['cantidad'])
    precio = float(request.form['precio'])
    
    # 1. GUARDAR EN MYSQL
    conexion = obtener_conexion()
    if conexion:
        cursor = conexion.cursor()
        sql = "INSERT INTO productos (nombre, cantidad, precio) VALUES (%s, %s, %s)"
        cursor.execute(sql, (nombre, cantidad, precio))
        conexion.commit()
        nuevo_id = cursor.lastrowid # Obtenemos el ID generado
        conexion.close()

        # 2. MANTENER PERSISTENCIA EN ARCHIVOS (Opcional, pero recomendado)
        datos_dict = {"id": nuevo_id, "nombre": nombre, "cantidad": cantidad, "precio": precio}

        # Guardar en TXT
        with open('productos.txt', 'a', encoding='utf-8') as f:
            f.write(f"{nuevo_id}|{nombre}|{cantidad}|{precio}\n")

        # Guardar en JSON
        productos_lista = []
        if os.path.exists('productos.json'):
            with open('productos.json', 'r', encoding='utf-8') as f:
                try: productos_lista = json.load(f)
                except: productos_lista = []
        productos_lista.append(datos_dict)
        with open('productos.json', 'w', encoding='utf-8') as f:
            json.dump(productos_lista, f, indent=4)

    return redirect(url_for('inventario'))

# --- RUTA PARA ELIMINAR (Punto 4) ---
@app.route('/eliminar_producto/<int:id>')
def eliminar_producto(id):
    conexion = obtener_conexion()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM productos WHERE id = %s", (id,))
        conexion.commit()
        conexion.close()
    return redirect(url_for('inventario'))

# --- RUTA PARA LEER ARCHIVOS (Se mantiene igual) ---
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
    return render_template('mostrar_archivos.html', formato=formato.upper(), datos=datos)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)