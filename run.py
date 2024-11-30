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
    """Simula la generación de datos cada 5 segundos."""
    global datos_sensores
    while True:
        # Genera un dato con marca de tiempo completa y velocidad aleatoria
        nuevo_dato = {
            "hora": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # Marca de tiempo completa
            "velocidad": round(random.uniform(0, 60), 2)  # Velocidad aleatoria
        }

        # Limita la lista a los últimos 50 registros
        if len(datos_sensores) >= 50:
            datos_sensores.pop(0)
        datos_sensores.append(nuevo_dato)

        sleep(5)  # Espera 3 segundos antes de generar otro dato

@app.route("/")
def index():
    """Carga la página principal."""
    return render_template("index.html")

@app.route("/api/data", methods=["GET", "POST"])
def manejar_datos():
    """Maneja la obtención (GET) y recepción (POST) de datos."""
    global datos_sensores

    if request.method == "GET":
        # Devuelve los datos almacenados temporalmente
        return jsonify(datos_sensores)

    if request.method == "POST":
        # Recibe datos del simulador
        data = request.json
        print("Datos recibidos en el servidor:", data)  # Depuración

        if not data:
            return jsonify({"error": "No se recibieron datos"}), 400

        # Validar formato de 'hora'
        try:
            datetime.strptime(data["hora"], "%Y-%m-%d %H:%M:%S")
        except ValueError as e:
            print(f"Error al procesar 'hora': {e}")  # Imprimir el error exacto
            return jsonify({"error": "Formato de hora inválido. Se requiere '%Y-%m-%d %H:%M:%S'"}), 400

        # Limitar la lista a los últimos 50 registros
        if len(datos_sensores) >= 50:
            datos_sensores.pop(0)
        datos_sensores.append(data)

        # Guardar los datos en Firebase
        try:
            firebase_db.guardar_datos("anemometro/datos", data)
            print("Datos guardados en Firebase:", data)
        except Exception as e:
            print(f"Error al guardar datos en Firebase: {e}")

        return jsonify({"message": "Datos recibidos y almacenados"}), 200

@app.route("/api/data/filtrar", methods=["GET"])
def filtrar_datos():
    """Filtra los datos por rango de fechas."""
    global datos_sensores
    fecha_inicio = request.args.get("inicio")
    fecha_fin = request.args.get("fin")

    try:
        # Convertir cadenas a objetos datetime
        if fecha_inicio:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        if fecha_fin:
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')

        # Filtrar datos dentro del rango
        datos_filtrados = [
            d for d in datos_sensores
            if (not fecha_inicio or datetime.strptime(d["hora"], "%Y-%m-%d %H:%M:%S") >= fecha_inicio)
               and (not fecha_fin or datetime.strptime(d["hora"], "%Y-%m-%d %H:%M:%S") <= fecha_fin + timedelta(days=1))
        ]

        if not datos_filtrados:
            # Generar datos simulados si no se encuentran datos reales
            datos_filtrados = generar_datos_simulados(fecha_inicio, fecha_fin)

        return jsonify(datos_filtrados)
    except ValueError as e:
        print("Error al procesar fechas:", e)
        return jsonify({"error": "Formato de fecha inválido. Use YYYY-MM-DD"}), 400


def generar_datos_simulados(fecha_inicio, fecha_fin):
    """Genera datos simulados para cubrir un rango de fechas sin datos."""
    datos_simulados = []
    actual = fecha_inicio or datetime.now()
    final = fecha_fin or (actual + timedelta(days=1))

    while actual <= final:
        datos_simulados.append({
            "hora": actual.strftime("%Y-%m-%d %H:%M:%S"),
            "velocidad": round(random.uniform(0, 50), 2),
            "direccion": random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"])
        })
        actual += timedelta(minutes=30)  # Generar un dato cada 30 minutos

    return datos_simulados

if __name__ == "__main__":
    # Iniciar el hilo para generar datos simulados
    hilo_simulador = Thread(target=generar_datos_periodicamente, daemon=True)
    hilo_simulador.start()

    app.run(debug=True)
