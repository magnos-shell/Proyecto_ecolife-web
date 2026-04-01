import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash, make_response, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from Conexion.conexion import obtener_conexion
from fpdf import FPDF

# --- IMPORTACIONES DE MODELOS Y SERVICIOS ---
from models.modelo_usuario import Usuario
from services.producto_service import ProductoService
from services.cliente_service import ClienteService
from forms.producto_form import ProductoForm

app = Flask(__name__)
app.secret_key = 'clave_secreta_ecolife'

# --- CONFIGURACIÓN DE FLASK-LOGIN ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

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
        pw_hash = generate_password_hash(password)
        
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
# --- GESTIÓN DE CLIENTES (ADAPTADO A TU DB) ---
# =====================================================================

@app.route('/clientes')
@login_required
def lista_clientes():
    clientes = ClienteService.get_all()
    return render_template('clientes/lista.html', clientes=clientes)

@app.route('/cliente/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_cliente():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        # Adaptado: Recibimos 'email' desde el formulario para tu columna 'email'
        email = request.form.get('email') 
        telefono = request.form.get('telefono')
        
        ClienteService.create(nombre, email, telefono)
        flash('Cliente registrado exitosamente.', 'success')
        return redirect(url_for('lista_clientes'))
    return render_template('clientes/formulario.html')


# =====================================================================
# --- CRUD DE PRODUCTOS ---
# =====================================================================

@app.route('/inventario')
@login_required
def inventario():
    productos_db = ProductoService.get_all()
    return render_template('inventario.html', productos=productos_db)

@app.route('/producto/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_producto():
    form = ProductoForm()
    if form.validate_on_submit():
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
        ProductoService.update(id, form.nombre.data, form.cantidad.data, form.precio.data)
        flash('Producto actualizado correctamente.', 'success')
        return redirect(url_for('inventario'))
    
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
# --- CARRITO DE COMPRAS Y VENTAS ---
# =====================================================================

@app.route('/carrito/agregar/<int:id>')
@login_required
def agregar_al_carrito(id):
    producto = ProductoService.get_by_id(id)
    if not producto:
        flash('Producto no encontrado.', 'danger')
        return redirect(url_for('inventario'))

    if 'carrito' not in session:
        session['carrito'] = {}

    carrito = session['carrito']
    id_str = str(id)

    if id_str in carrito:
        carrito[id_str]['cantidad'] += 1
    else:
        carrito[id_str] = {
            'nombre': producto.nombre,
            'precio': float(producto.precio),
            'cantidad': 1
        }
    
    session.modified = True
    flash(f'{producto.nombre} añadido al carrito.', 'success')
    return redirect(url_for('inventario'))

@app.route('/carrito')
@login_required
def ver_carrito():
    carrito = session.get('carrito', {})
    total = sum(item['precio'] * item['cantidad'] for item in carrito.values())
    clientes = ClienteService.get_all()
    return render_template('carrito.html', carrito=carrito, total=total, clientes=clientes)

@app.route('/carrito/eliminar/<id>')
@login_required
def eliminar_del_carrito(id):
    if 'carrito' in session and id in session['carrito']:
        session['carrito'].pop(id)
        session.modified = True
    return redirect(url_for('ver_carrito'))

@app.route('/carrito/finalizar', methods=['POST'])
@login_required
def finalizar_venta():
    cliente_id = request.form.get('cliente_id')
    carrito = session.get('carrito', {})
    
    if not carrito or not cliente_id:
        flash('Error al procesar la venta: falta cliente o productos.', 'warning')
        return redirect(url_for('ver_carrito'))

    try:
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            
            # 1. Registrar Cabecera de Venta
            total_venta = sum(item['precio'] * item['cantidad'] for item in carrito.values())
            cursor.execute("INSERT INTO ventas (cliente_id, total) VALUES (%s, %s)", (cliente_id, total_venta))
            venta_id = cursor.lastrowid

            # 2. Registrar Detalle y Actualizar Stock
            for prod_id, item in carrito.items():
                # Insertar detalle
                cursor.execute("""
                    INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario) 
                    VALUES (%s, %s, %s, %s)
                """, (venta_id, prod_id, item['cantidad'], item['precio']))

                # Restar stock
                cursor.execute("UPDATE productos SET cantidad = cantidad - %s WHERE id = %s", 
                               (item['cantidad'], prod_id))

            conexion.commit()
            conexion.close()
            
            session.pop('carrito', None)
            flash('Venta registrada con éxito y stock actualizado.', 'success')
            return redirect(url_for('inventario'))

    except Exception as e:
        flash(f'Error en la base de datos: {str(e)}', 'danger')
        return redirect(url_for('ver_carrito'))

    return redirect(url_for('inventario'))


# =====================================================================
# --- REPORTES ---
# =====================================================================

@app.route('/reporte/pdf')
@login_required
def generar_pdf():
    productos = ProductoService.get_all()
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt="Reporte de Inventario - EcoLife", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(20, 10, 'ID', 1, 0, 'C')
    pdf.cell(90, 10, 'Nombre del Producto', 1, 0, 'C')
    pdf.cell(40, 10, 'Stock', 1, 0, 'C')
    pdf.cell(40, 10, 'Precio', 1, 1, 'C')

    pdf.set_font("Arial", '', 12)
    for p in productos:
        pdf.cell(20, 10, str(p.id), 1, 0, 'C')
        nombre_limpio = p.nombre.encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(90, 10, nombre_limpio, 1, 0, 'L')
        pdf.cell(40, 10, str(p.cantidad), 1, 0, 'C')
        pdf.cell(40, 10, f"${p.precio:.2f}", 1, 1, 'C')

    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    response = make_response(pdf_bytes)
    response.headers.set('Content-Disposition', 'attachment', filename='Reporte_EcoLife.pdf')
    response.headers.set('Content-Type', 'application/pdf')
    return response

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)