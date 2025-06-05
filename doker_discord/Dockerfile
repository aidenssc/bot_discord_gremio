FROM python:3.11-slim

# Instala dependencias necesarias para Pillow y carga de fuentes TTF
RUN apt-get update && apt-get install -y \
    libfreetype6-dev \
    libjpeg-dev \
    zlib1g-dev \
    fonts-dejavu-core \
    fontconfig \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo
WORKDIR /app

# Copia requirements e instala dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código
COPY . .

# Variable de entorno opcional para el token
ENV DISCORD_TOKEN=changeme

# Comando para ejecutar el bot
CMD ["python", "bot.py"]
