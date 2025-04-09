import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from db.models.news import News

class MailSender():
    """Clase para manejar el envío de correos electrónicos."""
    
    def __init__(self, smtp_server: str, smtp_port: int, smtp_user: str, smtp_password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
    
    def send_email(self, user_email: str, news_list: list[News]):
        """Envía un correo con las noticias al usuario."""
        if not news_list:
            print(f"No hay noticias para enviar a {user_email}.")
            return
        
        # Crear el mensaje de correo
        msg = MIMEMultipart()
        msg["From"] = self.smtp_user
        msg["To"] = user_email
        msg["Subject"] = "\U0001F4E2 Boletín de Noticias Empresariales"

        # Construir el cuerpo del correo en formato HTML
        news_items = "".join([
            f"<li><b>{news.title}</b> ({news.company}) - {news.details}</li>"
            for news in news_list
        ])
        
        html_content = f"""
        <html>
        <body>
            <h2>\U0001F4E2 Noticias Empresariales Recientes</h2>
            <p>Hola, aquí tienes las últimas noticias relevantes según tus suscripciones:</p>
            <ul>{news_items}</ul>
            <p>Gracias por suscribirte a nuestro boletín.</p>
        </body>
        </html>
        """

        msg.attach(MIMEText(html_content, "html"))

        # Conectar con el servidor SMTP y enviar el correo
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Habilitar TLS (seguro)
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.smtp_user, user_email, msg.as_string())
            print(f"Correo enviado correctamente a {user_email}")
        except Exception as e:
            print(f"Error al enviar correo a {user_email}: {e}")

    def contact_email(self, user_email: str, name:str , mail_in_form:str, message: str):

        msg = MIMEText(f"Nombre: {name}\nEmail: {mail_in_form}\nMensaje: {message}")
        msg["From"] = self.smtp_user
        msg["To"] = user_email
        msg["Subject"] = "\U0001F4E2 Mensaje de usuario en seccion contactanos"

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Habilitar TLS (seguro)
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.smtp_user, user_email, msg.as_string())
            print(f"Correo enviado correctamente a {user_email}")
        except Exception as e:
            print(f"Error al enviar correo a {user_email}: {e}")

    def send_verification_email(self, user_email: str, name: str, verification_url: str):
        msg = MIMEMultipart()
        msg["From"] = self.smtp_user
        msg["To"] = user_email
        msg["Subject"] = "📩 Verifica tu cuenta en NotaStartupAnymore"

        html_content = f"""
        <html>
            <body>
                <p>Hola <b>{name}</b>,</p>
                <p>Gracias por registrarte. Para activar tu cuenta, haz clic en el siguiente enlace:</p>
                <p><a href="{verification_url}">Verificar cuenta</a></p>
                <p>Si no te registraste, puedes ignorar este correo.</p>
            </body>
        </html>
        """
        msg.attach(MIMEText(html_content, "html"))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.smtp_user, user_email, msg.as_string())
            print(f"Correo de verificación enviado a {user_email}")
        except Exception as e:
            print(f"Error al enviar correo de verificación a {user_email}: {e}")


"""
if __name__ == "__main__":
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SMTP_USER = "notstartupanymore@gmail.com"
    SMTP_PASSWORD = "hlfm inpu bzel zuuk"  # Usa variables de entorno en producción

    mail_sender = MailSender(SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD)
    
    # Ejemplo de uso con datos de prueba
    dummy_news = [News(title="Nueva Startup", company="TechCorp", details="Ha conseguido una gran inversión."),
                  News(title="Cambio de sede", company="BigCompany", details="Se ha trasladado a una nueva ciudad.")]
    
    mail_sender.send_email("destinatario@example.com", dummy_news)
"""