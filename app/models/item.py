"""Item model"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Item:
    id: int
    name: str
    price: float
    category: str
    description: str | None
