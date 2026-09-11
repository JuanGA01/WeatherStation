FROM python:3.11-alpine

# Instalar dependencias del sistema, librerías de desarrollo correctas y compilar rtl_433
RUN apk add --no-cache \
    rtl-sdr \
    librtlsdr-dev \
    build-base \
    cmake \
    libusb-dev \
    git \
    && git clone https://github.com/merbanan/rtl_433.git /tmp/rtl_433 \
    && cd /tmp/rtl_433 \
    && mkdir build && cd build \
    && cmake .. \
    && make -j$(nproc) \
    && make install \
    && apk del build-base cmake git librtlsdr-dev \
    && rm -rf /tmp/rtl_433

# Instalar dependencias de Python
RUN pip install --no-cache-dir requests

WORKDIR /app

# Copiamos tu archivo local con tilde y lo guardamos sin tilde dentro del contenedor
COPY Estación.py /app/estacion.py

# Comando de ejecución apuntando al archivo interno
CMD rtl_433 -f 433.92M -Y classic -s 250k -F json | python -u /app/estacion.py $WU_STATION_ID $WU_STATION_KEY
