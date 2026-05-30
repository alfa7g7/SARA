# Guía de Despliegue y Ejecución (SARA)

Este documento detalla los procedimientos exactos para levantar el ecosistema SARA en sus dos arquitecturas soportadas: **Modalidad Nativa** (uso de terminal y entornos virtuales puros) y **Modalidad Contenerizada** (Docker).

---

## 1. Modalidad Nativa (SARA Local / Bare-Metal)

Esta es la modalidad clásica. Los servicios se levantan independientemente en la terminal de Linux. Como el servidor de la universidad suele estar protegido por un Firewall, requerimos el uso de túneles SSH para poder ver la interfaz gráfica en nuestras máquinas locales.

### Paso 1.1: Conexión y Acceso (Local vs Remoto)
Dependiendo de dónde estés ejecutando el código, el acceso cambia:

**A. Ejecución 100% Local (Tu propio PC):**
Si descargaste el repositorio y lo estás corriendo en tu propio computador portátil o de escritorio, **no necesitas túneles SSH ni herramientas adicionales**. Simplemente abres tu navegador en `http://localhost:8501`.

**B. Ejecución Remota (Servidor / Nube / Icesi):**
Si el código está en un servidor (ej. un servidor de la Universidad), necesitarás hacer **Port Forwarding** por SSH para poder ver la interfaz en tu computador. 
*Nota: Si el servidor está protegido por Firewall y no estás en la red de la universidad, deberás usar una VPN (como **ZeroTier**) para tener acceso a la IP del servidor antes de conectarte por SSH.*

Si usas la consola nativa (Mac/Linux/Windows PowerShell), el comando genérico es:
```bash
ssh -L 8501:localhost:8501 -L 8000:localhost:8000 usuario@IP_del_servidor
```
*(Ejemplo en nuestro entorno de pruebas: `ssh -L 8501:localhost:8501 -L 8000:localhost:8000 analitica@104m01.icesi.edu.co`)*

> [!NOTA]  
> *Si usas VSCode Remoto, debes ir a la pestaña "Puertos" (Ports) en la terminal inferior y añadir manualmente los puertos `8000` y `8501` para que VSCode construya el túnel automáticamente a través de la conexión.*

### Paso 1.2: Matar procesos anteriores y verificar
Si el sistema se colgó o vas a reiniciar en frío, limpia los puertos usando:
```bash
pkill -f uvicorn
pkill -f streamlit
pkill -f ollama
```
Para estar 100% seguro de que los procesos murieron con éxito, ejecuta el siguiente comando. Si no te devuelve nada en pantalla, significa que los procesos están oficialmente muertos:
```bash
ps aux | grep -E "uvicorn|streamlit|ollama" | grep -v grep
```

### Paso 1.3: Encender el Motor de Inferencia (Ollama)
SARA depende de Llama 3. Ollama debe levantarse primero para que el puerto `11434` esté activo.
```bash
cd ~/SARA
nohup ollama serve > logs/ollama.log 2>&1 &
```
*(Nota: Si instalaste Ollama en una ruta personalizada, deberás colocar la ruta completa. Ejemplo en nuestro servidor Icesi: `nohup /home/analitica/ollama_bin/bin/ollama serve > logs/ollama.log 2>&1 &`)*

### Paso 1.4: Encender Backend y Frontend
Debemos activar el entorno virtual y levantar los dos servicios en segundo plano (`nohup`).

**A. Levantar la API (FastAPI):**
```bash
source SARA/bin/activate
nohup uvicorn src.api.main:app --host 0.0.0.0 --port 8000 > logs/api.log 2>&1 &
```

**B. Levantar el Panel Visual (Streamlit):**
```bash
nohup streamlit run src/frontend/app.py --server.address 0.0.0.0 --server.port 8501 > logs/frontend.log 2>&1 &
```

### Paso 1.5: Acceder
Abre tu navegador local en:
- Panel Principal: `http://localhost:8501`
- Swagger API: `http://localhost:8000/docs`

---

## 2. Modalidad Contenerizada (SARA Docker) 

*(Nota: Esta es la arquitectura definitiva hacia la que apuntamos en la Fase 3).*

En esta modalidad, **NO** dependes de configurar entornos virtuales de Python (`source bin/activate`), ni de lanzar procesos manuales con `nohup`. La arquitectura consta de **4 microservicios** (API, Frontend, Worker Autónomo y Ollama nativo).

### Requisitos Previos para Producción
1. **NVIDIA Container Toolkit:** Crítico. Debe estar instalado en el servidor anfitrión (bare-metal) para que el contenedor de Ollama pueda reclamar la GPU RTX.

### Ventajas del despliegue con Docker
1. **Un solo comando:** Levanta toda la infraestructura simultáneamente.
2. **Resiliencia:** Si la aplicación se cae, Docker la reinicia automáticamente (`restart: always`).
3. **Escalabilidad:** El Worker y la API operan en contenedores separados protegiendo la carga de memoria.

### Comandos de Ejecución (Arquitectura Docker)

Para levantar el ecosistema completo:
```bash
docker-compose up --build -d
```
> [!TIP]  
> El flag `-d` (detached) hace exactamente lo mismo que `nohup`: manda todo a correr silenciosamente en el fondo, pero de una manera organizada.

Para ver los logs en tiempo real sin usar `cat` o abrir archivos `.log`:
```bash
docker-compose logs -f
```

Para apagar todo el ecosistema de tajo (equivalente a los 3 comandos `pkill` nativos):
```bash
docker-compose down
```

### Acceso
Simplemente navegas a la IP pública del servidor sin preocuparte por túneles (asumiendo enrutamiento al puerto 80):
- Panel Principal: `http://104m01.icesi.edu.co`
