"""Item router"""

from typing import Literal
from fastapi import APIRouter, HTTPException, Query
from app.services import item_services
from app.schemas.item_schema import ItemCreateRequest, ItemResponse, ItemUpdateRequest, ItemPatchRequest    


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
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: int) -> ItemResponse:
    item = item_services.get_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="item not found")
    return item


@router.post("/", status_code=201, response_model=ItemResponse)
def create_item(request: ItemCreateRequest) -> ItemResponse:
    return item_services.create_item(request)

@router.put("/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, request: ItemUpdateRequest) -> ItemResponse:
    item = item_services.update_item(item_id, request)
    if item is None:
        raise HTTPException(status_code=404, detail="item not found")
    return item 

@router.patch("/{item_id}", response_model=ItemResponse)
def patch_item(item_id: int, request: ItemPatchRequest) -> ItemResponse:
    item = item_services.patch_item(item_id, request)
    if item is None:
        raise HTTPException(status_code=404, detail="item not found")
    return item

@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int) -> None:
    success = item_services.delete_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="item not found")   
    
