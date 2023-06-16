from enum import StrEnum

from sqlalchemy import Column, Enum, Integer, String

from .database import Base


class AlphaStreetCategory(StrEnum):
    concall_transcripts = "concall_transcripts"
    concall_insights = "concall_insights"
    earnings = "earnings"
    infographics = "infographics"
    stock_analysis = "stock_analysis"
    research_summary = "research_summary"
    research_tear_sheet = "research_tear_sheet"
    ipo = "ipo"
    other = "other"


class AlphaStreet(Base):
    __tablename__ = "alphastreet"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    category = Column(Enum(AlphaStreetCategory), index=True)
    title = Column(String)
    date = Column(String, index=True)
    link = Column(String, unique=True)
