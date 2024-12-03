from flask import Flask, jsonify, request, render_template
from threading import Thread
from time import sleep
import random
from datetime import datetime, timedelta
from api import firebase_db

app = Flask(__name__, template_folder="templates")

# Almacenamiento temporal para los datos simulados
datos_sensores = []

def generar_datos_periodicamente():
    """
    Genera datos simulados periódicamente para múltiples sensores.
    """
    global datos_sensores
    sensores = ["ANEM001", "ANEM002", "ANEM003", "ANEM004"]  # Lista de identificadores de sensores

    while True:
        for sensor in sensores:
            # Crear un nuevo dato simulado para cada sensor
            nuevo_dato = {
                "idsensor": sensor,  # Identificador del sensor
                "hora": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "velocidad": round(random.uniform(0, 60), 2),  # Velocidad aleatoria en km/h
            }

            # Mantener el almacenamiento con un máximo de 50 registros
            if len(datos_sensores) >= 50:
                datos_sensores.pop(0)
            datos_sensores.append(nuevo_dato)

            print(f"Dato generado para {sensor}: {nuevo_dato}")  # Depuración

        sleep(15)  # Esperar 15 segundos antes de generar el siguiente lote


@app.route("/")
def index():
    """
    Carga la página principal de la aplicación.

    Returns:
        str: Renderización de la plantilla `index.html`.
    """
    return render_template("index.html")

@app.route("/api/data", methods=["GET", "POST"])
def manejar_datos():
    """
    Maneja la obtención (GET) y recepción (POST) de datos del anemómetro.

    - `GET`: Devuelve los datos simulados almacenados temporalmente.
    - `POST`: Recibe un dato enviado por el simulador, lo valida, lo almacena localmente
              y lo guarda en Firebase.

    Returns:
        Response: Respuesta JSON con los datos o mensajes de estado.

    Raises:
        ValueError: Si el formato de `hora` no es válido en el método `POST`.
    """
    global datos_sensores

    if request.method == "GET":
        return jsonify(datos_sensores)

    if request.method == "POST":
        data = request.json
    print("Datos recibidos en el servidor:", data)

    if not data or "idsensor" not in data:
        return jsonify({"error": "No se recibieron datos o falta el campo 'idsensor'"}), 400

    # Validar formato de 'hora'
    try:
        datetime.strptime(data["hora"], "%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        print(f"Error al procesar 'hora': {e}")
        return jsonify({"error": "Formato de hora inválido. Se requiere '%Y-%m-%d %H:%M:%S'"}), 400

    # Limitar los registros a los últimos 50
    if len(datos_sensores) >= 50:
        datos_sensores.pop(0)
    datos_sensores.append(data)

    # Guardar en Firebase
    try:
        firebase_db.guardar_datos(f"sensores/{data['idsensor']}", data)  # Guardar según el sensor
        print(f"Datos guardados en Firebase para {data['idsensor']}: {data}")
    except Exception as e:
        print(f"Error al guardar datos en Firebase: {e}")

    return jsonify({"message": "Datos recibidos y almacenados"}), 200


@app.route("/api/data/filtrar", methods=["GET"])
def filtrar_datos():
    global datos_sensores
    fecha_inicio = request.args.get("inicio")
    fecha_fin = request.args.get("fin")
    idsensor = request.args.get("idsensor")  # Nuevo parámetro para filtrar por sensor

    try:
        # Convertir las fechas proporcionadas a objetos datetime
        if fecha_inicio:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        if fecha_fin:
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')

        # Filtrar los datos dentro del rango y por sensor
        datos_filtrados = [
            d for d in datos_sensores
            if (not idsensor or d.get("idsensor") == idsensor)
               and (not fecha_inicio or datetime.strptime(d["hora"], "%Y-%m-%d %H:%M:%S") >= fecha_inicio)
               and (not fecha_fin or datetime.strptime(d["hora"], "%Y-%m-%d %H:%M:%S") <= fecha_fin + timedelta(days=1))
        ]

        if not datos_filtrados:
            # Generar datos simulados si no hay datos reales
            datos_filtrados = generar_datos_simulados(fecha_inicio, fecha_fin)

        return jsonify(datos_filtrados)
    except ValueError as e:
        print("Error al procesar fechas:", e)
        return jsonify({"error": "Formato de fecha inválido. Use YYYY-MM-DD"}), 400


def generar_datos_simulados(fecha_inicio, fecha_fin):
    """
    Genera datos simulados para cubrir un rango de fechas sin datos reales.

    Genera un dato cada 30 minutos, simulando una velocidad aleatoria del viento
    y una dirección aleatoria.
    """
    datos_simulados = []
    actual = fecha_inicio or datetime.now()
    final = fecha_fin or (actual + timedelta(days=1))

    sensores = ["ANEM001", "ANEM002", "ANEM003", "ANEM004"]

    while actual <= final:
        for sensor in sensores:  # Generar datos para todos los sensores
            datos_simulados.append({
                "idsensor": sensor,
                "hora": actual.strftime("%Y-%m-%d %H:%M:%S"),
                "velocidad": round(random.uniform(0, 50), 2),
                "direccion": random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"])
            })
        actual += timedelta(minutes=30)  # Generar un dato cada 30 minutos

    return datos_simulados


if __name__ == "__main__":
    """
    Punto de entrada principal de la aplicación.

    Inicia un hilo para la generación periódica de datos simulados y ejecuta el servidor Flask.
    """
    # Iniciar el hilo para generar datos simulados
    hilo_simulador = Thread(target=generar_datos_periodicamente, daemon=True)
    hilo_simulador.start()

    app.run(debug=True)
