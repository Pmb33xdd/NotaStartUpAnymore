from ollama import chat
from ollama import ChatResponse
from db.models.news import News
from db.models.company import Company
from db.schemas.user import users_schema
from db.client import db_client
from send_email import send_email
import feedparser
import json

url = "https://e00-expansion.uecdn.es/rss/expansion-empleo/emprendedores.xml"

feed = feedparser.parse(url)
contador = 0
lista_noticias: list[News] = []

def insert_db_news(noticia: News):
    news_dict = dict(noticia)
    del news_dict["id"]
    db_client.local.news.insert_one(news_dict)

def insert_db_company(company: Company):
    company_dict = dict(company)
    del company_dict["id"]
    db_client.local.companies.insert_one(company_dict)

def search_company(company_name: str) -> Company | None:
    company_data = db_client.local.companies.find_one({"name": company_name})
    if company_data:
        return Company(**company_data)
    return None

def send_newsletters(news_list: list[News]):
    # Obtener todos los usuarios
    users_cursor = db_client.local.users.find()
    users = users_schema(users_cursor)

    for user in users:
        user_subscriptions = user.get("subscriptions", [])  # Acceder como diccionario
        user_news = []

        for news in news_list:
            if news.topic in user_subscriptions:  # Accedemos correctamente al atributo
                user_news.append(news)

        if user_news:
            # Lógica para enviar el correo al usuario
            print(f"Enviando correo a {user['email']} con {len(user_news)} noticias.")
            send_email(user["email"], user_news)



for entry in feed.entries:
    print(f"Noticia {contador}")
    titulo = entry.title
    print(titulo)
    print("\n")
    descripcion = entry.description
    print(descripcion)
    print("\n")
    response: ChatResponse = chat(model='llama3', messages=[
        {
            'role': 'system',
            'content': "Eres un especialista en noticias sobre empresas, tú trabajo consiste en deliverar si ciertas noticias están relacionadas con empresas o no,"
                       "y si lo están debes decidir si encajan en alguno de estos temas: \"Creación de una nueva empresa\", \"Contratación abundante de empleados por parte de una empresa \" o "
                       "\"Cambio de sede de una empresa\". En caso de que no esté relacionada con ninguno de estos tres temas el tema será \"ninguno\"."
                       "Tienes que responder únicamente en un formato JSON de la siguiente forma { \"noticia\": \"titulo de la noticia\", \"tema\":\"tema seleccionado para la noticia\", \"empresa\": \"empresa relacionada con la noticia\", \"detalles\": \"detalles relevantes de la noticia, ejemplo: cuántos empleados tendrá la nueva empresa\"}"
                       "Los detalles serán una breve cadena de texto. En caso de que no haya ninguna empresa relacionada el campo empresa será \"ninguna\". No respondas con nada más que este JSON"
        },
        {
            'role': 'user',
            'content': f"Titular: {titulo}    Descripción:{descripcion}\n",
        },
    ])
    try:
        json_response = json.loads(response['message']['content'])
        print(json_response)
        tema = json_response.get("tema", "ninguno")  # Obtiene el tema o usa "ninguno" si no está presente
        company_name = json_response.get("empresa", "Desconocida")
#       company_details = json_response.get("detalles", "Ninguno")

        if tema != "ninguno":

            existing_company = search_company(company_name)
            if not existing_company and company_name != "Desconocida":
                #Insertamos la nueva compañia en la base de datos
                new_company = Company(name=company_name, type="Desconocido", details="Desconocidos")
                insert_db_company(new_company)
                print(f"Compañía '{company_name}' insertada en la base de datos.")

            noticia = News(
                company=json_response.get("empresa", "Desconocida"),  # Obtiene la empresa o usa "Desconocida" si no está presente
                title=titulo,
                topic=tema,
                details=json_response.get("detalles", "Ninguno")
            )
            insert_db_news(noticia)
            print(f"Noticia '{titulo}' insertada en la base de datos.")
            lista_noticias.append(noticia)
        else:
            print(f"Noticia '{titulo}' no relacionada con los temas especificados. No se insertará en la base de datos.")

    except json.JSONDecodeError as e:
        print(f"Error al decodificar JSON para la noticia '{titulo}': {e}")
        print(response['message']['content'])  # Imprime el contenido del mensaje para depuración

    contador = contador + 1

send_newsletters(lista_noticias)