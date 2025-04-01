from data_ingestion import Ingestion
from send_email import MailSender

rss_Expansion_emprendedores = "https://e00-expansion.uecdn.es/rss/expansion-empleo/emprendedores.xml"
lista_urls = []
query = '"nueva sede" empleados '

explorador = Ingestion(rss_Expansion_emprendedores)
explorador.data_ingestion_rss()

for fuente in lista_urls:
    print("Hola :)  \n")
    explorador.change_source_and_reset(fuente)
    explorador.data_ingestion_rss()

explorador.data_ingestion_google_news(query)

explorador.send_newsletters(explorador.lista_noticias)