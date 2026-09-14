import sys
import json
import requests
import math
from datetime import datetime

# Weather Underground configuration
STATION_ID = sys.argv[1]
STATION_KEY = sys.argv[2]
API_URL = "http://weatherstation.wunderground.com/weatherstation/updateweatherstation.php"

print(f"Starting bridge to Weather Underground for station: {STATION_ID}")

# Memory to calculate daily rain
rain_at_day_start = None
current_day = datetime.now().day

def calculate_dewpoint_f(temp_c, humidity):
    """Calculates the Dew Point using the Magnus formula"""
    if temp_c is None or humidity is None or humidity <= 0:
        return None
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    dewpt_c = (b * alpha) / (a - alpha)
    return (dewpt_c * 1.8) + 32  # WU requires Fahrenheit

for line in sys.stdin:
    try:
        data = json.loads(line)

        if data.get("model") == "Fineoffset-WHx080":
            # --- Extract extra data for the log ---
            bat_ok = data.get("battery_ok")

            # --- 1. Temperature, Humidity and Dew Point ---
            temp_c = data.get("temperature_C")
            temp_f = (temp_c * 1.8) + 32 if temp_c is not None else None

            humidity = data.get("humidity")
            dewpt_f = calculate_dewpoint_f(temp_c, humidity)

            # --- 2. Wind (fixed to wind_max_km_h) ---
            wind_dir = data.get("wind_dir_deg")

            speed_kmh = data.get("wind_avg_km_h")
            wind_speed_mph = speed_kmh / 1.60934 if speed_kmh is not None else 0.0

            gust_kmh = data.get("wind_max_km_h")  # Fixed!
            wind_gust_mph = gust_kmh / 1.60934 if gust_kmh is not None else 0.0

            # --- 3. Daily Rain (Precip Accum) ---
            rain_mm_total = data.get("rain_mm")
            daily_rain_in = 0.0
            rain_today_mm = 0.0

            if rain_mm_total is not None:
                today = datetime.now().day
                # Reset to 0.0 at midnight or when the container starts
                if rain_at_day_start is None or current_day != today:
                    rain_at_day_start = rain_mm_total
                    current_day = today

                rain_today_mm = rain_mm_total - rain_at_day_start

                # Protection in case you change batteries and the counter resets to 0
                if rain_today_mm < 0:
                    rain_at_day_start = rain_mm_total
                    rain_today_mm = 0.0

                daily_rain_in = rain_today_mm / 25.4

            # --- 4. Build parameters for WU ---
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

            # --- 5. Send to WU and log ---
            response = requests.get(API_URL, params=params, timeout=10)
            if response.status_code == 200:
                # Full log for the terminal with all the requested data
                battery_status = "OK" if bat_ok == 1 else "LOW"
                print(
                    f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SENT | "
                    f"Bat: {battery_status}({bat_ok}) | "
                    f"Temp: {temp_c}°C | "
                    f"Hum: {humidity}% | "
                    f"Dir: {wind_dir}° | "
                    f"Avg: {speed_kmh}km/h | "
                    f"Max: {gust_kmh}km/h | "
                    f"RainTotal: {rain_mm_total}mm | "
                    f"RainToday: {rain_today_mm:.1f}mm"
                )
            else:
                print(f"WU Error: {response.text}")

    except json.JSONDecodeError:
        continue
    except Exception as e:
        print(f"Loop error: {e}")
