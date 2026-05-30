import os
import smtplib
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    
    if not all([sender_email, sender_password]):
        print("❌ Error: Faltan credenciales SENDER_EMAIL o SENDER_PASSWORD en .env")
        return
        
    print(f"=== PRUEBA DE DIAGNÓSTICO SMTP DE BAJO NIVEL ===")
    print(f"Servidor: {smtp_server}:{smtp_port}")
    print(f"Usuario: {sender_email}")
    print("Iniciando conexión con server.set_debuglevel(2)...\n")
    
    try:
        # Se establece la conexión con nivel máximo de depuración
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=15)
        server.set_debuglevel(2)
        
        print("\n>> Ejecutando EHLO/HELO inicial...")
        server.ehlo()
        
        print("\n>> Ejecutando STARTTLS...")
        server.starttls()
        
        print("\n>> Ejecutando EHLO/HELO tras TLS...")
        server.ehlo()
        
        print("\n>> Intentando Autenticación (LOGIN)...")
        server.login(sender_email, sender_password)
        
        print("\n✅ ÉXITO: Conexión y Autenticación completadas sin ser baneados.")
        
        server.quit()
    except smtplib.SMTPAuthenticationError as e:
        print(f"\n❌ Error de Autenticación (Credenciales revocadas o bloqueo por seguridad): {e}")
    except smtplib.SMTPConnectError as e:
        print(f"\n❌ Error de Conexión (IP Baneada temporalmente o firewall): {e}")
    except smtplib.SMTPServerDisconnected as e:
        print(f"\n❌ Servidor Desconectó Inesperadamente (Drop de la conexión por Rate Limiting estricto): {e}")
    except Exception as e:
        print(f"\n❌ Error General o Excepción Nativa: {e}")

if __name__ == "__main__":
    main()
