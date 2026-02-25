import sqlite3
import os

class Producto:
    """Clase que representa un producto ecológico en el inventario."""
    def __init__(self, id_prod, nombre, cantidad, precio):
        self._id_prod = id_prod
        self._nombre = nombre
        self._cantidad = cantidad
        self._precio = precio

    # Getters
    @property
    def id_prod(self): return self._id_prod
    
    @property
    def nombre(self): return self._nombre
    
    @property
    def cantidad(self): return self._cantidad
    
    @property
    def precio(self): return self._precio

    # Setters con validación
    @cantidad.setter
    def cantidad(self, nueva_cantidad):
        if nueva_cantidad >= 0:
            self._cantidad = nueva_cantidad
        else:
            print("❌ Error: La cantidad no puede ser negativa.")

    @precio.setter
    def precio(self, nuevo_precio):
        if nuevo_precio >= 0:
            self._precio = nuevo_precio
        else:
            print("❌ Error: El precio no puede ser negativo.")

    def __str__(self):
        return f"ID: {self.id_prod} | Producto: {self.nombre} | Stock: {self.cantidad} | Precio: ${self.precio:.2f}"


class Inventario:
    """Clase que gestiona la colección de productos y la conexión a SQLite."""
    def __init__(self, db_name="instance/ecolife_inventory.db"):
        self.db_name = db_name
        self.productos = {}  # Colección: Diccionario para búsquedas O(1) por ID
        
        # Aseguramos que la carpeta 'instance' exista antes de crear la DB
        os.makedirs(os.path.dirname(self.db_name), exist_ok=True)
        
        self._inicializar_db()
        self._cargar_desde_db()

    def _inicializar_db(self):
        """Crea la base de datos y las tablas (productos y clientes) si no existen."""
        conexion = sqlite3.connect(self.db_name)
        cursor = conexion.cursor()
        
        # Tabla de Productos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                cantidad INTEGER NOT NULL,
                precio REAL NOT NULL
            )
        ''')

        # Tabla de Clientes (Agregada para cumplir con el requisito de múltiples tablas)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                telefono TEXT
            )
        ''')
        
        conexion.commit()
        conexion.close()

    def _cargar_desde_db(self):
        """Carga los productos de SQLite al diccionario en memoria."""
        conexion = sqlite3.connect(self.db_name)
        cursor = conexion.cursor()
        cursor.execute('SELECT id, nombre, cantidad, precio FROM productos')
        filas = cursor.fetchall()
        for fila in filas:
            prod = Producto(fila[0], fila[1], fila[2], fila[3])
            self.productos[prod.id_prod] = prod
        conexion.close()

    def anadir_producto(self, producto):
        if producto.id_prod in self.productos:
            print(f"⚠️ El producto con ID {producto.id_prod} ya existe.")
            return

        # Guardar en DB SQLite
        conexion = sqlite3.connect(self.db_name)
        cursor = conexion.cursor()
        try:
            cursor.execute('INSERT INTO productos (id, nombre, cantidad, precio) VALUES (?, ?, ?, ?)',
                           (producto.id_prod, producto.nombre, producto.cantidad, producto.precio))
            conexion.commit()
            
            # Guardar en memoria (Diccionario)
            self.productos[producto.id_prod] = producto
            print("✅ Producto ecológico añadido con éxito.")
        except sqlite3.IntegrityError:
            print("⚠️ Error de integridad en la base de datos.")
        finally:
            conexion.close()

    def eliminar_producto(self, id_prod):
        if id_prod in self.productos:
            # Eliminar de DB SQLite
            conexion = sqlite3.connect(self.db_name)
            cursor = conexion.cursor()
            cursor.execute('DELETE FROM productos WHERE id = ?', (id_prod,))
            conexion.commit()
            conexion.close()
            
            # Eliminar de memoria
            del self.productos[id_prod]
            print("✅ Producto eliminado del inventario.")
        else:
            print("❌ Producto no encontrado en el sistema.")

    def actualizar_producto(self, id_prod, nueva_cantidad=None, nuevo_precio=None):
        if id_prod in self.productos:
            prod = self.productos[id_prod]
            
            if nueva_cantidad is not None:
                prod.cantidad = nueva_cantidad
            if nuevo_precio is not None:
                prod.precio = nuevo_precio

            # Actualizar en DB SQLite
            conexion = sqlite3.connect(self.db_name)
            cursor = conexion.cursor()
            cursor.execute('UPDATE productos SET cantidad = ?, precio = ? WHERE id = ?',
                           (prod.cantidad, prod.precio, id_prod))
            conexion.commit()
            conexion.close()
            print("✅ Producto actualizado correctamente.")
        else:
            print("❌ Producto no encontrado.")

    def buscar_por_nombre(self, nombre):
        """Usa comprensión de listas para filtrar la colección de productos."""
        resultados = [prod for prod in self.productos.values() if nombre.lower() in prod.nombre.lower()]
        if resultados:
            print("\n--- Resultados de Búsqueda ---")
            for prod in resultados:
                print(prod)
        else:
            print("❌ No se encontraron productos con ese nombre.")

    def mostrar_todos(self):
        if not self.productos:
            print("📦 El inventario está vacío.")
            return
        
        print("\n--- Inventario Completo de EcoLife ---")
        for prod in self.productos.values():
            print(prod)
        print("--------------------------------------")


def menu():
    """Interfaz de consola interactiva para el usuario."""
    inventario = Inventario()

    while True:
        print("\n🌱 --- Panel de Administración EcoLife --- 🌱")
        print("1. Añadir nuevo producto")
        print("2. Eliminar producto por ID")
        print("3. Actualizar cantidad o precio")
        print("4. Buscar producto por nombre")
        print("5. Mostrar todos los productos")
        print("6. Salir")
        
        opcion = input("Selecciona una opción (1-6): ")

        if opcion == '1':
            id_prod = input("ID del producto (ej. ECO001): ")
            nombre = input("Nombre del producto: ")
            try:
                cantidad = int(input("Cantidad en stock: "))
                precio = float(input("Precio unitario: "))
                nuevo_prod = Producto(id_prod, nombre, cantidad, precio)
                inventario.anadir_producto(nuevo_prod)
            except ValueError:
                print("❌ Error: Debes ingresar números válidos para cantidad y precio.")

        elif opcion == '2':
            id_prod = input("Ingrese el ID del producto a eliminar: ")
            inventario.eliminar_producto(id_prod)

        elif opcion == '3':
            id_prod = input("Ingrese el ID del producto a actualizar: ")
            print("Deja en blanco y presiona Enter si no deseas modificar el valor.")
            cant_input = input("Nueva cantidad: ")
            prec_input = input("Nuevo precio: ")
            
            try:
                nueva_cant = int(cant_input) if cant_input else None
                nuevo_prec = float(prec_input) if prec_input else None
                inventario.actualizar_producto(id_prod, nueva_cant, nuevo_prec)
            except ValueError:
                print("❌ Error: Ingresa valores numéricos válidos.")

        elif opcion == '4':
            nombre = input("Ingrese el nombre (o parte de él) a buscar: ")
            inventario.buscar_por_nombre(nombre)

        elif opcion == '5':
            inventario.mostrar_todos()

        elif opcion == '6':
            print("Saliendo del sistema. ¡Base de datos guardada con éxito!")
            break
        else:
            print("❌ Opción no válida. Intenta de nuevo.")

if __name__ == "__main__":
    menu()