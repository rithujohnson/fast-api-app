"""Categories router"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.services import item_services


router = APIRouter(
    prefix="/categories",
    tags=["categories"]
)


@router.get("/", response_model=list[str])
async def get_all_categories(db: AsyncSession = Depends(get_db)) -> list[str]:
    categories = await item_services.get_all_categories(db)
    return sorted(str(c) for c in categories)