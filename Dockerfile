FROM python:3.12-slim

# Metadatos
LABEL maintainer="Equipo SARA"
LABEL version="1.0"
LABEL description="SARA - Sistema de Análisis y Recuperación de Oportunidades SECOP"

# Configurar directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema operativo (necesarias para compilar algunos paquetes)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de requerimientos
COPY requirements.txt .

# Instalar dependencias de Python optimizadas y sin caché
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código fuente
# Nota: La carpeta data/ no se copiará si está en .dockerignore,
# lo cual es correcto porque se inyectará mediante volúmenes en el docker-compose.
COPY . .

# Exponer el puerto de Streamlit (Backend UI) y FastAPI (si se usa)
EXPOSE 8501
EXPOSE 8000

# Añadir variables de entorno por defecto generales
ENV PYTHONUNBUFFERED=1

# El comando de entrada se inyectará polimórficamente desde el docker-compose.yml
# (uvicorn, streamlit, o worker_loop)
CMD ["python", "--version"]
