import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash, make_response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from Conexion.conexion import obtener_conexion
from fpdf import FPDF  # <--- NUEVA IMPORTACIÓN PARA EL PDF

# --- IMPORTACIONES DEL MODELO ANTIGUO (USUARIOS) ---
from models.modelo_usuario import Usuario

# --- NUEVAS IMPORTACIONES DE LA ARQUITECTURA POR CAPAS (PRODUCTOS) ---
from services.producto_service import ProductoService
from forms.producto_form import ProductoForm

app = Flask(__name__)
app.secret_key = 'clave_secreta_ecolife' # Necesario para las sesiones y los mensajes flash

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
                flash('Registro exitoso. ¡Inicia sesión!', 'info')
                return redirect(url_for('login'))
            except:
                flash('El correo ya está registrado.', 'warning')
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
            flash('Email o contraseña incorrectos.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


# =====================================================================
# --- RUTAS PROTEGIDAS Y CRUD DE PRODUCTOS (ARQUITECTURA POR CAPAS) ---
# =====================================================================

@app.route('/inventario')
@login_required
def inventario():
    # El controlador solo pide los datos al Servicio. Mucho más limpio.
    productos_db = ProductoService.get_all()
    return render_template('inventario.html', productos=productos_db)

@app.route('/producto/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_producto():
    form = ProductoForm()
    if form.validate_on_submit():
        # Si el formulario es válido, el servicio guarda en MySQL
        ProductoService.create(form.nombre.data, form.cantidad.data, form.precio.data)
        flash('Producto agregado exitosamente.', 'success')
        return redirect(url_for('inventario'))
    
    return render_template('productos/formulario.html', form=form, accion="Añadir")

@app.route('/producto/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_producto(id):
    producto = ProductoService.get_by_id(id)
    if not producto:
        flash('El producto no existe.', 'danger')
        return redirect(url_for('inventario'))

    form = ProductoForm()
    
    if form.validate_on_submit():
        # Actualizar en la base de datos usando el Servicio
        ProductoService.update(id, form.nombre.data, form.cantidad.data, form.precio.data)
        flash('Producto actualizado correctamente.', 'success')
        return redirect(url_for('inventario'))
    
    # Pre-cargar los datos actuales en el formulario (solo cuando la página carga por primera vez)
    if request.method == 'GET':
        form.nombre.data = producto.nombre
        form.cantidad.data = producto.cantidad
        form.precio.data = producto.precio

    return render_template('productos/formulario.html', form=form, accion="Editar")

@app.route('/producto/eliminar/<int:id>')
@login_required
def eliminar_producto(id):
    ProductoService.delete(id)
    flash('Producto eliminado del sistema.', 'info')
    return redirect(url_for('inventario'))


# =====================================================================
# --- GENERACIÓN DE REPORTE PDF (Punto 6 de la tarea) ---
# =====================================================================

@app.route('/reporte/pdf')
@login_required
def generar_pdf():
    # 1. Obtener los datos desde el Servicio
    productos = ProductoService.get_all()

    # 2. Crear el documento PDF
    pdf = FPDF()
    pdf.add_page()
    
    # 3. Título del Reporte
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt="Reporte de Inventario - EcoLife", ln=True, align='C')
    pdf.ln(10) # Salto de línea

    # 4. Encabezados de la tabla
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(20, 10, 'ID', 1, 0, 'C')
    pdf.cell(90, 10, 'Nombre del Producto', 1, 0, 'C')
    pdf.cell(40, 10, 'Stock', 1, 0, 'C')
    pdf.cell(40, 10, 'Precio', 1, 1, 'C')

    # 5. Llenar la tabla con los datos de MySQL
    pdf.set_font("Arial", '', 12)
    for p in productos:
        pdf.cell(20, 10, str(p.id), 1, 0, 'C')
        # Manejar caracteres especiales en nombres
        nombre_limpio = p.nombre.encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(90, 10, nombre_limpio, 1, 0, 'L')
        pdf.cell(40, 10, str(p.cantidad), 1, 0, 'C')
        pdf.cell(40, 10, f"${p.precio:.2f}", 1, 1, 'C')

    # 6. Preparar la descarga
    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    response = make_response(pdf_bytes)
    response.headers.set('Content-Disposition', 'attachment', filename='Reporte_EcoLife.pdf')
    response.headers.set('Content-Type', 'application/pdf')
    
    return response

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)