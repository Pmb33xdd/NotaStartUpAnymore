from pydantic import BaseModel, Field
from typing import Optional, List

class User(BaseModel):
    id: Optional[str] = None
    username: str
    name: str
    surname: str
    email: str
    subscriptions: List[str] = Field(default_factory=list)  # Valor por defecto: lista vacía
    filters: List[str] = Field(default_factory=list)
    password: str
    is_verified: bool = False

class SubscriptionRequest(BaseModel):
    subscription: str
    action: str

class FiltersRequest(BaseModel):
    filters: List[str]