from datetime import datetime, timedelta
import asyncio

from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import Session
import openai

from api.enums import ItemCategory, UserType
from api.models import AlphaStreet, YouTube, MoneyControl
from api.schemas import TrackItemIn, TrackItemOut, PlaygroundItemIn, PlaygroundItemOut

from config import config


async def summarize(item: PlaygroundItemOut) -> PlaygroundItemOut:
    openai.api_key = config.OPENAI_API_KEY
    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": item.prompt},
            {"role": "user", "content": item.content},
        ],
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )

    # approximate cost of the request, in rupees
    item.cost = (response.usage.prompt_tokens / 1000 * 0.0015 + response.usage.completion_tokens / 1000 * 0.002) * 83.32
    item.summary = response.choices[0].message.content
    return item


async def get_moneycontrol_items_and_summary(db: Session, prompt: str, count: int) -> list[PlaygroundItemOut]:
    # get the last 10 moneycontrol items, sorted by date descending
    query = db.query(MoneyControl).order_by(MoneyControl.date.desc()).limit(count)

    tasks = []
    for item in query.all():
        item = PlaygroundItemOut(
            link=item.link,
            title=item.title,
            description=item.description,
            content=item.content,
            prompt=prompt,
        )
        tasks.append(summarize(item))
    items = await asyncio.gather(*tasks)
    return items


def get_track_items(db: Session, items: list[TrackItemIn], categories: list[ItemCategory]) -> list[TrackItemOut]:
    # we don't want to send all the attributes, and we want to maintain a valid schema for each item,
    # so we create a new list of TrackItemOut objects with only the required attributes
    result = []

    # get the items from all the sources
    moneycontrol = get_moneycontrol_items(db, items, categories)
    alphastreet = get_alphastreet_items(db, items, categories)
    youtube = get_youtube_videos(db, items, categories)

    # convert the items into TrackItemOut objects
    for item in moneycontrol + alphastreet + youtube:
        result.append(TrackItemOut(**item._mapping))

    # Sort the result by date
    result.sort(key=lambda x: x.date, reverse=True)

    return result


def get_moneycontrol_items(db: Session, items: list[TrackItemIn], categories: list[ItemCategory]) -> list[AlphaStreet]:
    """Get MoneyControl articles for a given symbol, works for multiple symbols"""
    subquery = select(
        MoneyControl,
        func.row_number().over(partition_by=MoneyControl.symbol, order_by=MoneyControl.date.desc()).label("row_num"),
    )
    if categories:
        subquery = subquery.filter(MoneyControl.category.in_(categories))
    subquery = subquery.subquery()

    # create the main query, which filters the subquery to only show the most relevant article for each symbol
    query = db.query(subquery).filter(
        and_(
            # only show the most relevant article for each symbol
            subquery.c.row_num <= 2,
            or_(
                # unpack the generator to pass each item as a separate argument; see: unpacking operator
                *(
                    # only show articles that are newer than the last fetched date
                    and_(
                        subquery.c.symbol == item.symbol,
                        subquery.c.scraped_date > item.last_fetched_date,
                        subquery.c.date.isnot(None),
                    )
                    for item in items
                )
            ),
        )
    )

    # print(query.statement.compile(compile_kwargs={"literal_binds": True}))
    return query.all()


def get_youtube_videos(db: Session, items: list[TrackItemIn], categories: list[ItemCategory]) -> list[YouTube]:
    """Get YouTube videos for a given symbol, sorted by relevancy, works for multiple symbols"""

    # if the user doesn't want YouTube videos, return an empty list
    if categories and ItemCategory.youtube_video not in categories:
        return []

    # create a subquery to get the most relevant youtube_video for each symbol
    subquery = select(
        YouTube,
        func.row_number().over(partition_by=YouTube.symbol, order_by=YouTube.relevancy.desc()).label("row_num"),
    ).subquery()

    # create the main query, which filters the subquery to only show the most relevant youtube_video for each symbol
    query = db.query(subquery).filter(
        and_(
            # only show the most relevant youtube_video for each symbol
            subquery.c.row_num == 1,
            or_(
                # unpack the generator to pass each item as a separate argument; see: unpacking operator
                *(
                    # only show videos that are newer than the last fetched date
                    and_(
                        subquery.c.symbol == item.symbol,
                        subquery.c.scraped_date > item.last_fetched_date,
                    )
                    for item in items
                )
            ),
        )
    )

    # print(query.statement.compile(compile_kwargs={"literal_binds": True}))
    return query.all()


def get_alphastreet_items(db: Session, items: list[TrackItemIn], categories: list[ItemCategory]) -> list[AlphaStreet]:
    """Get AlphaStreet articles for a given symbol, works for multiple symbols"""
    subquery = select(
        AlphaStreet,
        func.row_number().over(partition_by=AlphaStreet.symbol, order_by=AlphaStreet.date.desc()).label("row_num"),
    )
    if categories:
        subquery = subquery.filter(AlphaStreet.category.in_(categories))
    subquery = subquery.subquery()

    # create the main query, which filters the subquery to only show the most relevant article for each symbol
    query = db.query(subquery).filter(
        and_(
            # only show the most relevant article for each symbol
            subquery.c.row_num <= 2,
            or_(
                # unpack the generator to pass each item as a separate argument; see: unpacking operator
                *(
                    # only show articles that are newer than the last fetched date
                    and_(
                        subquery.c.symbol == item.symbol,
                        subquery.c.scraped_date > item.last_fetched_date,
                        subquery.c.date.isnot(None),
                    )
                    for item in items
                )
            ),
        )
    )

    # print(query.statement.compile(compile_kwargs={"literal_binds": True}))
    return query.all()


def get_youtube_videos2(db: Session, item: TrackItemIn) -> YouTube:
    """Get YouTube videos for a given symbol, sorted by relevancy"""
    query = db.query(YouTube).filter(YouTube.symbol == item.symbol)
    if item.last_fetched_date:
        query = query.filter(YouTube.date > item.last_fetched_date)

    query = query.order_by(YouTube.relevancy.desc())
    # print(query.statement.compile(compile_kwargs={"literal_binds": True}))
    return query.first()


def get_alphastreet_items2(
    db: Session,
    category: ItemCategory | None = None,
    user_type: UserType = UserType.new,
    symbol: str | None = None,
):
    # fetch records of last 90 days for new users, and last day for existing users
    filter_date = datetime.now() - timedelta(days=90)

    query = db.query(AlphaStreet)
    if category:
        query = query.filter(AlphaStreet.category == category)
    if symbol:
        query = query.filter(AlphaStreet.symbol == symbol)
    if user_type is UserType.existing:
        # only show very recent data to new users
        filter_date = datetime.now() - timedelta(days=1)

    query = query.filter(AlphaStreet.date >= filter_date)
    return query.order_by(AlphaStreet.date.desc())
