"""Categories router"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services import item_services


router = APIRouter(
    prefix="/categories",
    tags=["categories"]
)


@router.get("/", response_model=list[str])
def get_all_categories(db: Session = Depends(get_db)) -> list[str]:
    categories = item_services.get_all_categories(db)
    return sorted(str(c) for c in categories)