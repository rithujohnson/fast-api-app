"""Item schemas"""

from pydantic import BaseModel, ConfigDict, Field


class ItemCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)
    category: str = Field(min_length=1, max_length=50)
    description: str | None = Field(default=None, max_length=300)


class ItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: float
    category: str
    description: str | None

class ItemUpdateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)
    category: str = Field(min_length=1, max_length=50)
    description: str | None = Field(default=None, max_length=300)

class ItemPatchRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    price: float | None = Field(default=None, gt=0)
    category: str | None = Field(default=None, min_length=1, max_length=50)
    description: str | None = Field(default=None, max_length=300)