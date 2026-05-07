"""Item router"""

from typing import Literal
from fastapi import APIRouter, HTTPException, Query
from app.services import item_services
from app.schemas.item_schema import ItemCreateRequest, ItemResponse, ItemUpdateRequest, ItemPatchRequest    
from app.exceptions import AppBaseException, DuplicateItemNameError, InvalidPriceRangeError, ItemNotFoundError
from app.schemas.error_schema import ErrorResponse


def _error(exc: AppBaseException) -> dict:
    return ErrorResponse(code=exc.code, message=str(exc)).model_dump(exclude_none=True)


router = APIRouter(
    prefix="/items",
    tags=["items"]
)


@router.get("/", response_model=list[ItemResponse])
def get_all_items(
    category: str | None = Query(default=None),
    min_price: float | None = Query(default=None, gt=0),
    max_price: float | None = Query(default=None, gt=0),
    sort_by: Literal["name", "price"] | None = Query(default=None),
    order: Literal["asc", "desc"] = Query(default="asc"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
) -> list[ItemResponse]:
    try:
        return item_services.get_all_items(
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
def get_item(item_id: int) -> ItemResponse:
    try:
        return item_services.get_item(item_id)
    except ItemNotFoundError as e:
        raise HTTPException(status_code=404, detail=_error(e))


@router.post("/", status_code=201, response_model=ItemResponse)
def create_item(request: ItemCreateRequest) -> ItemResponse:
    try:
        return item_services.create_item(request)
    except DuplicateItemNameError as e:
        raise HTTPException(status_code=409, detail=_error(e))
    

@router.put("/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, request: ItemUpdateRequest) -> ItemResponse:
    try:
        return item_services.update_item(item_id, request)
    except ItemNotFoundError as e:
        raise HTTPException(status_code=404, detail=_error(e))


@router.patch("/{item_id}", response_model=ItemResponse)
def patch_item(item_id: int, request: ItemPatchRequest) -> ItemResponse:
    try:
        return item_services.patch_item(item_id, request)
    except ItemNotFoundError as e:
        raise HTTPException(status_code=404, detail=_error(e))

@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int) -> None:
    try:
        item_services.delete_item(item_id)
    except ItemNotFoundError as e:
        raise HTTPException(status_code=404, detail=_error(e))
    
