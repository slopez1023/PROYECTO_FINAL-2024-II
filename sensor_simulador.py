import random
import time
import requests
from datetime import datetime

# Configuración del simulador
SENSOR_ID = "ANEM001"
API_URL = "http://127.0.0.1:5000/api/data"
INTERVAL = 15  # Intervalo de tiempo entre lecturas en segundos

def generar_direccion_viento():
    """Genera una dirección de viento aleatoria."""
    direcciones = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    return random.choice(direcciones)

def simular_lectura():
    """Genera una lectura simulada."""
    velocidad = round(random.uniform(0, 50), 2)  # Velocidad en km/h
    direccion = generar_direccion_viento()
    return {
        "idsensor": SENSOR_ID,
        "velocidad": velocidad,
        "direccion": direccion,
        "hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Marca de tiempo completa
    }

def enviar_datos():
    """Envía datos simulados al servidor Flask."""
    while True:
        data = simular_lectura()
        print(f"Datos generados: {data}")  # Verificar el contenido de 'hora'
        try:
            response = requests.post(API_URL, json=data)
            if response.status_code == 200:
                print(f"Datos enviados correctamente: {data}")
            else:
                print(f"Error al enviar datos: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error de conexión: {e}")
        time.sleep(INTERVAL)


if __name__ == "__main__":
    enviar_datos()
