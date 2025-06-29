import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html import escape
from typing import List
from db.models.news import News

class MailSender:
    """Clase para manejar el envío de correos electrónicos."""
    
    def __init__(self, smtp_server: str, smtp_port: int, smtp_user: str, smtp_password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
    
    def send_email(self, user_email: str, news_list: List[News], user_name: str = "Usuario"):
        """Envía un boletín de noticias empresariales al usuario en formato HTML estilizado.

        Args:
            user_email (str): Dirección de correo del destinatario.
            news_list (List[News]): Lista de noticias a incluir en el boletín.
            user_name (str, optional): Nombre del usuario para personalización. Por defecto, "Usuario".
        """
        if not news_list:
            print(f"No hay noticias para enviar a {user_email}.")
            return
        
        # Validar correo electrónico básico
        if not self._is_valid_email(user_email):
            print(f"Correo inválido: {user_email}")
            return

        # Crear el mensaje de correo
        msg = MIMEMultipart()
        msg["From"] = self.smtp_user
        msg["To"] = user_email
        msg["Subject"] = "📢 Boletín de Noticias Empresariales - NotaStartupAnymore"

        # Agrupar noticias por tema
        news_by_topic = {}
        for news in news_list:
            topic = news.topic if news.topic != "ninguno" else "Otros"
            if topic not in news_by_topic:
                news_by_topic[topic] = []
            news_by_topic[topic].append(news)

        news_sections = ""
        for topic, news_items in news_by_topic.items():
            news_items_html = "".join([
                f"""
                <li style="margin-bottom: 15px;">
                    <strong>{escape(news.title)}</strong> ({escape(news.company)})<br>
                    {escape(news.details)}<br>
                    <small style="color: #6b7280;">Publicado: {escape(str(news.date))}</small>
                    {'<br><a href="' + escape(news.url) + '" style="color: #3b82f6; text-decoration: none;">Leer más</a>' if hasattr(news, 'url') and news.url else ''}
                </li>
                """
                for news in news_items
            ])
            news_sections += f"""
            <h3 style="font-size: 18px; color: #1f2937; margin-top: 20px; margin-bottom: 10px;">{escape(topic)}</h3>
            <ul style="list-style-type: none; padding-left: 0;">{news_items_html}</ul>
            """

        html_content = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f3f4f6;">
            <div style="max-width: 600px; margin: 20px auto; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); overflow: hidden;">
                <!-- Encabezado -->
                <div style="background-color: #3b82f6; padding: 20px; text-align: center;">
                    <h1 style="color: #ffffff; font-size: 24px; margin: 0;">NotaStartupAnymore</h1>
                    <p style="color: #dbeafe; font-size: 14px; margin: 5px 0;">Tu fuente de noticias empresariales</p>
                </div>
                <!-- Contenido -->
                <div style="padding: 20px;">
                    <h2 style="font-size: 20px; color: #1f2937; margin-top: 0;">¡Hola, {escape(user_name)}!</h2>
                    <p style="color: #4b5563; line-height: 1.5;">Aquí tienes las últimas noticias relevantes según tus suscripciones:</p>
                    {news_sections}
                </div>
                <!-- Pie de página -->
                <div style="background-color: #f9fafb; padding: 15px; text-align: center; font-size: 12px; color: #6b7280;">
                    <p style="margin: 0;">© 2025 NotaStartupAnymore. Todos los derechos reservados.</p>
                    <p style="margin: 5px 0;">
                        <a href="https://notastartupanymore-front.onrender.com/login" style="color: #3b82f6; text-decoration: none;">Gestionar suscripciones</a> | 
                        <a href="https://notastartupanymore-front.onrender.com/#contactanos" style="color: #3b82f6; text-decoration: none;">Contáctanos</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(html_content, "html"))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.smtp_user, user_email, msg.as_string())
            print(f"Correo enviado correctamente a {user_email}")
        except smtplib.SMTPException as e:
            print(f"Error SMTP al enviar correo a {user_email}: {e}")
        except Exception as e:
            print(f"Error inesperado al enviar correo a {user_email}: {e}")

    def _is_valid_email(self, email: str) -> bool:
        """Valida si una dirección de correo es válida (formato básico)."""
        import re
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    def contact_email(self, user_email: str, name: str, mail_in_form: str, message: str):
        """Envía un correo de contacto desde el formulario."""
        msg = MIMEText(f"Nombre: {escape(name)}\nEmail: {escape(mail_in_form)}\nMensaje: {escape(message)}")
        msg["From"] = self.smtp_user
        msg["To"] = user_email
        msg["Subject"] = "📧 Mensaje de usuario en sección Contáctanos"

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.smtp_user, user_email, msg.as_string())
            print(f"Correo enviado correctamente a {user_email}")
        except smtplib.SMTPException as e:
            print(f"Error SMTP al enviar correo a {user_email}: {e}")
        except Exception as e:
            print(f"Error inesperado al enviar correo a {user_email}: {e}")

    def send_verification_email(self, user_email: str, name: str, verification_url: str):
        """Envía un correo de verificación de cuenta."""
        msg = MIMEMultipart()
        msg["From"] = self.smtp_user
        msg["To"] = user_email
        msg["Subject"] = "📩 Verifica tu cuenta en NotaStartupAnymore"

        html_content = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f3f4f6;">
            <div style="max-width: 600px; margin: 20px auto; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); overflow: hidden;">
                <div style="background-color: #3b82f6; padding: 20px; text-align: center;">
                    <h1 style="color: #ffffff; font-size: 24px; margin: 0;">NotaStartupAnymore</h1>
                </div>
                <div style="padding: 20px;">
                    <h2 style="font-size: 20px; color: #1f2937;">¡Hola, {escape(name)}!</h2>
                    <p style="color: #4b5563; line-height: 1.5;">Gracias por registrarte.
                    <p style="color: #4b5563; line-height: 1.5;">Haz clic en el siguiente enlace para verificar tu cuenta:</p>
                    <p style="margin: 20px 0;">
                        <a href="{escape(verification_url)}" style="display: inline-block; padding: 10px 20px; background-color: #3b82f6; color: #ffffff; text-decoration: none; border-radius: 5px;">Verificar cuenta</a>
                    </p>
                    <p style="color: #4b5563; line-height: 1.5;">Si no te registraste, puedes ignorar este correo.</p>
                </div>
                <div style="background-color: #f9fafb; padding: 15px; text-align: center; font-size: 12px; color: #6b7280;">
                    <p style="margin: 0;">© 2025 NotaStartupAnymore. Todos los derechos reservados.</p>
                </div>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(html_content, "html"))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.smtp_user, user_email, msg.as_string())
            print(f"Correo de verificación enviado a {user_email}")
        except smtplib.SMTPException as e:
            print(f"Error SMTP al enviar correo de verificación a {user_email}: {e}")
        except Exception as e:
            print(f"Error inesperado al enviar correo de verificación a {user_email}: {e}")