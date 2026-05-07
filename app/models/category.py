"""Category domain model."""

from __future__ import annotations
from app.exceptions import InvalidCategoryError


class Category:
    VALID_NAMES: frozenset[str] = frozenset({"Fruit", "Vegetable", "Dairy", "Grain", "Protein"})

    def __init__(self, name: str) -> None:
        self.name = name

    @staticmethod
    def is_valid(name: str) -> bool:
        return name in Category.VALID_NAMES

    @classmethod
    def from_string(cls, name: str) -> Category:
        if not cls.is_valid(name):
            raise InvalidCategoryError(name)
        return cls(name)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"Category(name={self.name!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Category):
            return self.name.lower() == other.name.lower()
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.name.lower())
