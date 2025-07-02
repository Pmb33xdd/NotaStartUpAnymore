from data_ingestion import Ingestion
from send_email import MailSender

rss_url = "https://e00-expansion.uecdn.es/rss/expansion-empleo/emprendedores.xml"

queries = [
    # NUEVAS EMPRESAS
    '"nueva empresa" OR "creación de empresa" OR "se ha fundado una empresa"',
    '"ha nacido una empresa" OR "fundación de empresa" OR "startup creada"',
    '"nueva compañía" AND "ha comenzado a operar"',
    '"se constituye una empresa" OR "empresa recién creada"',
    '"empresa emergente" AND ("se ha creado" OR "inicio de actividad")',
    '"startup" AND ("fundada" OR "creada" OR "nacida")',

    # CAMBIO DE SEDE
    '"cambio de sede" OR "traslado de sede" OR "empresa cambia de sede"',
    '"nueva sede" AND ("empresa" OR "compañía")',
    '"relocalización de empresa" OR "empresa traslada su sede"',
    '"empresa" AND "nueva ubicación" AND ("sede" OR "oficina central")',
    '"empresa se muda" OR "reubica su sede"',

    # CONTRATACIÓN ABUNDANTE
    '"empresa contrata" AND ("cientos de empleados" OR "gran número de trabajadores")',
    '"nuevas contrataciones" AND "empresa"',
    '"plan de contratación masiva" OR "contratación de personal"',
    '"empresa incorpora" AND ("nuevos empleados" OR "nuevos trabajadores")',
    '"expansión de plantilla" OR "crecimiento de personal"',
    '"aumento de plantilla" AND ("empresa" OR "compañía")'
]

explorador = Ingestion(rss_url)

lista_urls = []
explorador.data_ingestion_rss()

for fuente in lista_urls:
    explorador.change_source_and_reset(fuente)
    explorador.data_ingestion_rss()

for query in queries:
    explorador.data_ingestion_newsAPI(query)

print("\n#### Iniciando filtrado y almacenamiento final de noticias ####\n")

if explorador.lista_noticias:
    explorador.lista_noticias = explorador.filtrar_noticias_repetidas(explorador.lista_noticias)

    for noticia in explorador.lista_noticias:
        explorador.insert_db_news(noticia)
        print(f"Noticia final '{noticia.title}' insertada en la base de datos.")
else:
    print("No se recolectaron noticias para filtrar e insertar.")

explorador.send_newsletters(explorador.lista_noticias)
explorador._update_last_run_date_in_db(explorador.lista_noticias)
