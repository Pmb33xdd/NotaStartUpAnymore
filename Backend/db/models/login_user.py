from pydantic import BaseModel

# Define el modelo para los datos de login
class LoginData(BaseModel):
    email: str
    password: str