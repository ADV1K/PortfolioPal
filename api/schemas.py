from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from .enums import ItemCategory, Source


class AlphaStreetOut(BaseModel):
    symbol: str
    category: ItemCategory
    title: str
    date: datetime
    link: str

    class Config:
        from_attributes = True


class TrackItemIn(BaseModel):
    symbol: str = Field(examples=["TCS"])
    in_portfolio: bool = Field(default=False, alias="inPortfolio", examples=[True])
    last_fetched_date: datetime | None = Field(
        default="1970-01-01T00:00:00.000",
        alias="lastFetchedDate",
        examples=["2023-07-01T14:34:34.177"],
    )
    # categories: tuple[ItemCategory, ...] | tuple[()] = Field(default=())

    @field_validator("symbol")
    def uppercase_symbol(cls, v):
        # convert symbol to uppercase, so that we can compare it with the symbol in the database
        return v.upper()

    # @field_validator("categories", mode="before")
    # def categories(cls, v):
    #     # convert a comma separated list of categories into a tuple of ItemCategory objects
    #     if isinstance(v, str):
    #         return tuple(ItemCategory(c) for c in v.split(","))
    #     return v

    @field_validator("last_fetched_date")
    def validate_date(cls, v):
        # if no date is provided, set it to unix epoch, so that all records are fetched
        if not v:
            return datetime.fromtimestamp(0)
        return v


class TrackItemOut(BaseModel):
    symbol: str
    category: ItemCategory
    short_code: str
    link: str
    title: str
    date: datetime
    summary: str | None = None


class PlaygroundItemIn(BaseModel):
    prompt: str


class PlaygroundItemOut(PlaygroundItemIn):
    link: str
    title: str
    description: str
    content: str
    summary: str = ""
    cost: int = 0
