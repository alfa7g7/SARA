import os
import sqlite3
import smtplib
import time
from datetime import datetime
from email.message import EmailMessage
from dotenv import load_dotenv
from src.utils.db_manager import get_db_connection

class SARANotifier:
    def __init__(self, db_path="data/historial_sara.sqlite3", propuestas_dir="data/05_propuestas"):
        load_dotenv()
        self.db_path = os.path.join(os.getcwd(), db_path)
        self.propuestas_dir = os.path.join(os.getcwd(), propuestas_dir)
        
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.sender_password = os.getenv("SENDER_PASSWORD")
        self.receiver_email = os.getenv("RECEIVER_EMAIL")
        
    def get_emails_sent_today(self):
        """Cuenta los correos notificados el día de hoy."""
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM evaluaciones WHERE DATE(fecha_notificacion) = DATE('now', 'localtime') AND notificado = 1")
        count = cursor.fetchone()[0]
        conn.close()
        return count
        
    def get_pending_notifications(self):
        """Obtiene las oportunidades viables (>=70) que no han sido notificadas."""
        conn = get_db_connection(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        from src.utils.db_manager import get_config
        config = get_config()
        umbral_correo = int(config.get("umbral_correo", 70))

        # FIX: Se remueve el filtro de fecha (date) por discrepancia entre UTC de SQLite 
        # y local de Python. Además, usamos IFNULL para atrapar posibles valores NULL.
        cursor.execute("""
            SELECT id_proceso, entidad, objeto, viabilidad, referencia, url 
            FROM evaluaciones 
            WHERE viabilidad >= ? 
              AND IFNULL(notificado, 0) = 0 
        """, (umbral_correo,))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
        
    def mark_as_notified(self, id_proceso):
        """Marca una oportunidad como notificada en la base de datos."""
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE evaluaciones SET notificado = 1, fecha_notificacion = CURRENT_TIMESTAMP WHERE id_proceso = ?", (id_proceso,))
        conn.commit()
        conn.close()

    def send_notification(self, oportunidad, server=None):
        """Arma y envía el correo electrónico en formato HTML con adjuntos."""
        if not all([self.sender_email, self.sender_password, self.receiver_email]):
            print("[Notifier] Faltan credenciales SMTP en el archivo .env. Ignorando notificación.")
            return False
            
        id_proceso = oportunidad['id_proceso']
        entidad = oportunidad['entidad']
        viabilidad = oportunidad['viabilidad']
        objeto = oportunidad['objeto']
        referencia = oportunidad.get('referencia', 'No disponible')
        url = oportunidad.get('url', '#')
        
        msg = EmailMessage()
        msg['Subject'] = f"SARA: 🚀 Nueva Oportunidad Viable SECOP - {entidad} ({viabilidad}%)"
        msg['From'] = self.sender_email
        msg['To'] = self.receiver_email
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
                <h2 style="color: #004b87; border-bottom: 2px solid #004b87; padding-bottom: 10px;">SARA - Alerta de Negocio</h2>
                <p>Hola,</p>
                <p>El Sistema SARA ha identificado un nuevo proceso de contratación con un índice de viabilidad favorable para la Universidad Icesi y ha generado el borrador de la propuesta correspondiente.</p>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-left: 5px solid #28a745; margin: 25px 0; border-radius: 4px;">
                    <p style="margin: 5px 0;"><strong>ID del Proceso:</strong> <span style="color: #555;">{id_proceso}</span></p>
                    <p style="margin: 5px 0;"><strong>Referencia:</strong> <span style="color: #555;">{referencia}</span></p>
                    <p style="margin: 5px 0;"><strong>Entidad:</strong> <span style="color: #555;">{entidad}</span></p>
                    <p style="margin: 5px 0;"><strong>Viabilidad Auditada:</strong> <span style="font-size: 1.3em; color: #28a745; font-weight: bold;">{viabilidad}%</span></p>
                    <p style="margin: 5px 0; margin-top: 15px;"><strong>Objeto del Contrato:</strong><br><span style="color: #555; font-style: italic;">{objeto}</span></p>
                    <p style="margin: 5px 0; margin-top: 10px;">
                        <a href="{url}" target="_blank" style="display: inline-block; padding: 8px 12px; background-color: #004b87; color: #fff; text-decoration: none; border-radius: 4px; font-weight: bold;">🔍 Ver en SECOP II</a>
                    </p>
                </div>
                
                <p style="font-weight: bold; color: #d9534f;">📎 Adjunto a este correo encontrarás el borrador oficial de la propuesta generado automáticamente en formato Markdown (.md).</p>
                <br>
                <p>Atentamente,<br><strong>SARA</strong><br><em>Sistema Analítico de Recomendación de Adjudicaciones</em></p>
            </body>
        </html>
        """
        # Fallback para clientes que no soportan HTML
        msg.set_content(f"SARA ha detectado una oportunidad de {viabilidad}% para {entidad} ({id_proceso}). Revisa el adjunto.")
        msg.add_alternative(html_content, subtype='html')
        
        # Adjuntar archivo .md
        md_file = os.path.join(self.propuestas_dir, f"{id_proceso}.md")
        if os.path.exists(md_file):
            with open(md_file, 'rb') as f:
                md_data = f.read()
            msg.add_attachment(md_data, maintype='text', subtype='markdown', filename=f"Propuesta_Icesi_{id_proceso}.md")
        else:
            print(f"[Notifier] Advertencia: No se encontró el borrador {md_file} para adjuntar.")
            
        # Enviar correo vía SMTP TLS
        try:
            if server:
                # Usa la conexión existente (Connection Pooling)
                server.send_message(msg)
            else:
                # Abre conexión independiente (Fallback)
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as independent_server:
                    independent_server.starttls()
                    independent_server.login(self.sender_email, self.sender_password)
                    independent_server.send_message(msg)
            
            print(f"[Notifier] ✉️ Correo enviado exitosamente a {self.receiver_email} para {id_proceso}")
            self.mark_as_notified(id_proceso)
            return True
        except Exception as e:
            error_msg = str(e).lower()
            print(f"[Notifier] ❌ Error enviando correo para {id_proceso}: {e}")
            if "limit" in error_msg or "exceeded" in error_msg or "connection" in error_msg:
                print(f"[Notifier] 🛑 CIRCUIT BREAKER ACTIVADO: Deteniendo cola completa por fallo de cuota/conexión.")
                raise e
            return False

def run_notifications():
    print("\n=== 📬 SARA NOTIFIER: Revisando Bandeja de Salida ===")
    notifier = SARANotifier()
    pendientes = notifier.get_pending_notifications()
    
    if not pendientes:
        print("[Notifier] No hay correos pendientes por enviar para el día de hoy.")
        return
        
    print(f"[Notifier] Se detectaron {len(pendientes)} oportunidades viables sin notificar.")
    
    if not all([notifier.sender_email, notifier.sender_password, notifier.receiver_email]):
        print("[Notifier] Faltan credenciales SMTP en el archivo .env. Abortando.")
        return
        
    try:
        # Límite Duro de Seguridad (Proteger cuenta gratuita)
        MAX_EMAILS_PER_RUN = 400
        enviados_hoy = notifier.get_emails_sent_today()
        
        if enviados_hoy >= MAX_EMAILS_PER_RUN:
            print("[Notifier] Cuota diaria excedida. Correos pausados hasta mañana.")
            return
            
        # CONNECTION POOLING: Abriendo la bóveda SMTP una sola vez
        with smtplib.SMTP(notifier.smtp_server, notifier.smtp_port) as server:
            server.starttls()
            server.login(notifier.sender_email, notifier.sender_password)
            
            for op in pendientes:
                if enviados_hoy >= MAX_EMAILS_PER_RUN:
                    print("[Notifier] Cuota diaria excedida. Correos pausados hasta mañana.")
                    break
                    
                if notifier.send_notification(op, server=server):
                    enviados_hoy += 1
                    
                time.sleep(2)  # THROTTLING: Escudo anti-spam
                
    except Exception as e:
        print(f"[Notifier] Error crítico de red conectando al servidor SMTP maestro: {e}")
        
if __name__ == "__main__":
    run_notifications()
