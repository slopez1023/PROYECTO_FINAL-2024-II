import firebase_admin
from firebase_admin import credentials, db

class FirebaseDB:
    def __init__(self, credentials_path, database_url):
        """Inicializa la conexión a Firebase."""
        try:
            cred = credentials.Certificate(credentials_path)
            firebase_admin.initialize_app(cred, {'databaseURL': database_url})
            print("Conexión con Firebase establecida.")
        except Exception as e:
            print(f"Error al conectar con Firebase: {e}")

    def guardar_datos(self, ruta, datos):
        """Guarda datos en una ruta específica."""
        try:
            ref = db.reference(ruta)
            ref.push(datos)
            print(f"Datos guardados en {ruta}: {datos}")
        except Exception as e:
            print(f"Error al guardar datos: {e}")
