import streamlit as st
import requests
import json
import pandas as pd
import os
import sys
import base64

# Asegurar que Streamlit puede importar desde src/
sys.path.append(os.getcwd())

# Configuración básica de la página
st.set_page_config(page_title="SARA - Universidad Icesi", layout="wide")

API_URL = os.getenv("API_URL", "http://localhost:8000")
LOG_FILE = os.path.join("logs", "pipeline_masivo.log")

# ==========================================
# 1. IDENTIDAD INSTITUCIONAL (CSS & BASE64)
# ==========================================
def inject_custom_branding():
    font_path = os.path.join("assets", "fuentes", "institucional.ttf")
    b64_font = ""
    if os.path.exists(font_path):
        with open(font_path, "rb") as f:
            b64_font = base64.b64encode(f.read()).decode("utf-8")
            
    custom_css = f"""
    <style>
    @font-face {{
        font-family: 'IcesiFont';
        src: url(data:font/ttf;base64,{b64_font});
    }}
    html, body, [class*="css"] {{
        font-family: 'IcesiFont', sans-serif;
    }}
    h1, h2, h3 {{
        color: #004b87 !important;
    }}
    .stButton>button {{
        background-color: #004b87;
        color: white;
        border-radius: 4px;
        border: none;
    }}
    .stButton>button:hover {{
        background-color: #003366;
        color: white;
    }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

inject_custom_branding()

# ==========================================
# 2. SISTEMA DE LOGIN (st.session_state)
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None

if not st.session_state.logged_in:
    # Mostramos el logo de Icesi en la pantalla de autenticación
    logo_path = os.path.join("assets", "logo_icesi.png")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists(logo_path):
            st.image(logo_path, width=200)
            
        st.markdown("<h2 style='text-align: center;'>Autenticación SARA</h2>", unsafe_allow_html=True)
        with st.form("login_form"):
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            submitted = st.form_submit_button("Ingresar")
            
            if submitted:
                emp_user = os.getenv("SARA_EMPLOYEE_USER", "empleado")
                emp_pass = os.getenv("SARA_EMPLOYEE_PASS", "icesi2026")
                adm_user = os.getenv("SARA_ADMIN_USER", "admin")
                adm_pass = os.getenv("SARA_ADMIN_PASS", "admin2026")
                
                if username == emp_user and password == emp_pass:
                    st.session_state.logged_in = True
                    st.session_state.user_role = "Empleado"
                    st.rerun()
                elif username == adm_user and password == adm_pass:
                    st.session_state.logged_in = True
                    st.session_state.user_role = "Administrador"
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")
    st.stop()

# ==========================================
# 3. SIDEBAR (Navegación e Imágenes)
# ==========================================
with st.sidebar:
    # 1era Imagen: Logo Icesi
    logo_icesi_path = os.path.join("assets", "logo_icesi.png")
    if os.path.exists(logo_icesi_path):
        st.image(logo_icesi_path, use_container_width=True)
        
    st.markdown("---")
    
    # 2da Imagen: Logo Original
    logo_original_path = os.path.join("assets", "logo.jpeg")
    if os.path.exists(logo_original_path):
        st.image(logo_original_path, use_container_width=True)
        
    st.markdown("---")
    st.markdown(f"**Usuario Actual:** {st.session_state.user_role}")
    if st.button("Cerrar Sesión"):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.rerun()
    st.markdown("---")

# ==========================================
# 4. VISTA: ADMINISTRADOR (Panel de Control)
# ==========================================
if st.session_state.user_role == "Administrador":
    st.title("⚙️ Panel de Administración SARA")
    
    # --- Módulo de Observabilidad ---
    st.subheader("🩺 Health Checks y Observabilidad")
    col1, col2, col3 = st.columns(3)
    try:
        resp = requests.get(f"{API_URL}/api/v1/health", timeout=5)
        if resp.status_code == 200:
            health_data = resp.json()
            with col1:
                if health_data.get("database_connected"):
                    st.success("🟢 Base de Datos: Activa")
                else:
                    st.error("🔴 Base de Datos: Caída")
            with col2:
                if health_data.get("ollama_connected"):
                    st.success("🟢 Llama 3 (Ollama): Respondiendo")
                else:
                    st.error("🔴 Llama 3 (Ollama): Fuera de Línea")
            with col3:
                st.info("🟡 SMTP / Notificador: Esperando ciclo")
        else:
            st.error("🔴 API FastAPI retornó error")
    except requests.exceptions.RequestException:
        st.error("🔴 API FastAPI no está en ejecución.")

    st.markdown("---")
    
    # --- Visor de Logs en Vivo ---
    st.subheader("🖥️ Visor de Logs en Vivo (pipeline_masivo.log)")
    log_path = os.path.join(os.getcwd(), LOG_FILE)
    if os.path.exists(log_path):
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                last_50 = "".join(lines[-50:])
            st.code(last_50, language="bash")
        except Exception as e:
            st.error(f"Error leyendo logs: {e}")
    else:
        st.warning(f"No se encontró el archivo de registro: {LOG_FILE}")
        
    st.markdown("---")

    # --- 4 Pestañas del Administrador ---
    tab_core, tab_rag, tab_truth, tab_ops = st.tabs([
        "⚙️ Configuración Core", 
        "📚 Base de Conocimiento (RAG)", 
        "🧠 Golden Truth (Calibración)", 
        "🚀 Operaciones Manuales"
    ])
    
    with tab_core:
        st.subheader("🎛️ Configuración Dinámica del Orquestador")
        try:
            config_resp = requests.get(f"{API_URL}/api/v1/config", timeout=5)
            if config_resp.status_code == 200:
                config_activa = config_resp.json()
                
                with st.form("form_config"):
                    umbral_pantalla = st.slider(
                        "Umbral de Visualización (Radar Empleado) (%)", 
                        min_value=0, max_value=100, 
                        value=int(config_activa.get("umbral_pantalla", 70)),
                        help="Qué tan permisiva es la tabla web (Radar)."
                    )
                    
                    umbral_correo = st.slider(
                        "Umbral de Alerta (Envío de Correos SMTP) (%)", 
                        min_value=50, max_value=100, 
                        value=int(config_activa.get("umbral_correo", 70)),
                        help="Qué tan exigente es SARA para disparar notificaciones."
                    )
                    
                    bl_list = config_activa.get("blacklist_palabras", [])
                    blacklist_str = ", ".join(bl_list) if isinstance(bl_list, list) else bl_list
                    blacklist_input = st.text_area(
                        "Blacklist: Palabras clave de exclusión", 
                        value=blacklist_str
                    )
                    
                    correos_list = config_activa.get("destinatarios_notificacion", [])
                    correos_str = ", ".join(correos_list) if isinstance(correos_list, list) else correos_list
                    destinatarios_input = st.text_area(
                        "Destinatarios del Notificador", 
                        value=correos_str
                    )
                    
                    estricto = st.toggle(
                        "Auditor Estricto Activado (Prompt V1)", 
                        value=config_activa.get("auditor_estricto", True)
                    )
                    
                    if st.form_submit_button("💾 Guardar y Aplicar Cambios"):
                        nuevas_palabras = [p.strip() for p in blacklist_input.split(",") if p.strip()]
                        nuevos_correos = [e.strip() for e in destinatarios_input.split(",") if e.strip()]
                        
                        payload = {
                            "umbral_pantalla": str(umbral_pantalla),
                            "umbral_correo": str(umbral_correo),
                            "blacklist_palabras": nuevas_palabras,
                            "destinatarios_notificacion": nuevos_correos,
                            "auditor_estricto": estricto
                        }
                        
                        put_resp = requests.put(f"{API_URL}/api/v1/config", json=payload)
                        if put_resp.status_code == 200:
                            st.success("¡Configuración inyectada a la base de datos con éxito!")
                            st.rerun()
                        else:
                            st.error("Error al comunicarse con la API para guardar los cambios.")
            else:
                st.warning("No se pudieron cargar los parámetros de la API.")
        except Exception as e:
            st.warning("Asegúrate de que la API esté corriendo para acceder a la configuración.")
            
    with tab_rag:
        st.subheader("📚 Alimentar Base Vectorial")
        st.info("Sube documentos (PDF o DOCX) para sumar al conocimiento institucional de SARA.")
        with st.form("form_rag", clear_on_submit=True):
            uploaded_file = st.file_uploader("Documento Institucional", type=["pdf", "docx"])
            submitted = st.form_submit_button("📥 Ingestar Documento")
            
            if submitted and uploaded_file is not None:
                # Guardar el archivo en la carpeta raw
                raw_dir = os.path.join(os.getcwd(), "data", "01_raw_icesi")
                os.makedirs(raw_dir, exist_ok=True)
                file_path = os.path.join(raw_dir, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success(f"¡Guardado con éxito! Archivo {uploaded_file.name} encolado para ingesta vectorial.")
                
    with tab_truth:
        st.subheader("🧠 Calibración de Precisión (Golden Truth)")
        st.markdown("Inyecta evaluaciones humanas aprobadas al `golden_truth.json` para testear el Recall y la Precisión de Llama 3.")
        with st.form("truth_form", clear_on_submit=True):
            gt_id = st.text_input("id_proceso", placeholder="ej. CO1.REQ.10278326")
            gt_obj = st.text_area("objeto_real", placeholder="Objeto de la licitación en SECOP")
            gt_via = st.slider("viabilidad_real_humana", min_value=0, max_value=100, value=0, help="Puntaje dado por un humano experto")
            gt_jus = st.text_area("justificacion_humana", placeholder="Explicación del humano experto...")
            
            if st.form_submit_button("➕ Agregar a Golden Truth"):
                if gt_id.strip() and gt_obj.strip():
                    gt_path = os.path.join(os.getcwd(), "data", "04_outputs", "golden_truth.json")
                    if os.path.exists(gt_path):
                        try:
                            with open(gt_path, "r", encoding="utf-8") as f:
                                gt_data = json.load(f)
                            
                            nuevo_registro = {
                                "id_proceso": gt_id,
                                "objeto_real": gt_obj,
                                "viabilidad_real_humana": gt_via,
                                "justificacion_humana": gt_jus
                            }
                            
                            # Validar duplicados
                            if any(item.get("id_proceso") == gt_id for item in gt_data):
                                st.warning(f"El id_proceso {gt_id} ya existe en el Golden Truth.")
                            else:
                                gt_data.append(nuevo_registro)
                                with open(gt_path, "w", encoding="utf-8") as f:
                                    json.dump(gt_data, f, ensure_ascii=False, indent=2)
                                st.success(f"¡Guardado con éxito! Registro {gt_id} añadido al Golden Truth.")
                        except Exception as e:
                            st.error(f"Error procesando golden_truth.json: {e}")
                    else:
                        st.error("No se encontró el archivo golden_truth.json en la ruta esperada.")
                else:
                    st.warning("⚠️ Por favor, llena al menos el ID y el Objeto del contrato.")

    with tab_ops:
        st.subheader("🚀 Orquestador Manual")
        st.warning("SARA evalúa automáticamente el día anterior (T-1) todos los días. Usa esto solo para procesos pasados no evaluados.")
        target_date = st.date_input("Target Date (Fecha a Evaluar)")
        limite = st.number_input("Límite de contratos (0 = Todo el día)", min_value=0, max_value=5000, value=5, help="Útil para hacer Dry Runs o pruebas sin saturar la GPU.")
        debug_mode = st.toggle("Habilitar Logs en Vivo (Modo Debug)")
        
        if st.button("▶️ Forzar Ejecución del Pipeline", type="primary"):
            cmd = f"python run_pipeline.py --date {target_date.strftime('%Y-%m-%d')} --limit {limite}"
            
            if debug_mode:
                st.info(f"Modo Debug Activado. Ejecutando: `{cmd}`")
                log_container = st.empty()
                log_text = ""
                with st.spinner("Procesando y observando en vivo... (Esto bloqueará la UI temporalmente)"):
                    import subprocess
                    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                    for line in process.stdout:
                        log_text += line
                        log_container.code(log_text)
                    process.wait()
                st.success("Ejecución finalizada")
            else:
                st.info(f"Modo Silencioso. Ejecutando en background: `{cmd}`")
                with st.spinner("Procesando en background..."):
                    import subprocess
                    subprocess.run(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                st.success("Ejecución finalizada")

# ==========================================
# 5. VISTA: EMPLEADO (Radar y Manual)
# ==========================================
else:
    # 3era Imagen: Banner Original
    banner_path = os.path.join("assets", "banner.png")
    if os.path.exists(banner_path):
        st.image(banner_path, use_container_width=True)

    st.title("Sistema SARA - Oportunidades SECOP II")
    
    tab1, tab2 = st.tabs(["📊 Radar Automático", "⚙️ Evaluación Manual (Debug)"])
    
    with tab1:
        st.markdown("### Oportunidades Detectadas por el Pipeline Automático")
        try:
            # Obtenemos el umbral de pantalla actual para pintar los colores dinámicamente
            cfg_resp = requests.get(f"{API_URL}/api/v1/config", timeout=5)
            u_pantalla = int(cfg_resp.json().get("umbral_pantalla", 70)) if cfg_resp.status_code == 200 else 70
            
            resp = requests.get(f"{API_URL}/api/v1/opportunities", timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                if data:
                    df = pd.DataFrame(data)
                    df_visual = df.copy()
                    
                    if 'notificado' in df_visual.columns:
                        df_visual['notificado'] = df_visual['notificado'].fillna(0).apply(lambda x: "✅ Enviado" if x == 1 else "⏳ Pendiente")
                    
                    # Casting estricto para evitar cuelgues numéricos
                    df_visual['viabilidad'] = pd.to_numeric(df_visual['viabilidad'], errors='coerce').fillna(0).astype(int)
                    df['viabilidad'] = pd.to_numeric(df['viabilidad'], errors='coerce').fillna(0).astype(int)
                    
                    def color_viabilidad(val):
                        try:
                            val = int(val)
                            if val >= 70:
                                return 'background-color: #d4edda; color: #155724'  # Verde
                            elif val >= 50:
                                return 'background-color: #fff3cd; color: #856404'  # Naranja/Amarillo
                            else:
                                return 'background-color: #f8d7da; color: #721c24'  # Rojo
                        except (ValueError, TypeError):
                            return ''
                            
                    # applymap is deprecated in newer pandas, use map
                    styled_df = df_visual.style.map(color_viabilidad, subset=['viabilidad']) if hasattr(df_visual.style, 'map') else df_visual.style.applymap(color_viabilidad, subset=['viabilidad'])
                    
                    st.dataframe(styled_df, use_container_width=True, column_config={
                        "viabilidad": st.column_config.NumberColumn("Viabilidad (%)", format="%d%%"),
                        "notificado": st.column_config.TextColumn("Estado Correo")
                    })
                    
                    st.markdown("---")
                    st.markdown("### 📝 Visor de Borradores")
                    viables = df[df['viabilidad'] >= u_pantalla]['id_proceso'].tolist()
                    if viables:
                        seleccion = st.selectbox("Selecciona un ID:", ["-- Seleccione --"] + viables)
                        if seleccion != "-- Seleccione --":
                            ruta_md = os.path.join(os.getcwd(), "data", "05_propuestas", f"{seleccion}.md")
                            if os.path.exists(ruta_md):
                                with open(ruta_md, "r", encoding="utf-8") as f:
                                    st.markdown(f"<h4 style='color: #004b87;'>Propuesta: {seleccion}</h4>", unsafe_allow_html=True)
                                    st.markdown(f.read())
                            else:
                                st.warning(f"No se encontró el borrador para {seleccion}.")
                else:
                    st.info("El radar aún no ha procesado oportunidades o la tabla está vacía.")
            else:
                st.error("Error al consultar la base de datos vía API.")
        except Exception as e:
            st.error("Error de conexión con la API de FastAPI.")

    with tab2:
        st.markdown("Pegue el registro de SECOP II para forzar una evaluación manual.")
        ejemplo_json = """{
  "id_del_proceso": "PRUEBA-ICESI-001",
  "nombre_del_procedimiento": "Desarrollo de IA",
  "modalidad_de_contratacion": "Mínima cuantía",
  "nombre_de_la_entidad": "Alcaldía de Cali"
}"""
        json_input = st.text_area("JSON SECOP II", value=ejemplo_json, height=150)
        if st.button("🧠 Evaluar", type="primary"):
            try:
                secop_record = json.loads(json_input)
                with st.spinner("Analizando..."):
                    res = requests.post(f"{API_URL}/api/v1/evaluate_opportunity", json=secop_record, timeout=120)
                    if res.status_code == 200:
                        ev = res.json()
                        st.success(f"Viabilidad: {ev.get('porcentaje_viabilidad')}%")
                        st.info(ev.get("justificacion_estrategica", ""))
                    else:
                        st.error("Falló la evaluación.")
            except Exception as e:
                st.error(f"JSON inválido o error de red: {e}")
