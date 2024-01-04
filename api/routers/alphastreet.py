from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session

from api.database import get_db
from api.services import get_alphastreet_items2
from api.enums import ItemCategory, UserType
from api.schemas import AlphaStreetOut

router = APIRouter(prefix="/alphastreet", tags=["AlphaStreet"])


# Routes
@router.get("/latest")
async def get_latest(
    category: ItemCategory | None = None,
    user_type: UserType = UserType.new,
    db: Session = Depends(get_db),
) -> Page[AlphaStreetOut]:
    return paginate(get_alphastreet_items2(db, category=category, user_type=user_type))


@router.get("/{symbol}")
async def get_ticker(
    symbol: str,
    category: ItemCategory | None = None,
    user_type: UserType = UserType.new,
    db: Session = Depends(get_db),
) -> Page[AlphaStreetOut]:
    return paginate(get_alphastreet_items2(db, symbol=symbol.upper(), category=category, user_type=user_type))
