import random
import time
import requests
from datetime import datetime

# Configuración del simulador
SENSORES = ["ANEM001", "ANEM002", "ANEM003", "ANEM004"]  # Identificadores únicos de sensores
API_URL = "http://127.0.0.1:5000/api/data"  # URL del endpoint para enviar los datos
INTERVAL = 15  # Intervalo de tiempo entre lecturas (en segundos)

def generar_direccion_viento():
    """
    Genera una dirección de viento aleatoria.

    Returns:
        str: Dirección del viento seleccionada aleatoriamente.
    """
    direcciones = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    return random.choice(direcciones)

def simular_lectura(idsensor):
    """
    Genera una lectura simulada para un sensor específico.

    Args:
        idsensor (str): Identificador único del sensor.

    Returns:
        dict: Diccionario con la lectura simulada.
    """
    return {
        "idsensor": idsensor,
        "velocidad": round(random.uniform(0, 50), 2),
        "direccion": generar_direccion_viento(),
        "hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

def enviar_datos():
    """
    Envía datos simulados de varios sensores al servidor Flask.
    """
    print("Sensores configurados:", SENSORES)  # Verificar la lista de sensores

    while True:
        for sensor in SENSORES:
            print(f"Generando datos para el sensor: {sensor}")  # Verificar iteración
            data = simular_lectura(sensor)  # Generar datos para cada sensor
            print(f"Datos generados: {data}")

            try:
                response = requests.post(API_URL, json=data)
                if response.status_code == 200:
                    print(f"Datos enviados correctamente: {data}")
                else:
                    print(f"Error al enviar datos: {response.status_code} - {response.reason}")
            except requests.ConnectionError:
                print(f"Error: No se pudo conectar con el servidor {API_URL}.")
            except requests.Timeout:
                print("Error: La solicitud al servidor excedió el tiempo límite.")
            except Exception as e:
                print(f"Error inesperado: {e}")

        time.sleep(INTERVAL)  # Esperar antes de enviar el siguiente lote de datos

if __name__ == "__main__":
    """
    Punto de entrada principal del simulador.
    """
    enviar_datos()
