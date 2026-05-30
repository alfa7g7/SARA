# Arquitectura de Red: Políticas y Límites SMTP

Este documento detalla las cuotas diarias de envío (Rate Limits) establecidas por los principales proveedores de correo electrónico. Es vital para planificar el paso a producción de SARA según la infraestructura que elija la Universidad Icesi.

## 1. Proveedores Tradicionales (Cuentas Personales y Corporativas)

### 📧 Gmail (Cuenta Gratuita @gmail.com)
- **Límite Diario:** 500 correos por día.
- **Límite de Frecuencia (Rate):** Aproximadamente 10-20 por minuto (variable según reputación).
- **Caso de Uso:** Desarrollo, pruebas, y flujos pequeños (como enviar 20-30 alertas diarias a un equipo).
- **Riesgo:** Alta susceptibilidad al baneo automático si se envían en ráfaga (Connection unexpectedly closed).

### 🎓 Google Workspace for Education (Cuenta Icesi)
- **Límite Diario:** 2,000 correos diarios por buzón (o hasta 10,000 para envíos internos dentro del mismo dominio `@icesi.edu.co`).
- **Caso de Uso:** Despliegue en producción para notificaciones a profesores o facultades.

### 💼 Microsoft 365 (Entorno Corporativo)
- **Límite Diario:** 10,000 destinatarios por día.
- **Límite de Frecuencia:** 30 mensajes por minuto.
- **Caso de Uso:** Excelente para producción interna si la Universidad maneja su directorio en Azure AD/Office 365.

---

## 2. Servicios Especializados (SMTP Relays / Transaccionales)

Si SARA escala a miles de contratos diarios y debe notificar a cientos de investigadores, se debe migrar a un servicio SMTP especializado.

### 🚀 SendGrid (Twilio)
- **Límite Diario:** 100 correos/día en capa gratuita. Millones en capa de pago.
- **Límite de Frecuencia:** Más de 10,000 por minuto (depende del plan).
- **Ventaja:** Manejo automático de colas (Queueing), métricas de apertura (Open Rate) y altísima reputación IP para no caer en Spam.

### ☁️ Amazon SES (Simple Email Service)
- **Límite Diario:** 62,000 correos gratis por mes (si se envía desde una instancia EC2).
- **Límite de Frecuencia:** Inicia en 14 correos por segundo y sube progresivamente.
- **Ventaja:** Extremadamente económico y robusto, ideal para arquitecturas cloud nativas.
