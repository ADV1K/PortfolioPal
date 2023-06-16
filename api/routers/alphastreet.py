from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import AlphaStreet

router = APIRouter(prefix="/alphastreet", tags=["alphastreet"])


# Data access layer
def get_latest_items(db: Session, category: str = None, symbol: str = None):
    query = db.query(AlphaStreet)
    if category:
        query = query.filter(AlphaStreet.category == category)
    if symbol:
        query = query.filter(AlphaStreet.symbol == symbol)

    # only fetch records of the last 90 days using datetime.timedelta
    filter_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    query = query.filter(AlphaStreet.date >= filter_date)

    return query.order_by(AlphaStreet.date.desc())


# Routes
@router.get("/latest", response_model=Page)
async def get_latest(category: str = None, db: Session = Depends(get_db)):
    return paginate(get_latest_items(db, category=category))


@router.get("/{symbol}", response_model=Page)
async def get_ticker(symbol: str, db: Session = Depends(get_db)):
    return paginate(get_latest_items(db, symbol=symbol.upper()))
