# Manual de Usuario - Ecosistema SARA

Bienvenido al manual operativo de **SARA (Sistema de Análisis mediante RAG y Agentes)**. Este documento está diseñado para los usuarios finales (Ej. Directores de Consultoría, Ingenieros de Operaciones) que interactúan con la interfaz gráfica del sistema en el día a día.

---

## 1. Acceso al Panel de Control

SARA cuenta con un panel de control web centralizado. Para acceder a él, asegúrate de que el sistema esté encendido (ya sea en modalidad local o en contenedores Docker) y abre tu navegador web en la dirección IP designada por el equipo de ingeniería (usualmente `Puerto 8501` en local, o `Puerto 80` en producción).

---

## 2. Navegación por Pestañas

La interfaz está dividida en cuatro (4) pestañas principales ubicadas en la parte superior. Cada una tiene una responsabilidad específica:

### ⚙️ Pestaña 1: Configuración Core
Esta es la sala de control de SARA. Cualquier cambio que hagas aquí se guarda en la base de datos y altera el comportamiento futuro de la Inteligencia Artificial de forma inmediata.

*   **Umbral de Visualización (Slider):** Define qué tan alto debe ser el porcentaje de viabilidad (0-100%) para que un contrato aparezca en las tablas de la interfaz visual. *Ejemplo: Si lo pones en 70%, solo verás los contratos que SARA considere altamente viables.*
*   **Umbral de Alerta SMTP:** Define el porcentaje mínimo para que SARA dispare una alerta automática a tu correo electrónico.
*   **Blacklist (Palabras Prohibidas):** Una lista separada por comas de palabras que SARA usará para descartar contratos sin siquiera analizarlos (Ej. `reparacion, pintura, cableado`).
*   **Destinatarios del Notificador:** Los correos electrónicos (separados por comas) que recibirán las alertas y borradores de propuestas.
*   **Auditor Estricto (Toggle):** Si está activado, el "Agente Jurídico" de SARA será extremadamente pesimista y buscará excusas para rechazar el contrato. Ayuda a evitar falsos positivos.

### 📚 Pestaña 2: Base de Conocimiento (RAG)
Aquí es donde "educas" a SARA. SARA no sabe nada de tu organización por defecto; su conocimiento proviene de los documentos institucionales que tú le subas.

*   **Sube PDFs o DOCX:** Arrastra aquí portafolios de servicios, historiales de proyectos pasados o CVs de investigadores.
*   SARA leerá el documento, lo fragmentará y lo guardará en su "memoria vectorial" (ChromaDB) para usarlo como referencia en futuras licitaciones.

### 🧠 Pestaña 3: Golden Truth (Calibración)
Esta pestaña está reservada para el equipo de analítica. Permite comparar las decisiones que tomó la IA contra las decisiones que hubiera tomado un consultor humano experto.

*   **Matriz de Confusión:** Gráficos que te muestran qué tan precisa es SARA (Exactitud, Falsos Positivos, Verdaderos Negativos).
*   **Tabla de Fallos:** Te muestra los contratos donde SARA se equivocó frente al humano, permitiéndote ajustar el *prompt* o subir más documentos a la Base de Conocimiento.

### 🚀 Pestaña 4: Operaciones Manuales
Ideal para pruebas o extracciones fuera del ciclo diario.

*   **Ingesta Masiva de SECOP II:** Te permite decirle a SARA que se conecte inmediatamente al gobierno y busque licitaciones de un rango de fechas específico, ignorando la automatización nocturna.

---

## 3. Entendiendo las Evaluaciones de SARA

Cuando SARA evalúa un contrato, genera un registro que puedes ver en el archivo de alertas o en la base de datos. Consta de 3 elementos:

1.  **Viabilidad (%):** Una puntuación de 0 a 100 basada en qué tanto se parece el pliego de condiciones a las capacidades institucionales subidas en la pestaña RAG.
2.  **Justificación:** Un párrafo narrativo donde Llama 3 explica **por qué** le dio ese puntaje, mencionando similitudes semánticas o riesgos legales encontrados.
3.  **Borrador de Propuesta (Opcional):** Si la viabilidad superó tu "Umbral de Alerta SMTP", SARA adjuntará un documento pre-redactado con una propuesta técnica inicial para enviar al cliente estatal.

---

## 4. Solución de Problemas (Troubleshooting)

*   **"No me llegan los correos":** Revisa que los correos en la *Configuración Core* estén bien escritos (sin espacios raros) y verifica que la contraseña de aplicación de Gmail esté vigente en el archivo `.env`.
*   **"SARA rechaza todos los contratos":** Tu *Blacklist* podría ser muy agresivo, o el *Auditor Estricto* está encendido sin que tengas suficientes documentos en la Base de Conocimiento RAG para convencerlo. Sube más PDFs descriptivos de tu capacidad instalada.
*   **"La interfaz no carga":** Notifica al ingeniero de sistemas para que levante los contenedores Docker o revise el puerto de red.
