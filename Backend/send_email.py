import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from db.models.news import News

# Configuración del servidor de correo
SMTP_SERVER = "smtp.gmail.com"  # Cambia esto según tu proveedor de correo
SMTP_PORT = 587  # Normalmente 587 para TLS o 465 para SSL
SMTP_USER = "notstartupanymore@gmail.com"  # Tu dirección de correo
SMTP_PASSWORD = "hlfm inpu bzel zuuk"  # Usa variables de entorno o un gestor seguro

def send_email(user_email: str, news_list: list[News]):
    """Envía un correo con las noticias al usuario."""
    if not news_list:
        print(f"No hay noticias para enviar a {user_email}.")
        return
    
    # Crear el mensaje de correo
    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = user_email
    msg["Subject"] = "📢 Boletín de Noticias Empresariales"

    # Construir el cuerpo del correo en formato HTML
    news_items = "".join([
        f"<li><b>{news.title}</b> ({news.company}) - {news.details}</li>"
        for news in news_list
    ])
    
    html_content = f"""
    <html>
    <body>
        <h2>📢 Noticias Empresariales Recientes</h2>
        <p>Hola, aquí tienes las últimas noticias relevantes según tus suscripciones:</p>
        <ul>{news_items}</ul>
        <p>Gracias por suscribirte a nuestro boletín.</p>
    </body>
    </html>
    """

    msg.attach(MIMEText(html_content, "html"))

    # Conectar con el servidor SMTP y enviar el correo
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Habilitar TLS (seguro)
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, user_email, msg.as_string())
        server.quit()
        print(f"Correo enviado correctamente a {user_email}")
    except Exception as e:
        print(f"Error al enviar correo a {user_email}: {e}")
