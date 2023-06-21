from sqlalchemy import Column, Enum, Integer, String

from .database import Base
from .enums import AlphaStreetCategory


class AlphaStreet(Base):
    __tablename__ = "alphastreet"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    category = Column(Enum(AlphaStreetCategory), index=True)
    title = Column(String)
    date = Column(String, index=True)
    link = Column(String, unique=True)
