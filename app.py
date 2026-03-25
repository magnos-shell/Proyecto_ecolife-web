import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from Conexion.conexion import obtener_conexion
from models import Usuario  # Asegúrate de haber creado models.py

app = Flask(__name__)
app.secret_key = 'clave_secreta_ecolife' # Necesario para las sesiones

# --- CONFIGURACIÓN DE FLASK-LOGIN ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # A donde redirigir si no hay sesión

@login_manager.user_loader
def load_user(user_id):
    return Usuario.get_by_id(user_id)

# --- RUTAS DE NAVEGACIÓN PÚBLICAS ---

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

# --- RUTAS DE AUTENTICACIÓN ---

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']
        pw_hash = generate_password_hash(password) # Encriptar contraseña
        
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            try:
                cursor.execute("INSERT INTO usuarios (nombre, email, password) VALUES (%s, %s, %s)", 
                               (nombre, email, pw_hash))
                conexion.commit()
                flash('Registro exitoso. ¡Inicia sesión!')
                return redirect(url_for('login'))
            except:
                flash('El correo ya está registrado.')
            finally:
                conexion.close()
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = Usuario.get_by_email(email)
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('inventario'))
        else:
            flash('Email o contraseña incorrectos.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# --- RUTAS PROTEGIDAS (Requieren Login) ---

@app.route('/inventario')
@login_required # <--- Solo usuarios registrados pueden entrar
def inventario():
    conexion = obtener_conexion()
    productos_db = []
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM productos")
        productos_db = cursor.fetchall()
        conexion.close()
    return render_template('inventario.html', productos=productos_db)

@app.route('/agregar_producto', methods=['POST'])
@login_required
def agregar_producto():
    nombre = request.form['nombre']
    cantidad = int(request.form['cantidad'])
    precio = float(request.form['precio'])
    
    conexion = obtener_conexion()
    if conexion:
        cursor = conexion.cursor()
        sql = "INSERT INTO productos (nombre, cantidad, precio) VALUES (%s, %s, %s)"
        cursor.execute(sql, (nombre, cantidad, precio))
        conexion.commit()
        conexion.close()
    return redirect(url_for('inventario'))

@app.route('/eliminar_producto/<int:id>')
@login_required
def eliminar_producto(id):
    conexion = obtener_conexion()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM productos WHERE id = %s", (id,))
        conexion.commit()
        conexion.close()
    return redirect(url_for('inventario'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)