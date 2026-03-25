# Archivo: models/producto.py

class ProductoModel:
    """Clase que representa la estructura de un producto en EcoLife"""
    def __init__(self, id, nombre, cantidad, precio):
        self.id = id
        self.nombre = nombre
        self.cantidad = cantidad
        self.precio = precio