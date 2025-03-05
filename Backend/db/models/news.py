from pydantic import BaseModel
from typing import Optional


class News(BaseModel):
    id: Optional[str] = None
    company: str
    title: str
    topic: str
    details: str