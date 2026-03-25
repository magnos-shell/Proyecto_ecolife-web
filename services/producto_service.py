# Archivo: services/producto_service.py

from Conexion.conexion import obtener_conexion
from models.producto import ProductoModel

class ProductoService:
    """Servicio que maneja todas las operaciones CRUD para los Productos"""

    @staticmethod
    def get_all():
        """Leer todos los registros (Read)"""
        conexion = obtener_conexion()
        productos = []
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM productos")
            filas = cursor.fetchall()
            for fila in filas:
                productos.append(ProductoModel(fila['id'], fila['nombre'], fila['cantidad'], fila['precio']))
            conexion.close()
        return productos

    @staticmethod
    def get_by_id(producto_id):
        """Obtener un solo producto por su ID (Para editar)"""
        conexion = obtener_conexion()
        producto = None
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM productos WHERE id = %s", (producto_id,))
            fila = cursor.fetchone()
            if fila:
                producto = ProductoModel(fila['id'], fila['nombre'], fila['cantidad'], fila['precio'])
            conexion.close()
        return producto

    @staticmethod
    def create(nombre, cantidad, precio):
        """Crear un nuevo registro (Create)"""
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            sql = "INSERT INTO productos (nombre, cantidad, precio) VALUES (%s, %s, %s)"
            cursor.execute(sql, (nombre, cantidad, precio))
            conexion.commit()
            conexion.close()

    @staticmethod
    def update(producto_id, nombre, cantidad, precio):
        """Actualizar un registro existente (Update)"""
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            sql = "UPDATE productos SET nombre=%s, cantidad=%s, precio=%s WHERE id=%s"
            cursor.execute(sql, (nombre, cantidad, precio, producto_id))
            conexion.commit()
            conexion.close()

    @staticmethod
    def delete(producto_id):
        """Eliminar un registro (Delete)"""
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM productos WHERE id = %s", (producto_id,))
            conexion.commit()
            conexion.close()