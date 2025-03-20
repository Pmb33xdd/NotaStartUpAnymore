from pydantic import BaseModel

class ContactMail(BaseModel):
    name: str
    mail: str
    message: str