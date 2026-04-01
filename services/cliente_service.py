from Conexion.conexion import obtener_conexion

class ClienteService:
    @staticmethod
    def get_all():
        conexion = obtener_conexion()
        clientes = []
        # Importante: Usamos dictionary=True para que Flask acceda por nombre de columna
        with conexion.cursor(dictionary=True) as cursor:
            # ACTUALIZADO: id_cliente ahora es id
            cursor.execute("SELECT id, nombre, email, telefono FROM clientes")
            clientes = cursor.fetchall()
        conexion.close()
        return clientes

    @staticmethod
    def create(nombre, email, telefono):
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            # Aquí usamos 'email' que es donde decidimos guardar la identificación
            query = "INSERT INTO clientes (nombre, email, telefono) VALUES (%s, %s, %s)"
            cursor.execute(query, (nombre, email, telefono))
            conexion.commit()
        conexion.close()