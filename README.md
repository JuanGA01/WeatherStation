# RTL-SDR Weather Station Bridge

A robust, Dockerized Python bridge that intercepts unencrypted 433MHz radio signals from a Fineoffset WHx080 weather station using an RTL-SDR dongle, processes the raw telemetry, and automatically pushes live updates to [Weather Underground](https://www.wunderground.com/).

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
* RTL-SDR USB Dongle (RTL-SDR V2 with Fitipower FC0012 tuner)
* A Linux host machine (e.g., Ubuntu Server, Raspberry Pi)

## Installation & Deployment

### 1. Clone the repository

```bash
git clone https://github.com/JuanGA01/WeatherStation.git
cd WeatherStation
```

### 2. Configure Weather Underground Credentials

To send data to Weather Underground, you need to register a Personal Weather Station (PWS) on their platform to obtain your unique Station ID and Station Key (Password):

* Go to [Weather Underground](https://www.wunderground.com/) and log into your account.
* Navigate to your profile/settings and select **My Devices** to register a new PWS.
* Once registered, note down your **Station ID** and **Station Key**.

Copy the example environment file and fill it with your credentials:

```bash
cp .env.example .env
nano .env
```

Insert your data:

```
WU_STATION_ID=your_station_id_here
WU_STATION_KEY=your_station_key_here
```

### 3. Deploy with Docker Compose

The `docker-compose.yml` handles building the Alpine-based Python image, compiling `rtl_433` from source (utilizing the RTL-SDR V2 with the Fitipower FC0012 tuner), and passing the USB device to the container.

```bash
sudo docker compose up -d --build
```

### 4. Monitor Live Logs

```bash
sudo docker compose logs -f
```
