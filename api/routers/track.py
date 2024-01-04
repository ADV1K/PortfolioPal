from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session

from api.database import get_db
from api.enums import ItemCategory
from api.models import MoneyControl
from api.schemas import TrackItemIn, TrackItemOut
from api.services import get_track_items


router = APIRouter(prefix="/track", tags=["Stock Tracker"])


@router.post("/")
def track_stocks(
    items: list[TrackItemIn],
    categories: list[ItemCategory] | None = None,
    db: Session = Depends(get_db),
) -> list[TrackItemOut]:
    """Get the latest articles and videos for the given symbols"""
    if categories is None:
        categories = []
    return get_track_items(db, items, categories)


@router.get("/recent")
def get_recent_stock_news(
    count: int = 5,
    db: Session = Depends(get_db),
) -> list[TrackItemOut]:
    """Get the recently published articles"""
    query = db.query(MoneyControl).order_by(MoneyControl.date.desc()).limit(count)
    return query.all()
