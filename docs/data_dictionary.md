# Diccionario de Datos - Proyecto SARA
## Dataset: SECOP II - Procesos de Contratación (SODA API)

Agencia Nacional de Contratación Pública – Colombia Compra Eficiente
Subdirección de Información y Desarrollo Tecnológico
Sistemas de Información
Fecha: octubre 2025 | Versión: 1.0

### 1. Objetivo del Documento
El presente diccionario de datos tiene como objetivo proporcionar una descripción estructurada, clara y detallada del conjunto de datos SECOP II - Procesos de Contratación, administrado por la Agencia Nacional de Contratación Pública - Colombia Compra Eficiente. Este documento busca facilitar la comprensión, uso, interoperabilidad y análisis de la información contenida en el sistema SECOP II. Además, sirve como herramienta de referencia técnica para garantizar la calidad, consistencia y trazabilidad de los datos abiertos.

### 2. Conjunto de Datos
El conjunto de datos contiene información detallada sobre los procesos de contratación estatal en Colombia. Incluye variables de identificación institucional, ubicación geográfica, y características de los procesos de compra.

### 3. URL
https://www.datos.gov.co/Gastos-Gubernamentales/SECOP-II-Procesos-de-Contrataci-n/p6dx-8zbt/about_data 
SECOP II - Procesos de Contratación | Datos Abiertos Colombia


### 4. Metadatos (Estructura de la API)

| Núm | Nombre de la columna | Descripción | Nombre del campo API | Tipo de Dato |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Entidad | Nombre de la Entidad que publica el proceso de compra pública | `entidad` | Texto |
| 2 | Nit Entidad | NIT de la Entidad que publicó el proceso | `nit_entidad` | Texto |
| 3 | Departamento Entidad | Departamento en el cual está registrada la entidad | `departamento_entidad` | Texto |
| 4 | Ciudad Entidad | Ciudad en la cual está registrada la entidad | `ciudad_entidad` | Texto |
| 5 | Orden Entidad | Orden de la Entidad (Nacional, Regional) | `ordenentidad` | Texto |
| 6 | Entidad Centralizada | Identifica si la entidad es o no centralizada | `codigo_pci` | Texto |
| 7 | ID del Proceso | Identificador Único del Proceso, valor generado por la plataforma | `id_del_proceso` | Texto |
| 8 | Referencia del Proceso | Identificador del Proceso, valor generado por la Entidad | `referencia_del_proceso` | Texto |
| 9 | PCI | Código de Unidad - Sub-Unidad Contratación | `ppi` | Texto |
| 10 | ID del Portafolio | Identificador del Portafolio al cual corresponde el proceso de compra | `id_del_portafolio` | Texto |
| 11 | Nombre del Procedimiento | Nombre dado al proceso de compra por la Entidad | `nombre_del_procedimiento` | Texto |
| 12 | Descripción del Procedimiento | Primera definición de las características principales del proceso | `descripci_n_del_procedimiento` | Texto |
| 13 | Fase | Fase en la que actualmente se encuentra el proceso | `fase` | Texto |
| 14 | Fecha de Publicación del Proceso | Fecha de la publicación inicial del proceso de compra | `fecha_de_publicacion_del` | Timestamp |
| 15 | Fecha de Ultima Publicación | Fecha de la última publicación hecha para el proceso de compra | `fecha_de_ultima_publicaci` | Timestamp |
| 16 | Fecha de Publicación (Fase Planeación Precalificación) | Fecha de publicación, dentro del proceso, de la fase de Planeación en Precalificación | `fecha_de_publicacion_fase` | Timestamp |
| 17 | Fecha de Publicación (Fase Selección Precalificación) | Fecha de publicación, dentro del proceso, de la fase de Selección en Precalificación | `fecha_de_publicacion_fase_1` | Timestamp |
| 18 | Fecha de Publicación (Manifestación de Interés) | Fecha de publicación, dentro del proceso, de la fase de Manifestación de Interés | `fecha_de_publicacion` | Timestamp |
| 19 | Fecha de Publicación (Fase Borrador) | Fecha de publicación, dentro del proceso, de la fase Borrador | `fecha_de_publicacion_fase_2` | Timestamp |
| 20 | Fecha de Publicación (Fase Selección) | Fecha de publicación, dentro del proceso, de la fase Selección | `fecha_de_publicacion_fase_3` | Timestamp |
| 21 | Precio Base | Precio Base, proyectado, del proceso de Compra | `precio_base` | Número |
| 22 | Modalidad de Contratación | Modalidad de selección bajo la cual se desarrolla el proceso de Compra | `modalidad_de_contratacion` | Texto |
| 23 | Justificación Modalidad de Contratación | En caso de requerirse, Justificación para la modalidad de selección elegida | `justificaci_n_modalidad_de` | Texto |
| 24 | Duración | Valor de la Duración estimada del proceso de compra pública | `duracion` | Número |
| 25 | Unidad de Duración | Unidad que aplica a la Duración estimada del proceso de compra pública | `unidad_de_duracion` | Texto |
| 26 | Fecha de Recepción de Respuestas | Fecha asignada para la recepción de respuestas por parte de los proveedores | `fecha_de_recepcion_de` | Timestamp |
| 27 | Fecha de Apertura de Respuesta | Fecha Estimada para la Apertura de las respuestas | `fecha_de_apertura_de_respuesta` | Timestamp |
| 28 | Fecha de Apertura Efectiva | Fecha Real para la Apertura de las respuestas | `fecha_de_apertura_efectiva` | Timestamp |
| 29 | Ciudad de la Unidad de Contratación | Cuidad en la que aparece registrada la unidad de contratación de la Entidad | `ciudad_de_la_unidad_de` | Texto |
| 30 | Nombre de la Unidad de Contratación | Nombre de la unidad de contratación de la Entidad | `nombre_de_la_unidad_de` | Texto |
| 31 | Proveedores Invitados | Número de Proveedores invitados a participar del proceso, en total | `proveedores_invitados` | Número |
| 32 | Proveedores con Invitación Directa | Proveedores con Invitación a participar hecha de forma directa | `proveedores_con_invitacion` | Número |
| 33 | Visualizaciones del Procedimiento | Número de Visualizaciones hechas a través de la herramienta, del Proceso de Compra | `visualizaciones_del` | Número |
| 34 | Proveedores que Manifestaron Interés | Proveedores que Manifestaron Interés en el proceso a través de la plataforma | `proveedores_que_manifestaron` | Número |
| 35 | Respuestas al Procedimiento | Respuestas hechas al procedimiento, tanto de proveedores como de la misma entidad | `respuestas_al_procedimiento` | Número |
| 36 | Respuestas Externas | Número de Respuestas hechas por entes externos | `respuestas_externas` | Número |
| 37 | Conteo de Respuestas a Ofertas | Número de Respuestas hechas de forma directa en las ofertas | `conteo_de_respuestas_a_ofertas` | Número |
| 38 | Proveedores Únicos con Respuestas | Proveedores Únicos que han redactado respuestas en el proceso | `proveedores_unicos_con` | Número |
| 39 | Numero de Lotes | Número de lotes de artículos solicitados dentro del proceso | `numero_de_lotes` | Número |
| 40 | Estado del Procedimiento | Estado actual de desarrollo del procedimiento de compra pública | `estado_del_procedimiento` | Texto |
| 41 | ID, Estado del Procedimiento | Identificador del Estado del procedimiento | `id_estado_del_procedimiento` | Número |
| 42 | Adjudicado | Determina si el proceso fue adjudicado | `adjudicado` | Texto |
| 43 | ID Adjudicación | Identificador de la adjudicación | `id_adjudicacion` | Texto |
| 44 | Código Proveedor | Código, en la plataforma, del proveedor adjudicado | `codigoproveedor` | Texto |
| 45 | Departamento Proveedor | Departamento en el que está registrado el proveedor adjudicado | `departamento_proveedor` | Texto |
| 46 | Ciudad Proveedor | Ciudad en la que está registrado el proveedor adjudicado | `ciudad_proveedor` | Texto |
| 47 | Fecha Adjudicación | Fecha en la que se hizo la adjudicación del proceso para el proveedor seleccionado | `fecha_adjudicacion` | Timestamp |
| 48 | Valor Total Adjudicación | Valor total Adjudicado | `valor_total_adjudicacion` | Número |
| 49 | Nombre del Adjudicador | Nombre del Usuario que ejecutó la acción de adjudicación | `nombre_del_adjudicador` | Texto |
| 50 | Nombre del Proveedor Adjudicado | Nombre del Proveedor Adjudicado | `nombre_del_proveedor` | Texto |
| 51 | NIT del Proveedor Adjudicado | NIT del Proveedor Adjudicado | `nit_del_proveedor_adjudicado` | Texto |
| 52 | Código Principal de Categoría | Código UNSPSC de la categoría principal del producto | `codigo_principal_de_categoria` | Texto |
| 53 | Estado de Apertura del Proceso | Estado actual de Apertura de información del proceso | `estado_de_apertura_del_proceso` | Texto |
| 54 | Tipo de Contrato | Tipo de Contrato definido para el proceso de compra | `tipo_de_contrato` | Texto |
| 55 | Subtipo de Contrato | Subtipo de Contrato definido para el proceso de compra | `subtipo_de_contrato` | Texto |
| 56 | Categorías Adicionales | Identificador de las categorías UNSPSC adicionales | `categorias_adicionales` | Texto |
| 57 | URL Proceso | URL, en la plataforma, en la que se puede consultar el proceso de compra | `urlproceso` | URL |
| 58 | Código Entidad | Código de la entidad en la plataforma SECOPII | `codigo_entidad` | Número |
| 59 | Estado Resumen | Resumen del estado del proceso de compra pública | `estado_resumen` | Texto |

### 5. Frecuencia
El conjunto de datos se actualiza diariamente, garantizando acceso a información vigente y consolidada sobre los actores registrados en SECOP II.

### 6. Cobertura
*   Geográfica: Nacional (Colombia). 
*   Institucional: Todas las entidades públicas registradas en SECOP II.
*   Temporal: Desde el inicio de operaciones de SECOP II hasta la fecha actual.
*   Temática: Información de contacto, clasificación institucional, estado de actividad, y datos del representante legal.
