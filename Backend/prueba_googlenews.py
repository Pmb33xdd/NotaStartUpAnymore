import requests, os
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("API_KEY_GOOGLE_NEWS")
query = '"nueva sede" empleados '
url = f"https://newsapi.org/v2/everything?q={query}&apiKey={API_KEY}"

response = requests.get(url)
data = response.json()

for article in data["articles"]:
    print(f"Fuente: {article['source']['name']}")
    print(f"Autor: {article.get('author', 'Desconocido')}")
    print(f"Título: {article['title']}")
    print(f"Descripción: {article['description']}")
    print(f"URL: {article['url']}")
    print(f"Imagen: {article['urlToImage']}")
    print(f"Fecha de publicación: {article['publishedAt']}\n")
    print("-" * 80)



# PODEMOS BUSCAR NOTICIAS RELEVANTES CON ESTO, SELECCIONAR LAS QUE NOS INTERESEN CON IA
# Y HACER WEB SCRAPPING EN EL ENLACE PARA EXTRAER MÁS INFORMACIÓN DE LAS SELECCIONADAS

#https://www.abc.es/espana/comunidad-valenciana/bc3-cocinas-traslada-alicante-lean-manufaturing-amplia-20250317213230-nt.html?ref=https%3A%2F%2Fwww.abc.es%2Fespana%2Fcomunidad-valenciana%2Fbc3-cocinas-traslada-alicante-lean-manufaturing-amplia-20250317213230-nt.html