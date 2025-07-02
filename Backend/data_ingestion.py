import re
import requests
import os
import json
from ollama import chat
from datetime import datetime, timedelta, timezone
from ollama import ChatResponse
from bs4 import BeautifulSoup
from db.models.news import News
from db.models.company import Company
from db.schemas.user import users_schema
from db.client import db_client, metadata_collection
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

    def _get_last_run_date_from_db(self) -> Optional[datetime]:

        metadata = metadata_collection.find_one({"_id": "last_ingestion_timestamp"})
        if metadata and "timestamp" in metadata:
            try:
                
                return metadata["timestamp"]
            except Exception as e:
                print(f"Advertencia: Formato de fecha inválido en DB para last_ingestion_timestamp. {e}")
                return None
        return None
    
    def _update_last_run_date_in_db(self, news_list: list[News]):
        
        if not news_list:
            print("La lista de noticias está vacía. No se actualiza la fecha de última ejecución.")
            return

        latest_news_date = None
        for news_item in news_list:
            if latest_news_date is None or news_item.date > latest_news_date:
                latest_news_date = news_item.date

        date_to_save = latest_news_date

        metadata_collection.update_one(
            {"_id": "last_ingestion_timestamp"},
            {"$set": {"timestamp": date_to_save}},
            upsert=True
        )
        print(f"Fecha de última ejecución actualizada en DB a: {date_to_save.strftime('%Y-%m-%d %H:%M:%S')}")

    def change_source_and_reset(self, url_nueva):
        self.feed = feedparser.parse(url_nueva)
        self.contador = 0

    def insert_db_news(self, noticia: News):
        news_dict = dict(noticia)
        del news_dict["id"]
        db_client.news.insert_one(news_dict)

    def insert_db_company(self, company: Company):
        company_dict = dict(company)
        del company_dict["id"]
        db_client.companies.insert_one(company_dict)

    def search_company(self, company_name: str) -> Company | None:
        company_data = db_client.companies.find_one({"name": company_name})
        if company_data:
            return Company(**company_data)
        return None
    
    def send_newsletters(self, news_list: list[News]):
        users_cursor = db_client.users.find()
        users = users_schema(users_cursor)

        for user in users:
            user_subscriptions = user.get("subscriptions", [])
            user_filters = user.get("filters", [])
            
            subscribed_news = []
            for news in news_list:
                if news.topic in user_subscriptions or news.company in user_subscriptions:
                    subscribed_news.append(news)
            
            if not subscribed_news:
                continue

            final_news_to_send = subscribed_news
            
            if "__APLICAR_A_BOLETINES__" in user_filters:
                
                location_filters = {f for f in user_filters if f != "__APLICAR_A_BOLETINES__"}
                
                if location_filters:
                    filtered_news = []
                    for news in subscribed_news:

                        news_location = getattr(news, 'location', None)
                        news_region = getattr(news, 'region', None)
                        
                        if (news_location and news_location in location_filters) or (news_region and news_region in location_filters):
                            filtered_news.append(news)
                    
                    final_news_to_send = filtered_news

            if final_news_to_send:
                print(f"Enviando correo a {user['email']} con {len(final_news_to_send)} noticias.")
                cartero.send_email(user["email"], final_news_to_send, user["name"])

    def extract_json(self, content: str):
        match = re.search(r'({.*})', content, re.DOTALL)
        if match:
            return match.group(0)
        return None

    
    def data_ingestion_rss(self):
        last_run_date = self._get_last_run_date_from_db()
        print(f"Última fecha de ejecución (RSS): {last_run_date}")

        for entry in self.feed.entries:

            fecha_str = entry.get("published", "Fecha no disponible")
            try:
                if 'z' in "%a, %d %b %Y %H:%M:%S %z": 
                    published_date_aware = datetime.strptime(fecha_str, "%a, %d %b %Y %H:%M:%S %z")
                else:
                    published_date_aware = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            except ValueError:
                print(f"Advertencia: No se pudo parsear la fecha '{fecha_str}' para la noticia '{entry.title}'. Saltando.")
                continue

            if last_run_date and last_run_date.tzinfo is None:
                last_run_date = last_run_date.replace(tzinfo=timezone.utc)
            
            if published_date_aware and published_date_aware.tzinfo is None:
                published_date_aware = published_date_aware.replace(tzinfo=timezone.utc)


            if last_run_date and published_date_aware <= last_run_date:
                print(f"Noticia '{entry.title}' es antigua (fecha: {published_date_aware}). Saltando.")
                continue

            print(f"Noticia {self.contador}")
            titulo = entry.title
            print(titulo)
            print("\n")
            descripcion = entry.description
            fecha = entry.get("published", "Fecha no disponible")
            fecha = datetime.strptime(fecha, "%a, %d %b %Y %H:%M:%S %z").strftime("%Y-%m-%d %H:%M:%S")
            noticia_url = entry.get("guid", "url no disponible")
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
                        nuevo_tema, resumen, nuevo_tipo_empresa, nuevo_nombre_empresa = self.scrape_article(noticia_url, titulo, tema)
                        if (nuevo_tema != "ninguno"):

                            noticia = News(
                                company=nuevo_nombre_empresa,
                                title=titulo,
                                topic=nuevo_tema,
                                date=fecha,
                                location= loc,
                                region=reg,
                                url = noticia_url,
                                details=resumen or json_response.get("detalles", "Ninguno")
                            )

                            self.lista_noticias.append(noticia)
                            existing_company = self.search_company(nuevo_nombre_empresa)

                            if not existing_company and (nuevo_nombre_empresa != "Desconocida" and nuevo_nombre_empresa != "ninguna" and nuevo_tema !="ninguno"):
                                new_company = Company(name=nuevo_nombre_empresa, type=nuevo_tipo_empresa, details="Desconocidos")
                                self.insert_db_company(new_company)
                                print(f"Compañía '{nuevo_nombre_empresa}' insertada en la base de datos. \n")

                else:
                    print(f"No se encontró un JSON válido en la respuesta de la IA.")
            except json.JSONDecodeError as e:
                print(f"Error al decodificar JSON para la noticia '{titulo}': {e}")
                print(response['message']['content'])
                print(f"\nJSON extraído: {json_content}")

            self.contador += 1

    
    def scrape_article(self, url, title, tema):
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")

            paragraphs = soup.find_all("p")
            content = " ".join([p.get_text() for p in paragraphs])
            if len(content) > 1000:
                content = content[:1000] + "..."
            
            if not content.strip():
                print(f"No se pudo extraer contenido relevante de la noticia '{title}'.")
                return "ninguno", "No se pudo extraer contenido relevante", "Desconocido", "Desconocida"

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
                 
            
            try:
                json_content = self.extract_json(response['message']['content'])
                if json_content:
                    json_response = json.loads(json_content)
                    print("Noticia reevaluada: \n")
                    print(json_response)
                    topic = json_response.get("tema","ninguno")
                    tipo_empresa = json_response.get("tipo_empresa", "Desconocido")
                    nombre_empresa = json_response.get("empresa", "Desconocida")
                    details = json_response.get("detalles", "Desconocidos")
                    return topic, details, tipo_empresa, nombre_empresa
                else:
                    print(f"No se encontró un JSON válido en la respuesta de la IA para la noticia '{title}'.")
                    return "ninguno", "No se pudo extraer contenido relevante", "Desconocido", "Desconocida"

            except json.JSONDecodeError as e:
                print(f"Error procesando noticia '{title}': {e}")
                return "ninguno", "No se pudo extraer contenido relevante", "Desconocido", "Desconocida"
       
        except Exception as e:
            print(f"Error extrayendo información de {url}: {e}")
            return "ninguno", "Error de scraping", "Desconocido", "Desconocida"
    
        
    def data_ingestion_newsAPI(self, query):
        last_run_date = self._get_last_run_date_from_db()
        print(f"Última fecha de ejecución (newsAPI): {last_run_date}")

        url = f"https://newsapi.org/v2/everything?q={query}&apiKey={API_KEY}"
        response = requests.get(url)
        data = response.json()

        for article in data.get("articles", []):
            titulo = article["title"]
            descripcion = article.get("description", "")
            noticia_url = article["url"]
            fecha_str = article["publishedAt"]

            try:
                published_date_aware = datetime.strptime(fecha_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            except ValueError:
                print(f"Advertencia: No se pudo parsear la fecha '{fecha_str}' para la noticia '{titulo}'. Saltando.")
                continue

            if last_run_date and last_run_date.tzinfo is None:
                last_run_date = last_run_date.replace(tzinfo=timezone.utc)

            if last_run_date and published_date_aware <= last_run_date:
                print(f"Noticia '{titulo}' es antigua (fecha: {published_date_aware}). Saltando.")
                continue


            fecha = datetime.strptime(fecha_str, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M:%S")

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
                    loc = json_response.get("ambito", "Desconocido")
                    reg = json_response.get("region", "Desconocido")
                    nuevo_tema = "ninguno"
                    
                    if tema != "ninguno":
                        nuevo_tema, resumen, nuevo_tipo_empresa, nuevo_nombre_empresa = self.scrape_article(noticia_url, titulo, tema)
                        if (nuevo_tema != "ninguno"):
                            noticia = News(
                                company=nuevo_nombre_empresa,
                                title=titulo,
                                topic=nuevo_tema,
                                date=fecha,
                                location= loc,
                                region=reg,
                                url = noticia_url,
                                details=resumen or json_response.get("detalles", "Ninguno")
                            )

                            self.lista_noticias.append(noticia)
                            existing_company = self.search_company(nuevo_nombre_empresa)

                            if not existing_company and (nuevo_nombre_empresa != "Desconocida" and nuevo_nombre_empresa != "ninguna" and nuevo_tema !="ninguno"):
                                new_company = Company(name=nuevo_nombre_empresa, type=nuevo_tipo_empresa, details="Desconocidos")
                                self.insert_db_company(new_company)
                                print(f"Compañía '{nuevo_nombre_empresa}' insertada en la base de datos. \n")

            except json.JSONDecodeError as e:
                print(f"Error procesando noticia '{titulo}': {e}")


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
                    urls = set(existente.url.split(" || ")) | set([noticia.url])
                    existente.url = " || ".join(urls)
                    duplicada = True
                    break
            if not duplicada:
                noticias_finales.append(noticia)

        return noticias_finales
