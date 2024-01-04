from enum import StrEnum, auto


class AlphaStreetCategory(StrEnum):
    concall_transcripts = auto()
    concall_insights = auto()
    earnings = auto()
    infographics = auto()
    stock_analysis = auto()
    research_summary = auto()
    research_tear_sheet = auto()
    ipo = auto()
    other = auto()


class ItemCategory(StrEnum):
    alphastreet_concall_transcripts = auto()
    alphastreet_concall_insights = auto()
    alphastreet_earnings = auto()
    alphastreet_infographics = auto()
    alphastreet_stock_analysis = auto()
    alphastreet_research_summary = auto()
    alphastreet_research_tear_sheet = auto()
    alphastreet_ipo = auto()
    alphastreet_other = auto()

    youtube_video = auto()

    moneycontrol_news = auto()


class UserType(StrEnum):
    new = auto()
    existing = auto()


class Source(StrEnum):
    alphastreet = auto()
    youtube = auto()
    moneycontrol = auto()
