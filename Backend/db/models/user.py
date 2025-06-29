from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

class User(BaseModel):
    id: Optional[str] = None
    username: str
    name: str
    surname: str
    email: str
    subscriptions: List[str] = Field(default_factory=list)
    filters: List[str] = Field(default_factory=list)
    password: str
    is_verified: bool = False

class SubscriptionRequest(BaseModel):
    subscription: str
    action: str

class FiltersRequest(BaseModel):
    filters: List[str]

class ReportFormData(BaseModel):
    fechaInicio: date
    fechaFin: date
    tipoCreacion: bool
    tipoCambioSede: bool
    tipoCrecimiento: bool
    tipoOtras: bool
    incluirGraficos: bool
    mail: Optional[str] = None
    message: Optional[str] = None