
import base64
from collections import defaultdict
from datetime import date, datetime, time
from html import escape
from io import BytesIO
from typing import List
from fastapi import HTTPException
from matplotlib import pyplot as plt
from db.models.user import ReportFormData
from db.client import db_client
from xhtml2pdf import pisa


class ReportGenerator:

    def generar_grafico(self, news_list):
        contador = {
            "Creación": 0,
            "Cambio de sede": 0,
            "Crecimiento": 0,
            "Otras": 0
        }

        for n in news_list:
            if n["topic"] == "Creación de una nueva empresa":
                contador["Creación"] += 1
            elif n["topic"] == "Cambio de sede de una empresa":
                contador["Cambio de sede"] += 1
            elif n["topic"] == "Contratación abundante de empleados por parte de una empresa":
                contador["Crecimiento"] += 1
            else:
                contador["Otras"] += 1

        fig, ax = plt.subplots()
        ax.bar(contador.keys(), contador.values(), color="#0077cc")
        ax.set_title("Distribución de Noticias por Tipo", fontsize=14)
        ax.set_ylabel("Cantidad", fontsize=12)
        ax.grid(axis="y", linestyle="--", alpha=0.7)
        plt.xticks(rotation=15)

        buffer = BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format="png")
        plt.close(fig)
        buffer.seek(0)
        encoded = base64.b64encode(buffer.read()).decode('utf-8')
        return f'<img src="data:image/png;base64,{encoded}" width="500"/>'
    
    async def fetch_filtered_news(self, start_date: date, end_date: date, types: List[str]):

        print(start_date)
        print(end_date)

        start_datetime_utc = datetime.combine(start_date, time.min)
        end_datetime_utc = datetime.combine(end_date, time.max)

        print("\n")
        print(start_datetime_utc)
        print(end_datetime_utc)
        print("\n")
        print(types)

        query = {
            "topic": {"$in": types},
            "date": {
                "$gte": start_datetime_utc,
                "$lte": end_datetime_utc
            }
        }

        news_cursor = db_client.news.find(query)
        results = news_cursor.to_list(None)
        print(results)
        return results

    async def generate_pdf_report(self, form_data: ReportFormData):

        news_list = []

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Informe de Noticias</title>
            <style>
                body {{ font-family: Arial, sans-serif;  margin: 2em; color: #333; line-height: 1.5; }}
                h1,h2 {{ color: #004080; border-bottom: 1px solid #ccc; padding-bottom: 0.3em; }}
                p {{ margin-bottom: 1em; }}
                ul {{ padding-left: 1.5em;}}
                .news-item {{ margin-bottom: 0.6em;}}
                .italic {{ font-style: italic; }}
            </style>
        </head>
        <body>
            <h1>Informe de Noticias</h1>
            <p><strong>Periodo:</strong> {form_data.fechaInicio} hasta {form_data.fechaFin}</p>
            <p><strong>Tipos de Noticias Seleccionadas:</strong> {', '.join([
                tipo
                for tipo, seleccionado in [
                    ("Creación de una nueva empresa", form_data.tipoCreacion),
                    ("Cambio de sede de una empresa", form_data.tipoCambioSede),
                    ("Contratación abundante de empleados por parte de una empresa", form_data.tipoCrecimiento),
                ]
                if seleccionado
            ]) or '<span class="italic">Ninguno seleccionado</span>'}</p>
        """

        selected_types = [
            tipo
            for tipo, seleccionado in [
                ("Creación de una nueva empresa", form_data.tipoCreacion),
                ("Cambio de sede de una empresa", form_data.tipoCambioSede),
                ("Contratación abundante de empleados por parte de una empresa", form_data.tipoCrecimiento),
            ]
            if seleccionado
        ]

        if selected_types:
            news_list = await self.fetch_filtered_news(form_data.fechaInicio, form_data.fechaFin, selected_types)
            if news_list:
                grouped_news = defaultdict(list)
                for news in news_list:
                    grouped_news[escape(news.get("topic", "Otro"))].append(news)

                html_content += "<h2>Noticias Encontradas:</h2>"

                for topic in selected_types:
                    noticias_tipo = grouped_news.get(topic, [])
                    if noticias_tipo:
                        noticias_tipo.sort(key=lambda n: n.get("date", datetime.min), reverse=True)
                        html_content += f"<h3>{topic}</h3><ul>"
                        for news in noticias_tipo:
                            formatted_date = news.get("date", None)
                            if formatted_date:
                                try:
                                    formatted_date = formatted_date.strftime("%d/%m/%Y %H:%M") if isinstance(formatted_date, datetime) else str(formatted_date)
                                except Exception:
                                    formatted_date = str(formatted_date)
                            else:
                                formatted_date = "Fecha desconocida"
                            
                            urls_raw = news.get("url", "")
                            urls = urls_raw.split("||")
                            formatted_urls = "<br>".join(
                                f'<a href="{url.strip()}" target="_blank" style="color:#0077cc; text-decoration:underline;">{escape(url.strip())}</a>'
                                for url in urls if url.strip()
                            )

                            html_content += (
                                f'<li class="news-item">{escape(news.get("title", "Sin título"))} '
                                f'({formatted_date}) - Empresa: {escape(news.get("company", "Desconocida"))} '
                                f'- <strong>URL:</strong><br>{formatted_urls}</li>'
                            )
                            
                        html_content += "</ul>"
            else:
                html_content += '<p class="italic">No se encontraron noticias para los criterios seleccionados.</p>'
        else:
            html_content += '<p class="italic">No se seleccionaron tipos de noticias.</p>'

        if form_data.message:
            html_content += f"<h2>Notas Adicionales:</h2><p>{escape(form_data.message)}</p>"

        if form_data.incluirGraficos and news_list:
            grafico_html = self.generar_grafico(news_list)
            html_content += f"<h2>Gráfico de Distribución de Noticias:</h2>{grafico_html}"

        html_content += """
        </body>
        </html>
        """

        buffer = BytesIO()
        pisa_status = pisa.CreatePDF(html_content, dest=buffer)
        if not pisa_status.err:
            buffer.seek(0)
            return buffer
        else:
            raise HTTPException(status_code=500, detail=f"Error al generar el PDF con xhtml2pdf: {pisa_status.err_msg}")