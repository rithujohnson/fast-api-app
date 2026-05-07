"""Custom exception hierarchy."""


class AppBaseException(Exception):
    code: str = "APP_ERROR"

    def __init__(self, message: str = "An application error occurred.") -> None:
        self.message = message
        super().__init__(self.message)


class ItemNotFoundError(AppBaseException):
    code = "ITEM_NOT_FOUND"

    def __init__(self, item_id: int) -> None:
        self.item_id = item_id
        self.message = f"Item with id {item_id} was not found."
        super().__init__(self.message)

    def __repr__(self) -> str:
        return f"ItemNotFoundError(item_id={self.item_id})"


class DuplicateItemNameError(AppBaseException):
    code = "DUPLICATE_ITEM_NAME"

    def __init__(self, name: str) -> None:
        self.name = name
        self.message = f"An item with the name '{name}' already exists."
        super().__init__(self.message)

    def __repr__(self) -> str:
        return f"DuplicateItemNameError(name={self.name!r})"
    

class InvalidPriceRangeError(AppBaseException):
    code = "INVALID_PRICE_RANGE"

    def __init__(self, min_price: float, max_price: float) -> None:
        self.min_price = min_price
        self.max_price = max_price
        self.message = f"min_price ({min_price}) cannot be greater than max_price ({max_price})."
        super().__init__(self.message)

    def __repr__(self) -> str:
        return f"InvalidPriceRangeError(min_price={self.min_price}, max_price={self.max_price})"


class InvalidCategoryError(AppBaseException):
    code = "INVALID_CATEGORY"

    def __init__(self, name: str) -> None:
        self.name = name
        self.message = f"'{name}' is not a valid category."
        super().__init__(self.message)

    def __repr__(self) -> str:
        return f"InvalidCategoryError(name={self.name!r})"