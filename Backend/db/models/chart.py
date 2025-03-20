from pydantic import BaseModel
from typing import Optional


class Chart(BaseModel):
    label: str
    value: int