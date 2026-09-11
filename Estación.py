import sys
import json
import requests
import math
from datetime import datetime

# Configuración de Weather Underground
STATION_ID = sys.argv[1]
STATION_KEY = sys.argv[2]
API_URL = "http://weatherstation.wunderground.com/weatherstation/updateweatherstation.php"

print(f"Iniciando puente hacia Weather Underground para la estación: {STATION_ID}")

# Memoria para calcular la lluvia diaria
lluvia_arranque_dia = None
dia_actual = datetime.now().day

def calcular_dewpoint_f(temp_c, humedad):
    """Calcula el punto de rocío (Dew Point) usando la fórmula de Magnus"""
    if temp_c is None or humedad is None or humedad <= 0:
        return None
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humedad / 100.0)
    dewpt_c = (b * alpha) / (a - alpha)
    return (dewpt_c * 1.8) + 32 # WU requiere Fahrenheit

for line in sys.stdin:
    try:
        data = json.loads(line)

        if data.get("model") == "Fineoffset-WHx080":
            # --- Extraer datos extra para el log ---
            bat_ok = data.get("battery_ok")
            
            # --- 1. Temperatura, Humedad y Punto de Rocío ---
            temp_c = data.get("temperature_C")
            temp_f = (temp_c * 1.8) + 32 if temp_c is not None else None
            
            humidity = data.get("humidity")
            dewpt_f = calcular_dewpoint_f(temp_c, humidity)

            # --- 2. Viento (Corregido a wind_max_km_h) ---
            wind_dir = data.get("wind_dir_deg")

            speed_kmh = data.get("wind_avg_km_h")
            wind_speed_mph = speed_kmh / 1.60934 if speed_kmh is not None else 0.0

            gust_kmh = data.get("wind_max_km_h")  # ¡Corregido!
            wind_gust_mph = gust_kmh / 1.60934 if gust_kmh is not None else 0.0

            # --- 3. Lluvia Diaria (Precip Accum) ---
            rain_mm_total = data.get("rain_mm")
            daily_rain_in = 0.0
            lluvia_hoy_mm = 0.0

            if rain_mm_total is not None:
                hoy = datetime.now().day
                # Resetear a 0.0 a medianoche o al arrancar el contenedor
                if lluvia_arranque_dia is None or dia_actual != hoy:
                    lluvia_arranque_dia = rain_mm_total
                    dia_actual = hoy
                
                lluvia_hoy_mm = rain_mm_total - lluvia_arranque_dia
                
                # Protección por si cambias las pilas y el contador vuelve a 0
                if lluvia_hoy_mm < 0:
                    lluvia_arranque_dia = rain_mm_total
                    lluvia_hoy_mm = 0.0
                    
                daily_rain_in = lluvia_hoy_mm / 25.4

            # --- 4. Construir parámetros para WU ---
            params = {
                "ID": STATION_ID,
                "PASSWORD": STATION_KEY,
                "dateutc": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "tempf": f"{temp_f:.1f}" if temp_f is not None else "",
                "humidity": str(humidity) if humidity is not None else "",
                "dewptf": f"{dewpt_f:.1f}" if dewpt_f is not None else "",
                "winddir": str(wind_dir) if wind_dir is not None else "",
                "windspeedmph": f"{wind_speed_mph:.1f}",
                "windgustmph": f"{wind_gust_mph:.1f}",
                "dailyrainin": f"{daily_rain_in:.2f}",
                "softwaretype": "rtl_433_Docker_Bridge",
                "action": "updateraw"
            }

            # --- 5. Enviar a WU y registrar en el log ---
            response = requests.get(API_URL, params=params, timeout=10)
            if response.status_code == 200:
                # Log completo para la terminal con todos los datos que pediste
                estado_bateria = "OK" if bat_ok == 1 else "BAJA"
                print(
                    f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ENVIADO | "
                    f"Bat: {estado_bateria}({bat_ok}) | "
                    f"Temp: {temp_c}°C | "
                    f"Hum: {humidity}% | "
                    f"Dir: {wind_dir}° | "
                    f"Med: {speed_kmh}km/h | "
                    f"Max: {gust_kmh}km/h | "
                    f"LluviaTot: {rain_mm_total}mm | "
                    f"LluviaHoy: {lluvia_hoy_mm:.1f}mm"
                )
            else:
                print(f"Error WU: {response.text}")

    except json.JSONDecodeError:
        continue
    except Exception as e:
        print(f"Error en el bucle: {e}")

