from fastapi import APIRouter, HTTPException, Query, status, Depends
from typing import Dict, List
from db.schemas.user import user_schema, users_schema
from db.schemas.new import new_schema, news_schema
from db.schemas.company import company_schema, companies_schema
from db.models.user import User, SubscriptionRequest, SourcesRequest
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
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv

load_dotenv()


API_KEY = os.getenv("API_KEY")
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

@router.get("/", response_model=list[User])
async def users():
    return users_schema(db_client.users.find())

@router.get("/news", response_model=list[News])
async def news():
    return news_schema(db_client.news.find())

@router.get("/companies", response_model=list[Company])
async def news():
    return companies_schema(db_client.companies.find())

"""
@router.get("/{id}")
async def user(id: str):
    return search_user("_id", ObjectId(id))
"""

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def user(user: User):
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
        return User(**new_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear usuario: {str(e)}",
        )


@router.post("/login", response_model=dict)
async def login(login_data: LoginData):  # Usa LoginData como tipo de parámetro
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
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/")
async def user(user: User):
    user_dict = dict(user)
    del user_dict["id"]
    try:
        db_client.users.find_one_and_replace(
            {"_id": ObjectId(user.id)}, user_dict
        )
    except:
        return {"error": "No se ha actualizado el usuario"}
    return search_user("_id", ObjectId(user.id))

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def user(id: str):
    found = db_client.users.find_one_and_delete({"_id": ObjectId(id)})
    if not found:
        return {"error": "No se ha eliminado el usuario"}
    
@router.put("/me", response_model=User)
async def update_user_me(
    request: SubscriptionRequest, current_user: User = Depends(get_current_user)
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
    
@router.put("/me/sources", response_model=User)
async def update_user_sources(
    sources_request: SourcesRequest, current_user: User = Depends(get_current_user)
):
    try:
        sources = sources_request.sources
        print(f"Las fuentes antiguas de este usuario son {current_user.sources}")
        print(f"Las fuentes nuevas de este usuario son {sources_request.sources}")

        result = db_client.users.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$set": {"sources": sources}}
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
async def send_contact_email(contact: ContactMail):

    cartero.contact_email("pablomoreno37185@gmail.com", contact.name, contact.mail, contact.message )

@router.get("/charts")
async def get_chart_data(
    dataType: str = Query(...),
    companyType: str = Query(...),
    timePeriod: str = Query(...)
) -> List[Chart]:
    """
    Obtiene los datos para el gráfico según los parámetros de selección.
    """
    print(f"Parámetros recibidos: data_type={dataType}, company_type={companyType}, time_period={timePeriod}")
    data = []
    if dataType == "empresasCreadas":
        if companyType == "todos":
            data = [{"label": "Tecnología", "value": 10}, {"label": "Finanzas", "value": 5}]
        elif companyType == "tecnologia":
            data = [{"label": "Tecnología", "value": 8}]
        else:
            raise HTTPException(status_code=400, detail="Tipo de empresa no válido")
    elif dataType == "crecimientoEmpleados":
        data = [{"label": "2023", "value": 150}, {"label": "2024", "value": 200}]
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