from pydantic import BaseModel

class LoginData(BaseModel):
    email: str
    password: str