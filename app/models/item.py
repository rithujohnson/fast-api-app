"""Item model"""

from dataclasses import dataclass
from app.models.category import Category


@dataclass(frozen=True)
class Item:
    id: int
    name: str
    price: float
    category: Category
    description: str | None

    def __str__(self) -> str:
        return f"{self.name} ({self.category}) — ${self.price:.2f}"
