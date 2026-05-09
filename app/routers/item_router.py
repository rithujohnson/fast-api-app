"""Item router"""

from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.services import item_services
from app.schemas.item_schema import ItemCreateRequest, ItemResponse, ItemUpdateRequest, ItemPatchRequest
from app.exceptions import AppBaseException, DuplicateItemNameError, InvalidCategoryError, InvalidPriceRangeError, ItemNotFoundError
from app.schemas.error_schema import ErrorResponse
from app.dependencies import get_current_user, require_admin
from app.models.user import User

def _error(exc: AppBaseException) -> dict:
    return ErrorResponse(code=exc.code, message=str(exc)).model_dump(exclude_none=True)


router = APIRouter(
    prefix="/items",
    tags=["items"]
)


@router.get("/", response_model=list[ItemResponse])
async def get_all_items(
    category: str | None = Query(default=None),
    min_price: float | None = Query(default=None, gt=0),
    max_price: float | None = Query(default=None, gt=0),
    sort_by: Literal["name", "price"] | None = Query(default=None),
    order: Literal["asc", "desc"] = Query(default="asc"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> list[ItemResponse]:
    try:
        return await item_services.get_all_items(
            db=db,
            category=category,
            min_price=min_price,
            max_price=max_price,
            sort_by=sort_by,
            order=order,
            skip=skip,
            limit=limit,
        )
    except InvalidPriceRangeError as e:
        raise HTTPException(status_code=400, detail=_error(e))


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)) -> ItemResponse:
    try:
        return await item_services.get_item(db, item_id)
    except ItemNotFoundError as e:
        raise HTTPException(status_code=404, detail=_error(e))


@router.post("/", status_code=201, response_model=ItemResponse)
async def create_item(request: ItemCreateRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)) -> ItemResponse:
    try:
        return await item_services.create_item(db, request)
    except DuplicateItemNameError as e:
        raise HTTPException(status_code=409, detail=_error(e))
    except InvalidCategoryError as e:
        raise HTTPException(status_code=400, detail=_error(e))


@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(item_id: int, request: ItemUpdateRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)) -> ItemResponse:
    try:
        return await item_services.update_item(db, item_id, request)
    except ItemNotFoundError as e:
        raise HTTPException(status_code=404, detail=_error(e))
    except InvalidCategoryError as e:
        raise HTTPException(status_code=400, detail=_error(e))


@router.patch("/{item_id}", response_model=ItemResponse)
async def patch_item(item_id: int, request: ItemPatchRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)) -> ItemResponse:
    try:
        return await item_services.patch_item(db, item_id, request)
    except ItemNotFoundError as e:
        raise HTTPException(status_code=404, detail=_error(e))
    except InvalidCategoryError as e:
        raise HTTPException(status_code=400, detail=_error(e))


@router.delete("/{item_id}", status_code=204)
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_admin)) -> None:
    try:
        await item_services.delete_item(db, item_id)
    except ItemNotFoundError as e:
        raise HTTPException(status_code=404, detail=_error(e))
