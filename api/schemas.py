from pydantic import BaseModel

from .enums import AlphaStreetCategory


class AlphaStreetOut(BaseModel):
    symbol: str
    category: AlphaStreetCategory
    title: str
    date: str
    link: str

    class Config:
        orm_mode = True
