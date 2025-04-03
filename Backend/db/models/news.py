from pydantic import BaseModel
from typing import Optional


class News(BaseModel):
    id: Optional[str] = None
    company: str
    title: str
    topic: str
    date: str
    location: str
    region: str
    details: str