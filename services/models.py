from pydantic import BaseModel


class Dht22(BaseModel):
    temperature: float
    humidity: float
    heatindex: float
    date_create: str
    