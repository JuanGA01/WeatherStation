FROM python:3.11-alpine

# Install system dependencies, correct dev libraries, and build rtl_433
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

# Install Python dependencies
RUN pip install --no-cache-dir requests

WORKDIR /app

# Copy your local file with an accent and save it without the accent inside the container
COPY Estación.py /app/estacion.py

# Run command pointing to the internal file
CMD rtl_433 -f 433.92M -Y classic -s 250k -F json | python -u /app/estacion.py $WU_STATION_ID $WU_STATION_KEY
