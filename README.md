# RTL-SDR Weather Station Bridge

A robust, Dockerized Python bridge that intercepts unencrypted 433MHz radio signals from a Fineoffset WHx080 weather station using an RTL-SDR dongle, processes the raw telemetry, and automatically pushes live updates to Weather Underground.

## Features
* **SDR Data Interception:** Uses `rtl_433` to demodulate and decode proprietary 433MHz FSK signals.
* **Custom Telemetry Processing:** 
  * Calculates daily rain accumulation from a continuous hardware counter.
  * Dynamically computes the **Dew Point** using the Magnus-Tetens formula.
  * Correctly distinguishes between sustained wind speed and wind gusts.
* **Hardware Monitoring:** Logs battery status (`battery_ok`) directly from the sensor's radio packets.
* **Resilient Architecture:** Fully containerized with Docker, featuring automatic restart policies to survive power outages or host reboots.

## Hardware Requirements
* Fineoffset WHx080 Weather Station (or compatible 433MHz clones)
* RTL-SDR USB Dongle (e.g., RTL2832U)
* A Linux host machine (e.g., Ubuntu Server, Raspberry Pi)

## Installation & Deployment

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/JuanGA01/WeatherStation.git](https://github.com/JuanGA01/WeatherStation.git)
   cd WeatherStation
