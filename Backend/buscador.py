from data_ingestion import Ingestion
from send_email import MailSender
#import feedparser

rss_Expansion_emprendedores = "https://e00-expansion.uecdn.es/rss/expansion-empleo/emprendedores.xml"
lista_urls = []
query = ' "nueva sede" empleados'
#query = '"nueva sede" empleados "contratar" "nueva empresa" '
#query = '"nueva sede" OR empleados OR "contratar" OR "nueva empresa" '


#feed = feedparser.parse(rss_Expansion_emprendedores)
#for entry in feed.entries:

explorador = Ingestion(rss_Expansion_emprendedores)
#explorador.data_ingestion_rss()

for fuente in lista_urls:
    print("Hola :)  \n")
    explorador.change_source_and_reset(fuente)
    explorador.data_ingestion_rss()

explorador.data_ingestion_google_news(query)

#explorador.send_newsletters(explorador.lista_noticias)