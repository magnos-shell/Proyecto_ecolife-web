from flask_login import UserMixin
from Conexion.conexion import obtener_conexion

class Usuario(UserMixin):
    def __init__(self, id_usuario, nombre, email, password):
        # Flask-Login necesita obligatoriamente que el identificador se llame 'id'
        self.id = id_usuario 
        self.nombre = nombre
        self.email = email
        self.password = password

    @staticmethod
    def get_by_id(user_id):
        """Busca un usuario por su ID en MySQL (necesario para Flask-Login)"""
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (user_id,))
            user_data = cursor.fetchone()
            conexion.close()
            if user_data:
                return Usuario(
                    user_data['id_usuario'], 
                    user_data['nombre'], 
                    user_data['email'], 
                    user_data['password']
                )
        return None

    @staticmethod
    def get_by_email(email):
        """Busca un usuario por su Email (necesario para el Login)"""
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
            user_data = cursor.fetchone()
            conexion.close()
            if user_data:
                return Usuario(
                    user_data['id_usuario'], 
                    user_data['nombre'], 
                    user_data['email'], 
                    user_data['password']
                )
        return None