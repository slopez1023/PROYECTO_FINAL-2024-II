import firebase_admin
from firebase_admin import credentials, db

class FirebaseDB:
    """
    Clase para interactuar con Firebase Realtime Database.

    Esta clase permite establecer una conexión con una base de datos de Firebase
    y proporciona métodos para guardar datos en rutas específicas.

    Atributos:
        credentials_path (str): Ruta al archivo de credenciales JSON de Firebase.
        database_url (str): URL de la base de datos de Firebase Realtime Database.
    """

    def __init__(self, credentials_path, database_url):
        """
        Inicializa la conexión a Firebase Realtime Database.

        Args:
            credentials_path (str): Ruta al archivo de credenciales JSON de Firebase.
            database_url (str): URL de la base de datos en tiempo real.

        Raises:
            Exception: Si no se puede establecer la conexión con Firebase.
        """
        try:
            # Cargar credenciales y configurar la conexión
            cred = credentials.Certificate(credentials_path)
            firebase_admin.initialize_app(cred, {'databaseURL': database_url})
            print("Conexión con Firebase establecida.")
        except Exception as e:
            print(f"Error al conectar con Firebase: {e}")
            raise

    def guardar_datos(self, ruta, datos):
        """
        Guarda datos en una ruta específica dentro de Firebase Realtime Database.

        Args:
            ruta (str): Ruta en la base de datos donde se almacenarán los datos.
            datos (dict): Diccionario con los datos a guardar.

        Raises:
            Exception: Si ocurre un error al intentar guardar los datos en Firebase.

        Ejemplo:
            firebase_db = FirebaseDB("credenciales.json", "https://example.firebaseio.com/")
            firebase_db.guardar_datos("sensores/anemometro", {"velocidad": 25.5, "direccion": "N"})
        """
        try:
            ref = db.reference(ruta)  # Referencia a la ruta en la base de datos
            ref.push(datos)  # Añade los datos como un nuevo nodo
            print(f"Datos guardados en {ruta}: {datos}")
        except Exception as e:
            print(f"Error al guardar datos: {e}")
            raise
