from fastapi import APIRouter, HTTPException, Query, status, Depends, Security, Header
from typing import Dict, List
from db.schemas.user import user_schema, users_schema
from db.schemas.new import new_schema, news_schema
from db.schemas.company import company_schema, companies_schema
from db.models.user import User, SubscriptionRequest, FiltersRequest, ReportFormData
from db.models.news import News
from send_email import MailSender
from db.models.contact_mail import ContactMail
from db.models.company import Company
from db.models.login_user import LoginData
from db.models.chart import Chart
import os
from db.client import db_client
from bson import ObjectId
import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone, date, time
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from dotenv import load_dotenv
from collections import Counter
from fastapi.responses import StreamingResponse
from io import BytesIO
from xhtml2pdf import pisa
import matplotlib.pyplot as plt
import base64

load_dotenv()

API_KEY = os.getenv("SECRET_MI_API")
API_KEY_NAME = "access_token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT") 
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

cartero = MailSender(SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD )

# Configuración de JWT
JWT_SECRET = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}},
)

# Esquema de autenticación OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Función para crear un token de acceso JWT
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt

# Función para obtener el usuario actual (requiere autenticación)
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = search_user("email", email)
    if user is None:
        raise credentials_exception
    return user

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate API key",
        )


@router.get("/", response_model=list[User])
async def users(api_key: str = Depends(get_api_key)):
    return users_schema(db_client.users.find())

@router.get("/news", response_model=list[News])
async def news(api_key: str = Depends(get_api_key)):
    return news_schema(db_client.news.find())

@router.get("/companies", response_model=list[Company])
async def companies(api_key: str = Depends(get_api_key)):
    return companies_schema(db_client.companies.find())

@router.get("/filters", response_model=list[str])
async def filters(api_key: str = Depends(get_api_key)):

    unique_filters = set()

    news_items = db_client.news.find().to_list(None)

    for news_item in news_items:
        if "location" in news_item and news_item["location"]:
            if(news_item["location"] != "desconocido"):
                unique_filters.add(news_item["location"])
        if "region" in news_item and news_item["region"]:
            if(news_item["region"] != "desconocido"):
                unique_filters.add(news_item["region"])

    return list(unique_filters)

"""
@router.get("/{id}")
async def user(id: str):
    return search_user("_id", ObjectId(id))
"""

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(user: User, api_key: str = Depends(get_api_key)):
    try:
        if type(search_user("email", user.email)) == User:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario ya existe"
            )
        hashed_password = bcrypt.hashpw(
            user.password.encode("utf-8"), bcrypt.gensalt()
        )
        user_dict = dict(user)
        del user_dict["id"]
        user_dict["password"] = hashed_password

        id = db_client.users.insert_one(user_dict).inserted_id
        new_user = user_schema(db_client.users.find_one({"_id": id}))

        verification_token = create_access_token(
            data={"sub": user.email, "type": "verify"},
        )

        verification_link = f"https://notastartupanymore.onrender.com/users/verify-email?token={verification_token}"
        cartero.send_verification_email(user_dict["email"], user_dict["name"], verification_link)
        return User(**new_user)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear usuario: {str(e)}",
        )

@router.get("/verify-email")
async def verify_email(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        email = payload.get("sub")
        token_type = payload.get("type")

        if token_type != "verify" or not email:
            raise HTTPException(status_code=400, detail="Token inválido")

        user = search_user("email", email)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        # Marcar como verificado
        db_client.users.update_one({"email": email}, {"$set": {"is_verified": True}})
        return {"message": "Correo verificado con éxito"}

    except JWTError:
        raise HTTPException(status_code=400, detail="Token inválido o expirado")


@router.post("/login", response_model=dict)
async def login(login_data: LoginData, api_key: str = Depends(get_api_key)):  # Usa LoginData como tipo de parámetro
    try:
        db_user = search_user("email", login_data.email)  # Accede al email desde login_data
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas"
            )
    
        if not bcrypt.checkpw(
            login_data.password.encode("utf-8"), db_user.password.encode("utf-8")
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas"
            )
        
        if not db_user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Debes verificar tu correo antes de iniciar sesión"
            )
        
        # Crea el token JWT
        access_token = create_access_token(data={"sub": db_user.email})
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException as e:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en el servidor: {str(e)}",
        )

# Endpoint para obtener los datos del usuario actual (protegido)
@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user), api_key: str = Depends(get_api_key)):
    return current_user

@router.put("/")
async def user(user: User, api_key: str = Depends(get_api_key)):
    user_dict = dict(user)
    del user_dict["id"]
    try:
        db_client.users.find_one_and_replace(
            {"_id": ObjectId(user.id)}, user_dict
        )
    except:
        return {"error": "No se ha actualizado el usuario"}
    return search_user("_id", ObjectId(user.id))

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, api_key: str = Depends(get_api_key)):
    try:
        found = db_client.users.find_one_and_delete({"_id": ObjectId(user_id)})
        if not found:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return  # 204 no content
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en el servidor: {str(e)}")

    
@router.put("/me", response_model=User)
async def update_user_me(
    request: SubscriptionRequest, current_user: User = Depends(get_current_user), api_key: str = Depends(get_api_key)
):
    try:
        subscription = request.subscription
        action = request.action
        print(f"Subscription: {subscription}")  
        
        # Asegurar que la lista de suscripciones existe
        user_subscriptions = current_user.subscriptions if current_user.subscriptions else []

        if action == "add" and subscription not in user_subscriptions:
            user_subscriptions.append(subscription)
        
        elif action == "remove" and subscription in user_subscriptions:
            user_subscriptions.remove(subscription)

        result = db_client.users.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$set": {"subscriptions": user_subscriptions}}
        )

        if result.modified_count >= 0 and result.acknowledged:
            updated_user = search_user("_id", ObjectId(current_user.id))
            if updated_user:
                return updated_user
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se pudo actualizar el usuario")

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en el servidor: {str(e)}")
    
@router.put("/me/filters", response_model=User)
async def update_user_filters(
    filters_request: FiltersRequest, current_user: User = Depends(get_current_user), api_key: str = Depends(get_api_key)
):
    try:
        filters = filters_request.filters
        print(f"Las fuentes antiguas de este usuario son {current_user.filters}")
        print(f"Las fuentes nuevas de este usuario son {filters_request.filters}")

        result = db_client.users.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$set": {"filters": filters}}
        )

        print(f"Resultado de la actualización en MongoDB: {result.raw_result}")

        if result.modified_count >= 0 and result.acknowledged:
            updated_user = search_user("_id", ObjectId(current_user.id))
            if updated_user:
                return updated_user
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se pudo actualizar el usuario")

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error en el servidor: {str(e)}")

@router.post("/contactmail")
async def send_contact_email(contact: ContactMail, api_key: str = Depends(get_api_key)):

    cartero.contact_email("pablomoreno37185@gmail.com", contact.name, contact.mail, contact.message )

@router.get("/charts")
def get_chart_data(
    dataType: str = Query(...),
    companyType: str = Query(...),
    timePeriod: str = Query(...),
    api_key: str = Depends(get_api_key)
) -> List[Chart]:
    """
    Obtiene los datos para el gráfico según los parámetros de selección.
    """
    print(f"Parámetros recibidos: data_type={dataType}, company_type={companyType}, time_period={timePeriod}")
    data = []

    if timePeriod == "ultimoAno":
            # Obtener la fecha de hace un año
            one_year_ago = datetime.now() - timedelta(days=365)
            # Truncar la hora a las 00:00:00 para solo comparar la fecha
            one_year_ago = one_year_ago.replace(hour=0, minute=0, second=0, microsecond=0)
            # Convertir la fecha a formato string en el mismo formato que la base de datos
            date_filter = {"$gte": one_year_ago}

    elif timePeriod == "ultimoMes":
            # Obtener la fecha de hace un mes
            one_month_ago = datetime.now() - timedelta(days=30)
            # Truncar la hora a las 00:00:00
            one_month_ago = one_month_ago.replace(hour=0, minute=0, second=0, microsecond=0)
            # Convertir la fecha a formato string
            date_filter = {"$gte": one_month_ago}

    else:
        # Si no es "ultimoAno" ni "ultimoMes", no filtramos por fecha
        date_filter = {}
    if dataType == "empresasCreadas":
        data = generar_datos_chart("Creación de una nueva empresa", companyType, date_filter)

    elif  dataType == "cambioSede":
        data = generar_datos_chart("Cambio de sede de una empresa", companyType, date_filter)

    elif dataType == "crecimientoEmpleados":
        data = generar_datos_chart("Contratación abundante de empleados por parte de una empresa", companyType, date_filter)
        
    else:
        raise HTTPException(status_code=400, detail="Tipo de datos no válido")

    print(f"Datos devueltos: {data}")
    return data

def search_user(field: str, key):
    try:
        user_data = db_client.users.find_one({field: key})
        if user_data:  # Verifica si se encontró un usuario
            user = user_schema(user_data)
            return User(**user)
        return None  # Retorna None si no se encuentra el usuario
    except Exception as e:
        print(f"Error en search_user: {e}") # Imprime el error para debuggear
        return None  # También retorna None en caso de error
    
def generar_datos_chart(type: str, companyType: str, date_filter):
        news_list = list(db_client.news.find({"topic": type, "date": date_filter}))

        # Extraer las empresas de las noticias
        companies = {news["company"] for news in news_list}
        print(f"{companies}")

        # Buscar las empresas en la base de datos
        companies_list = list(db_client.companies.find({"name": {"$in": list(companies)}}))
        print(f"{companies_list}")

        # Contar la cantidad de empresas por tipo
        type_counts = Counter(company["type"] for company in companies_list)

        # Filtrar por tipo de empresa si es necesario
        if companyType != "todos":
            type_counts = {k: v for k, v in type_counts.items() if k == companyType}
     
        # Crear la respuesta
        data = [{"label": tipo, "value": cantidad} for tipo, cantidad in type_counts.items()]

        return data

from datetime import datetime, time, date
from typing import List

async def fetch_filtered_news(start_date: date, end_date: date, types: List[str]):
    """
    Obtiene las noticias filtradas por fecha y tipo desde la base de datos,
    usando objetos datetime para la comparación.
    """
    print(start_date)
    print(end_date)

    # Convertimos start_date y end_date en datetime con hora y en UTC
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


def generar_grafico(news_list):
    tipos = ["Creación", "Cambio de sede", "Crecimiento", "Otras"]
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
    ax.set_title("Distribución de Noticias por Tipo")
    ax.set_ylabel("Cantidad")
    plt.xticks(rotation=15)

    buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format="png")
    plt.close(fig)
    buffer.seek(0)
    encoded = base64.b64encode(buffer.read()).decode('utf-8')
    return f'<img src="data:image/png;base64,{encoded}" width="500"/>'

async def generate_pdf_report(form_data: ReportFormData):
    """
    Genera el informe PDF utilizando xhtml2pdf.
    """
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
                ("otras", form_data.tipoOtras),
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
            ("otras", form_data.tipoOtras),
        ]
        if seleccionado
    ]

    if selected_types:
        news_list = await fetch_filtered_news(form_data.fechaInicio, form_data.fechaFin, selected_types)
        if news_list:
            html_content += "<h2>Noticias Encontradas:</h2><ul>"
            for news in news_list:
                formatted_date = news.get("date", None)
                if formatted_date:
                    try:
                        formatted_date = formatted_date.strftime("%d/%m/%Y %H:%M") if isinstance(formatted_date, datetime) else str(formatted_date)
                    except Exception:
                        formatted_date = str(formatted_date)
                else:
                    formatted_date = "Fecha desconocida"
                html_content += f'<li class="news-item">{news.get("title", "Sin título")} ({formatted_date}) - Empresa: {news.get("company", "Desconocida")} - URL de la noticia: {news.get("url","URL no disponible")}</li>'
            html_content += "</ul>"
        else:
            html_content += '<p class="italic">No se encontraron noticias para los criterios seleccionados.</p>'
    else:
        html_content += '<p class="italic">No se seleccionaron tipos de noticias.</p>'

    if form_data.message:
        html_content += f"<h2>Notas Adicionales:</h2><p>{form_data.message}</p>"

    if form_data.incluirGraficos and news_list:
        grafico_html = generar_grafico(news_list)
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


@router.post("/generate-pdf")
async def generate_report(form_data: ReportFormData, api_key: str = Depends(get_api_key)):
    """
    Endpoint para generar un informe PDF basado en los datos proporcionados.
    """
    try:
        pdf_buffer = await generate_pdf_report(form_data)
        headers = {
            'Content-Disposition': f'attachment; filename="reporte_{date.today()}.pdf"'
        }
        return StreamingResponse(pdf_buffer, media_type="application/pdf", headers=headers)
    except HTTPException as e:
        raise e # Re-raise las HTTPExceptions para que FastAPI las maneje
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar el PDF: {str(e)}")
