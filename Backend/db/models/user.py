from pydantic import BaseModel, Field
from typing import Optional, List

class User(BaseModel):
    id: Optional[str] = None
    username: str
    name: str
    surname: str
    email: str
    subscriptions: List[str] = Field(default_factory=list)  # Valor por defecto: lista vacía
    sources: List[str] = Field(default_factory=list)
    password: str

class SubscriptionRequest(BaseModel):
    subscription: str
    action: str

class SourcesRequest(BaseModel):
    sources: List[str]