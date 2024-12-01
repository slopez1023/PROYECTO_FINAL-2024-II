import random
import time
import requests
from datetime import datetime

# Configuración del simulador
SENSOR_ID = "ANEM001"  # Identificador único del sensor
API_URL = "http://127.0.0.1:5000/api/data"  # URL del endpoint para enviar los datos
INTERVAL = 15  # Intervalo de tiempo entre lecturas (en segundos)

def generar_direccion_viento():
    """
    Genera una dirección de viento aleatoria.

    Las direcciones posibles son: N, NE, E, SE, S, SW, W, NW.

    Returns:
        str: Dirección del viento seleccionada aleatoriamente.
    """
    direcciones = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    return random.choice(direcciones)

def simular_lectura():
    """
    Genera una lectura simulada del anemómetro.

    La lectura incluye:
    - Velocidad del viento en km/h (aleatoria entre 0 y 50).
    - Dirección del viento (aleatoria).
    - Hora actual en formato `YYYY-MM-DD HH:MM:SS`.

    Returns:
        dict: Diccionario con la lectura simulada.
    """
    velocidad = round(random.uniform(0, 50), 2)  # Velocidad en km/h
    direccion = generar_direccion_viento()
    return {
        "idsensor": SENSOR_ID,
        "velocidad": velocidad,
        "direccion": direccion,
        "hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Marca de tiempo completa
    }

def enviar_datos():
    """
    Envía datos simulados del anemómetro al servidor Flask.

    Este método se ejecuta en un bucle infinito, generando una lectura simulada cada
    `INTERVAL` segundos y enviándola al servidor Flask configurado en `API_URL`.

    Proceso:
        1. Genera una lectura simulada usando `simular_lectura`.
        2. Intenta enviar los datos al servidor mediante una solicitud POST.
        3. Maneja errores de conexión y muestra mensajes de estado en la consola.

    Excepciones:
        Exception: Si ocurre un error de conexión con el servidor.

    Logs:
        - Muestra en consola los datos generados y su estado de envío.
    """
    while True:
        data = simular_lectura()  # Generar una nueva lectura
        print(f"Datos generados: {data}")  # Depuración

        try:
            # Enviar los datos al servidor mediante POST
            response = requests.post(API_URL, json=data)
            if response.status_code == 200:
                print(f"Datos enviados correctamente: {data}")
            else:
                print(f"Error al enviar datos: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error de conexión: {e}")

        # Esperar el intervalo definido antes de enviar otra lectura
        time.sleep(INTERVAL)

if __name__ == "__main__":
    """
    Punto de entrada principal del simulador.

    Llama a `enviar_datos` para iniciar el envío periódico de lecturas simuladas
    del anemómetro.
    """
    enviar_datos()
