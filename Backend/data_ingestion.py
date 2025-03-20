import re
import json
from ollama import chat
from ollama import ChatResponse
from db.models.news import News
from db.models.company import Company
from db.schemas.user import users_schema
from db.client import db_client
from send_email import MailSender
import feedparser

SMTP_SERVER = "smtp.gmail.com"  # Cambia esto según tu proveedor de correo
SMTP_PORT = 587  # Normalmente 587 para TLS o 465 para SSL
SMTP_USER = "notstartupanymore@gmail.com"  # Tu dirección de correo
SMTP_PASSWORD = "hlfm inpu bzel zuuk"  # Usa variables de entorno o un gestor seguro

cartero = MailSender(SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD )

class Ingestion():
    def __init__(self, url, contador = 0):
        self.feed = feedparser.parse(url)
        self.lista_noticias: list[News] = []
        self.contador = contador
    
    def change_source_and_reset(self, url_nueva):
        self.feed = feedparser.parse(url_nueva)
        self.lista_noticias = []
        self.contador = 0

    def insert_db_news(self, noticia: News):
        news_dict = dict(noticia)
        del news_dict["id"]
        db_client.local.news.insert_one(news_dict)

    def insert_db_company(self, company: Company):
        company_dict = dict(company)
        del company_dict["id"]
        db_client.local.companies.insert_one(company_dict)

    def search_company(self, company_name: str) -> Company | None:
        company_data = db_client.local.companies.find_one({"name": company_name})
        if company_data:
            return Company(**company_data)
        return None
    
    def send_newsletters(self, news_list: list[News]):
        users_cursor = db_client.local.users.find()
        users = users_schema(users_cursor)

        for user in users:
            user_subscriptions = user.get("subscriptions", [])
            user_news = []

            for news in news_list:
                if news.topic in user_subscriptions:
                    user_news.append(news)

            if user_news:
                print(f"Enviando correo a {user['email']} con {len(user_news)} noticias.")
                cartero.send_email(user["email"], user_news)

    def extract_json(self, content: str):
        # Busca el JSON dentro de la respuesta
        match = re.search(r'({.*})', content, re.DOTALL)
        if match:
            return match.group(0)
        return None
    
    def data_ingestion(self):
        for entry in self.feed.entries[:10]:
            print(f"Noticia {self.contador}")
            titulo = entry.title
            print(titulo)
            print("\n")
            descripcion = entry.description
            print(descripcion)
            print("\n")
            response: ChatResponse = chat(model='deepseek-coder-v2:16b', messages=[
                {
                    'role': 'system',
                    'content': (
                        "Eres un especialista en noticias sobre empresas. "
                        "Tu trabajo consiste en determinar si ciertas noticias están relacionadas con empresas o no, "
                        "y si lo están, debes decidir si encajan en alguno de estos tres temas: "
                        "\"Creación de una nueva empresa\", \"Contratación abundante de empleados por parte de una empresa\" o "
                        "\"Cambio de sede de una empresa\". En caso de que no esté relacionada con ninguno de estos tres temas, "
                        "el tema será \"ninguno\". Responde únicamente en formato JSON como se muestra en el siguiente ejemplo, "
                        "sin ningún texto adicional ni comillas triples:\n\n"
                        "Ejemplo:\n"
                        '{ "noticia": "Vega Chargers cierra una ronda de cinco millones con sus socios", '
                        '"tema":"ninguno", "empresa": "Vega Chargers", "tipo_empresa": Desconocido, "detalles": "ninguno", "razones":"No está relacionada con ninguno de los temas que buscamos"}\n\n'
                        "Los detalles serán una breve cadena de texto. "
                        "En el campo \"tipo_empresa\" incluiremos el sector al que se dedica, Ejemplos:\"Hardware\", \"Agricola\", \"Ganaderia\", \"Textil\", \"Alimentacion\", \"Software\", \"Entretenimiento\", etc. En caso de que no haya una evidencia y no podamos saber esto con exactitud este campo será \"Desconocido\" "
                        "El cerrar una ronda de cierta cantidad de millones, invertir millones, ganar o recaudar cierta cantidad de beneficios, etc, no se considerará como ninguno de los tres temas que estamos buscando y el tema seleccionado será \"ninguno\""
                        "En caso de que no haya ninguna empresa relacionada, el campo empresa será \"ninguna\". Responde únicamente con el JSON válido."

                    )
                },
                {
                    'role': 'user',
                    'content': f"Titular: {titulo}    Descripción:{descripcion}\n",
                },
            ])

            try:
                json_content = self.extract_json(response['message']['content'])
                if json_content:
                    json_response = json.loads(json_content)
                    print(json_response)
                    tema = json_response.get("tema", "ninguno")
                    company_name = json_response.get("empresa", "Desconocida")
                    company_type = json_response.get("tipo_empresa", "Desconocido")

                    if tema != "ninguno":
                        existing_company = self.search_company(company_name)
                        if not existing_company and (company_name != "Desconocida" and company_name != "ninguna"):
                            new_company = Company(name=company_name, type=company_type, details="Desconocidos")
                            self.insert_db_company(new_company)
                            print(f"Compañía '{company_name}' insertada en la base de datos.")

                        noticia = News(
                            company=company_name,
                            title=titulo,
                            topic=tema,
                            details=json_response.get("detalles", "Ninguno")
                        )
                        self.insert_db_news(noticia)
                        print(f"Noticia '{titulo}' insertada en la base de datos.")
                        self.lista_noticias.append(noticia)
                    else:
                        print(f"Noticia '{titulo}' no relacionada con los temas especificados. No se insertará en la base de datos.")
                else:
                    print(f"No se encontró un JSON válido en la respuesta de la IA.")
            except json.JSONDecodeError as e:
                print(f"Error al decodificar JSON para la noticia '{titulo}': {e}")
                print(response['message']['content'])
                print(f"\nJSON extraído: {json_content}")

            self.contador += 1
            

        self.send_newsletters(self.lista_noticias)
    



