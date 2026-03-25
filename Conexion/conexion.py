import mysql.connector
from mysql.connector import Error

def obtener_conexion():
    """Establece la conexión a la base de datos MySQL"""
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",          # Tu usuario de phpMyAdmin
            password="",          # Déjalo vacío si entraste sin contraseña
            database="ecolife_db" # La base de datos que acabamos de crear
        )
        if conexion.is_connected():
            print("Conexión exitosa a MySQL - EcoLife")
            return conexion
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None