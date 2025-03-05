from pydantic import BaseModel
from typing import Optional


class Company(BaseModel):
    id: Optional[str] = None
    name: str
    type: str
    details: str