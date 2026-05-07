"""Categories router"""

from fastapi import APIRouter
from app.services import item_services


router = APIRouter(
    prefix="/categories",
    tags=["categories"]
)


@router.get("/", response_model=list[str])
def get_all_categories() -> list[str]:
    categories = item_services.get_all_categories()
    return sorted(str(c) for c in categories)
