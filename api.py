from flask import Blueprint, request, jsonify
from firebase_database import FirebaseDB
from datetime import datetime

# Crear un Blueprint
api_app = Blueprint("api", __name__)

# Inicializar conexión con Firebase
CREDENTIALS_PATH = "firebase_credentials.json"
DATABASE_URL = "https://sistemasensores-ac46d-default-rtdb.firebaseio.com/"
firebase_db = FirebaseDB(CREDENTIALS_PATH, DATABASE_URL)

@api_app.route("/api/data", methods=["POST"])
def receive_data():
    """
    Endpoint para recibir datos del sensor.
    """
    try:
        # Validar Content-Type
        if not request.is_json:
            return jsonify({
                "status": "error",
                "message": "Unsupported Media Type: Request Content-Type must be 'application/json'."
            }), 415

        # Leer los datos JSON enviados en la solicitud
        data = request.get_json()

        # Validar que el idsensor es el anemómetro
        if data.get("idsensor") != "ANEM001":
            return jsonify({
                "status": "error",
                "message": "El sensor no es reconocido como un anemómetro."
            }), 400

        fecha = datetime.now().strftime("%Y-%m-%d")  # Fecha actual
        hora = datetime.now().strftime("%H:%M:%S")  # Hora actual

        # Agregar fecha y hora a los datos recibidos
        data["fecha"] = fecha
        data["hora"] = hora

        # Guardar datos en Firebase
        firebase_db.guardar_datos("sensores", data)

        return jsonify({"status": "success", "message": "Datos guardados correctamente"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@api_app.route("/api/sensor/anemometro", methods=["GET"])
def get_anemometer_data():
    """
    Endpoint para recuperar datos del sensor anemómetro.
    """
    try:
        # Recuperar todos los datos de la colección 'sensores'
        datos = firebase_db.obtener_datos("sensores")

        # Filtrar los datos que corresponden al anemómetro (idsensor == "ANEM001")
        anemometro_datos = [dato for dato in datos if dato.get("idsensor") == "ANEM001"]

        return jsonify({
            "status": "success",
            "data": anemometro_datos
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
