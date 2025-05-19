import re
import requests
import os
import json
from ollama import chat
from datetime import datetime
from ollama import ChatResponse
from bs4 import BeautifulSoup
from db.models.news import News
from db.models.company import Company
from db.schemas.user import users_schema
from db.client import db_client
from send_email import MailSender
from typing import Optional
import feedparser
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY_GOOGLE_NEWS")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT") 
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

cartero = MailSender(SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD )

JWT_SECRET = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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
        db_client.news.insert_one(news_dict)

    def insert_db_company(self, company: Company):
        company_dict = dict(company)
        del company_dict["id"]
        db_client.companies.insert_one(company_dict)

    def search_company(self, company_name: str) -> Optional[Company]:
        company_data = db_client.companies.find_one({"name": company_name})
        if company_data:
            return Company(**company_data)
        return None
    
    def send_newsletters(self, news_list: list[News]):
        users_cursor = db_client.users.find()
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

    
    def data_ingestion_rss(self):
        for entry in self.feed.entries[:10]:
            print(f"Noticia {self.contador}")
            titulo = entry.title
            print(titulo)
            print("\n")
            descripcion = entry.description
            fecha = entry.get("published", "Fecha no disponible")
            fecha = datetime.strptime(fecha, "%a, %d %b %Y %H:%M:%S %z").strftime("%Y-%m-%d %H:%M:%S")
            url = entry.get("guid", "url no disponible")
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
                        '"tema":"ninguno", "empresa": "Vega Chargers", "tipo_empresa": "Desconocido", "detalles": "ninguno", "ambito": "desconocido", "region": "desconocido", "razones":"No está relacionada con ninguno de los temas que buscamos"}\n\n'
                        "Los detalles serán una breve cadena de texto. "
                        'El campo ambito lo rellenaremos con "Nacional" si se trata de una empresa española o "Internacional" en caso contrario, en caso de no tener informacion al respecto este campo sera "desconocido"'
                        'El campo region lo rellenaremos con "Nacion una localizacion mas concreta de la empresa en cuestion, Ejemplos: "Valencia", "Bilbao", "Paris". En caso de no tener informacion al respecto este campo sera "desconocido". En caso de que el campo ambito sea "desconocido" este campo region siempre sera "desconocido" tambien' 
                        '"En el campo empresa si se trata de varias las añadiremos seguidas de esta con , de la forma: "Empresa1, Empresa2, Empresa3, etc")"'
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
                    loc = json_response.get("ambito", "Desconocido")
                    reg = json_response.get("region", "Desconocido")

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
                            date = fecha,
                            location = loc,
                            region= reg,
                            url = url,
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

    
    def scrape_article(self, url, title, tema):
        """Extrae información de la noticia desde la URL usando web scraping."""
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")

            # Extraer contenido basado en etiquetas comunes en noticias
            paragraphs = soup.find_all("p")
            content = " ".join([p.get_text() for p in paragraphs])
            if len(content) > 1000:  # Limitamos a 1000 caracteres ya que de otra forma al ser un prompt demasiado grande tendremos un error de RAM
                content = content[:1000] + "..."

            if content:
                 response: ChatResponse = chat(model='deepseek-coder-v2:16b', messages=[
                {
                    'role': 'system',
                    'content': (
                        "Eres un especialista en noticias sobre empresas, vas a recibir una extensa noticia sobre una empresa"
                        "La noticia tratara sobre alguno de estos tres temas: \"Creación de una nueva empresa\", \"Contratación abundante de empleados por parte de una empresa\" o \"Cambio de sede de una empresa\" "
                        "Debes resumir la noticia y extraer los detalles más relevantes, excluyendo texto sin relevancia"
                        "Responde unicamente con un formato JSON que contenga los siguientes campos"
                        '{ "tema": "Tema sobre el que trata la noticia de los tres planteados", "empresa": "Nombre de la empresa de la que trata la noticia", "tipo_empresa": "Sector en el que trabaja la empresa", "detalles": "Breve resumen que contenga la informacion relevante de la noticia excluyendo texto sin importancia" , }\n\n'
                        "Deberas decidir si el tema proporcionado como tema provisional, realmente encaja con la noticia o no, en caso de que si que encaje en el campo tema del JSON dejaras el mismo tema que se proporciono como Tema provisional, si encaja mejor con alguno de los otros dos temas posibles pondrás el que mejor encaje y en caso de que finalmente no tenga que ver con nignuno de los tres pondrás \"ninguno\""
                    )
                },
                {
                    'role': 'user',
                    'content': f"Titular: {title}    Descripción:{content} Tema provisional:{tema}\n",
                },
            ])
                 
            else:
                return None
            
            try:
                json_content = self.extract_json(response['message']['content'])
                if json_content:
                    json_response = json.loads(json_content)
                    print("Noticia reevaluada: \n")
                    print(json_response)
                    topic = json_response.get("tema","ninguno")
                    tipo_empresa = json_response.get("tipo_empresa", "Desconocido")
                    details = json_response.get("detalles", "Desconocidos")

            except json.JSONDecodeError as e:
                print(f"Error procesando noticia '{title}': {e}")
                
            return topic, details, tipo_empresa
        
        except Exception as e:
            print(f"Error extrayendo información de {url}: {e}")
            return None
    
        
    def data_ingestion_google_news(self, query):
        url = f"https://newsapi.org/v2/everything?q={query}&apiKey={API_KEY}"
        response = requests.get(url)
        data = response.json()

        for article in data.get("articles", []):
            titulo = article["title"]
            descripcion = article.get("description", "")
            noticia_url = article["url"]
            fecha = article["publishedAt"]
            fecha = datetime.strptime(fecha, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M:%S")

            print(f"Procesando noticia: {titulo} \n")

            response_ai: ChatResponse = chat(model='deepseek-coder-v2:16b', messages=[
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
                        '"tema":"ninguno", "empresa": "Vega Chargers", "tipo_empresa": "Desconocido", "detalles": "ninguno", "ambito": "desconocido", "region": "desconocido", "razones":"No está relacionada con ninguno de los temas que buscamos"}\n\n'
                        "Los detalles serán una breve cadena de texto. "
                        'El campo ambito lo rellenaremos con "Nacional" si se trata de una empresa española o "Internacional" en caso contrario, en caso de no tener informacion al respecto este campo sera "desconocido"'
                        'El campo region lo rellenaremos con "Nacion una localizacion mas concreta de la empresa en cuestion, Ejemplos: "Valencia", "Bilbao", "Paris". En caso de no tener informacion al respecto este campo sera "desconocido". En caso de que el campo ambito sea "desconocido" este campo region siempre sera "desconocido" tambien' 
                        '"En el campo empresa si se trata de varias las añadiremos seguidas de esta con , de la forma: "Empresa1, Empresa2, Empresa3, etc")"'
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
                json_content = self.extract_json(response_ai['message']['content'])
                if json_content:
                    json_response = json.loads(json_content)
                    print(json_response)
                    tema = json_response.get("tema", "ninguno")
                    titulo = json_response.get("noticia","ninguno")
                    company_name = json_response.get("empresa", "Desconocida")
                    company_type = json_response.get("tipo_empresa", "Desconocido")
                    loc = json_response.get("ambito", "Desconocido")
                    reg = json_response.get("region", "Desconocido")
                    nuevo_tema = "ninguno"
                    existing_company = self.search_company(company_name)

                    if tema != "ninguno":
                        nuevo_tema, resumen, nuevo_tipo_empresa = self.scrape_article(noticia_url, titulo, tema)  # 🔍 Scraping
                        if (nuevo_tema != "ninguno"):
                            noticia = News(
                                company=company_name,
                                title=titulo,
                                topic=nuevo_tema,
                                date=fecha,
                                location= loc,
                                region=reg,
                                url = noticia_url,
                                details=resumen or json_response.get("detalles", "Ninguno")
                            )
#                            self.insert_db_news(noticia)
#                            print(f"Noticia '{titulo}' insertada en la base de datos. \n")
                            self.lista_noticias.append(noticia)

                    if not existing_company and (company_name != "Desconocida" and company_name != "ninguna" and nuevo_tema !="ninguno"):
                        new_company = Company(name=company_name, type=nuevo_tipo_empresa, details="Desconocidos")
                        self.insert_db_company(new_company)
                        print(f"Compañía '{company_name}' insertada en la base de datos. \n")

            except json.JSONDecodeError as e:
                print(f"Error procesando noticia '{titulo}': {e}")

        print("\n Vamos a filtrar las noticias para asegurarnos de que no haya duplicados \n")

        self.lista_noticias = self.filtrar_noticias_repetidas(self.lista_noticias)

        for noticia in self.lista_noticias:
            self.insert_db_news(noticia)
            print(f"Insertada noticia {noticia.title} en la base de datos")


    def es_noticia_duplicada_ia(self, nueva_noticia, noticia_existente):
        response_ai: ChatResponse = chat(
            model='deepseek-coder-v2:16b',
            messages=[
                {
                    'role': 'system',
                    'content': (
                        "Eres un experto en análisis de noticias empresariales. "
                        "Tu tarea es determinar si dos noticias se refieren al mismo evento o suceso empresarial, "
                        "aunque puedan tener textos o titulares diferentes. "
                        "Evalúa la similitud semántica y el contexto. "
                        "Responde únicamente en formato JSON como este:\n\n"
                        '{ "duplicada": true, "razon": "Ambas noticias tratan sobre la misma contratación de empleados por parte de la empresa XYZ"}\n\n'
                        'O, si no son duplicadas:\n'
                        '{ "duplicada": false, "razon": "Hablan de temas distintos o de empresas distintas"}\n\n'
                        "No añadas explicaciones fuera del JSON ni comillas triples."
                    )
                },
                {
                    'role': 'user',
                    'content': (
                        f"Noticia A:\nTítulo: {nueva_noticia.title}\nContenido: {nueva_noticia.details}\n\n"
                        f"Noticia B:\nTítulo: {noticia_existente.title}\nContenido: {noticia_existente.details}"
                    )
                }
            ]
        )

        try:
            respuesta_json = self.extract_json(response_ai['message']['content'])
            data = json.loads(respuesta_json)
            return data["duplicada"], data.get("razon", "")
        except Exception as e:
            print("Error al interpretar la respuesta de la IA:", e)
            return False, "Error en IA"



    def filtrar_noticias_repetidas(self, lista_noticias):
        noticias_finales = []

        for noticia in lista_noticias:
            duplicada = False
            for existente in noticias_finales:
                es_dup, razon = self.es_noticia_duplicada_ia(noticia, existente)
                if es_dup:
                    print(f"Noticia duplicada detectada: {razon}")
                    # Combinar URLs si no están ya
                    urls = set(existente.url.split(" || ")) | set([noticia.url])
                    existente.url = " || ".join(urls)
                    duplicada = True
                    break
            if not duplicada:
                noticias_finales.append(noticia)

        return noticias_finales
