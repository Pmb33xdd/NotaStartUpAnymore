from pydantic import BaseModel

class Chart(BaseModel):
    label: str
    value: int