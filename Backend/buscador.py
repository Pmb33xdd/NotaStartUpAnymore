from data_ingestion import Ingestion
from send_email import MailSender
#import feedparser

rss_Expansion_emprendedores = "https://e00-expansion.uecdn.es/rss/expansion-empleo/emprendedores.xml"
lista_urls = []

#QUERIES CREACION DE UNA NUEVA EMPRESA
query1 = '"nueva empresa" OR "creación de empresa" OR "se ha fundado una empresa"'
query2 = '"ha nacido una empresa" OR "fundación de empresa" OR "startup creada"'
query3 = '"nueva compañía" AND "ha comenzado a operar" '
query4 = '"se constituye una empresa" OR "empresa recién creada"'
query5 = '"empresa emergente" AND ("se ha creado" OR "inicio de actividad")'
query6 = '"startup" AND ("fundada" OR "creada" OR "nacida")'

#QUERIES CAMBIO DE SEDE DE UNA EMPRESA
query7 = '"cambio de sede" OR "traslado de sede" OR "empresa cambia de sede"'
query8 = '"nueva sede" AND ("empresa" OR "compañía")'
query9 = '"relocalización de empresa" OR "empresa traslada su sede"'
query10 = '"empresa" AND "nueva ubicación" AND ("sede" OR "oficina central")'
query11 = '"empresa se muda" OR "reubica su sede"'

#QUERIES CONTRATACIÓN ABUNDANTE DE EMPLEADOS
query12 = '"empresa contrata" AND ("cientos de empleados" OR "gran número de trabajadores")'
query13 = '"nuevas contrataciones" AND "empresa"'
query14 = '"plan de contratación masiva" OR "contratación de personal"'
query15 = '"empresa incorpora" AND ("nuevos empleados" OR "nuevos trabajadores")'
query16 = '"expansión de plantilla" OR "crecimiento de personal"'
query17 = '"aumento de plantilla" AND ("empresa" OR "compañía")'


#feed = feedparser.parse(rss_Expansion_emprendedores)
#for entry in feed.entries:

explorador = Ingestion(rss_Expansion_emprendedores)
#explorador.data_ingestion_rss()

for fuente in lista_urls:
    print("Hola :)  \n")
    explorador.change_source_and_reset(fuente)
    explorador.data_ingestion_rss()

explorador.data_ingestion_google_news(query13)

explorador.send_newsletters(explorador.lista_noticias)