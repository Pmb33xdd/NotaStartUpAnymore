from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class News(BaseModel):
    id: Optional[str] = None
    company: str
    title: str
    topic: str
    date: datetime
    location: str
    region: str
    url: str
    details: str