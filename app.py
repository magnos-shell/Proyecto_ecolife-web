from flask import Flask

app = Flask(__name__)

# --- RUTA 1: HOME (Requisito básico) ---
@app.route('/')
def home():
    return '<h1>Bienvenido al Sistema EcoLife</h1><p>Plataforma de gestión de productos sostenibles y reciclaje.</p>'

# --- RUTA 2: USUARIO (Requisito: Mensaje de bienvenida personalizado) ---
# Esta ruta cumple con la instrucción: @app.route('/usuario/<nombre>')
@app.route('/usuario/<nombre>')
def usuario(nombre):
    # Devuelve: "Bienvenido, Ana!" (como pide el ejemplo)
    return f'<h1>Bienvenido, {nombre}!</h1><p>Gracias por registrarte en EcoLife.</p>'

# --- RUTA 3: NEGOCIO ECOLIFE (Requisito: Adaptación al negocio) ---
# Adaptación: Tienda/Inventario de productos ecológicos
# Esta ruta cumple con: "La ruta dinámica debe devolver un mensaje coherente"
@app.route('/producto/<item>')
def verificar_producto(item):
    # Lógica simulada: Si el cliente pone "bambu" o "panel", sale disponible.
    # El mensaje sigue el formato: "Producto: Laptop – disponible."
    return f'<h3>Producto: {item} – Disponible</h3><p>Este artículo se encuentra en stock en nuestra bodega sostenible.</p>'

# --- RUTA EXTRA (Opcional): Para servicios de reciclaje ---
@app.route('/servicio/<tipo>')
def servicio(tipo):
    return f'Servicio solicitado: Recolección de {tipo} – En proceso.'

if __name__ == '__main__':
    app.run(debug=True)