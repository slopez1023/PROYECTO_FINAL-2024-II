from flask import Blueprint, request, jsonify
from firebase_database import FirebaseDB
from datetime import datetime

# Crear un Blueprint para organizar las rutas de la API
api_app = Blueprint("api", __name__)

# Inicializar conexión con Firebase usando las credenciales y la URL de la base de datos
CREDENTIALS_PATH = "firebase_credentials.json"
DATABASE_URL = "https://sistemasensores-ac46d-default-rtdb.firebaseio.com/"
firebase_db = FirebaseDB(CREDENTIALS_PATH, DATABASE_URL)

@api_app.route("/api/data", methods=["POST"])
def receive_data():
    """
    Endpoint para recibir datos del sensor y almacenarlos en Firebase.

    Funcionalidad:
    - Valida que la solicitud sea en formato JSON.
    - Asegura que el sensor sea del tipo anemómetro (`idsensor` == "ANEM001").
    - Enriquece los datos con la fecha y hora actuales.
    - Guarda los datos en Firebase.

    Respuestas:
    - 200: Datos recibidos y guardados correctamente.
    - 400: Error en los datos enviados (por ejemplo, sensor no válido).
    - 415: Error en el formato de la solicitud (Content-Type no válido).
    - 500: Error interno al procesar los datos.

    """
    try:
        # Validar que el contenido sea JSON
        if not request.is_json:
            return jsonify({
                "status": "error",
                "message": "Unsupported Media Type: Request Content-Type must be 'application/json'."
            }), 415

        # Extraer los datos del cuerpo de la solicitud
        data = request.get_json()

        # Validar que el idsensor esté en la lista de sensores permitidos
        if data.get("idsensor") not in ["ANEM001", "ANEM002", "ANEM003", "ANEM004"]:
            return jsonify({
                "status": "error",
                "message": f"El sensor {data.get('idsensor')} no está permitido."
            }), 400

        # Agregar la fecha y hora actuales a los datos
        fecha = datetime.now().strftime("%Y-%m-%d")
        hora = datetime.now().strftime("%H:%M:%S")
        data["fecha"] = fecha
        data["hora"] = hora

        # Guardar los datos en Firebase en la colección 'sensores'
        firebase_db.guardar_datos("sensores", data)

        return jsonify({"status": "success", "message": "Datos guardados correctamente"}), 200
    except Exception as e:
        # Manejo de excepciones genéricas
        return jsonify({"status": "error", "message": str(e)}), 500
@api_app.route("/api/sensor/anemometro", methods=["GET"])
def get_anemometer_data():
    """
    Endpoint para recuperar datos históricos del sensor anemómetro desde Firebase.

    Funcionalidad:
    - Recupera todos los datos almacenados en la colección 'sensores'.
    - Filtra los datos que pertenecen al sensor anemómetro (`idsensor` == "ANEM001").

    Respuestas:
    - 200: Datos recuperados exitosamente.
    - 500: Error interno al recuperar los datos.

    """
    try:
        # Recuperar el identificador del sensor de los parámetros de consulta
        idsensor = request.args.get("idsensor")
        if not idsensor:
            return jsonify({
                "status": "error",
                "message": "Debe especificar el identificador del sensor (idsensor)."
            }), 400

        # Validar que el idsensor esté permitido
        if idsensor not in ["ANEM001", "ANEM002", "ANEM003", "ANEM004"]:  # Ajusta según tu lista
            return jsonify({
                "status": "error",
                "message": f"El sensor {idsensor} no está permitido."
            }), 400

        # Obtener todos los datos de la colección 'sensores'
        datos = firebase_db.obtener_datos("sensores")

        # Filtrar los datos correspondientes al sensor solicitado
        sensor_datos = [dato for dato in datos if dato.get("idsensor") == idsensor]

        return jsonify({
            "status": "success",
            "data": sensor_datos
        }), 200
    except Exception as e:
        # Manejo de excepciones genéricas
        return jsonify({"status": "error", "message": str(e)}), 500
