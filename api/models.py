from datetime import datetime

from sqlalchemy import Column, Enum, String, DateTime, BigInteger, func
from sqlalchemy.ext.hybrid import hybrid_property

from .database import Base
from .enums import ItemCategory


class AlphaStreet(Base):
    __tablename__ = "alphastreet"

    link = Column(String, primary_key=True)
    short_code = Column(String)
    symbol = Column(String, index=True)
    category = Column(Enum(ItemCategory), index=True)
    title = Column(String)
    date = Column(DateTime, index=True)
    scraped_date = Column(DateTime, index=True)


class MoneyControl(Base):
    __tablename__ = "moneycontrol"

    link = Column(String, primary_key=True)
    short_code = Column(String)
    symbol = Column(String, index=True)
    category = Column(Enum(ItemCategory), index=True)
    title = Column(String)
    description = Column(String)
    content = Column(String)
    date = Column(DateTime, index=True)
    scraped_date = Column(DateTime, index=True)
    summary = Column(String)


class YouTube(Base):
    __tablename__ = "youtube"

    link = Column(String, primary_key=True)
    short_code = Column(String)
    symbol = Column(String, index=True)
    category = Column(Enum(ItemCategory), index=True)
    views = Column(BigInteger)
    name = Column(String)
    sector = Column(String)
    title = Column(String)
    channel = Column(String)
    date = Column(DateTime, index=True)
    scraped_date = Column(DateTime, index=True)

    # calculate relevancy as views / weeks since upload; higher is better
    @hybrid_property
    def relevancy(self):
        return self.views / ((datetime.now() - self.date).days / 7 + 1)

    @relevancy.expression
    def relevancy(cls):
        return cls.views / (func.extract("day", func.now() - cls.date) / 7 + 1)
