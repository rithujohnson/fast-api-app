"""Unit tests for item service"""

import pytest
from unittest.mock import patch
from app.models.item import Item
from app.models.category import Category
from app.schemas.item_schema import ItemCreateRequest, ItemUpdateRequest, ItemPatchRequest
from app.services import item_services
from app.exceptions import DuplicateItemNameError, InvalidCategoryError, InvalidPriceRangeError, ItemNotFoundError


pytestmark = pytest.mark.unit

APPLE = Item(id=1, name="Apple", price=1.50, category=Category("Fruit"), description="A juicy red apple")
BANANA = Item(id=2, name="Banana", price=0.75, category=Category("Fruit"), description="A sweet yellow banana")


# --- get_all_items ---

def test_get_all_items_returns_list():
    mock_items = [APPLE, BANANA]
    with patch("app.services.item_services.item_repository.get_all", return_value=mock_items) as mock:
        result = item_services.get_all_items()
        mock.assert_called_once_with(
            category=None,
            min_price=None,
            max_price=None,
            sort_by=None,
            order="asc",
            skip=0,
            limit=10,
        )
        assert len(result) == 2
        assert result[0].name == "Apple"


def test_get_all_items_forwards_filters_to_repository():
    with patch("app.services.item_services.item_repository.get_all", return_value=[APPLE]) as mock:
        item_services.get_all_items(
            category="Fruit",
            min_price=1.00,
            max_price=2.00,
            sort_by="price",
            order="desc",
            skip=0,
            limit=5,
        )
        mock.assert_called_once_with(
            category="Fruit",
            min_price=1.00,
            max_price=2.00,
            sort_by="price",
            order="desc",
            skip=0,
            limit=5,
        )


def test_get_all_items_raises_when_min_price_greater_than_max_price():
    with pytest.raises(InvalidPriceRangeError) as exc_info:
        item_services.get_all_items(min_price=5.00, max_price=1.00)
    assert exc_info.value.min_price == 5.00
    assert exc_info.value.max_price == 1.00


# --- get_item ---

def test_get_item_returns_item_when_found():
    with patch("app.services.item_services.item_repository.get_by_id", return_value=APPLE) as mock:
        result = item_services.get_item(1)
        mock.assert_called_once_with(1)
        assert result.id == 1
        assert result.name == "Apple"


def test_get_item_raises_when_not_found():
    with patch("app.services.item_services.item_repository.get_by_id", side_effect=ItemNotFoundError(99)) as mock:
        with pytest.raises(ItemNotFoundError) as exc_info:
            item_services.get_item(99)
        mock.assert_called_once_with(99)
        assert exc_info.value.item_id == 99


# --- create_item ---

def test_create_item_returns_created_item():
    request = ItemCreateRequest(name="Mango", price=2.00, category="Fruit")
    mock_created = Item(id=3, name="Mango", price=2.00, category=Category("Fruit"), description=None)
    with patch("app.services.item_services.item_repository.create", return_value=mock_created) as mock:
        result = item_services.create_item(request)
        mock.assert_called_once_with(name="Mango", price=2.00, category="Fruit", description=None)
        assert result.id == 3
        assert result.name == "Mango"
        assert result.price == 2.00


def test_create_item_raises_on_duplicate_name():
    request = ItemCreateRequest(name="Apple", price=1.50, category="Fruit")
    with patch("app.services.item_services.item_repository.create", side_effect=DuplicateItemNameError("Apple")) as mock:
        with pytest.raises(DuplicateItemNameError) as exc_info:
            item_services.create_item(request)
        mock.assert_called_once_with(name="Apple", price=1.50, category="Fruit", description=None)
        assert exc_info.value.name == "Apple"


def test_create_item_raises_on_invalid_category():
    request = ItemCreateRequest(name="Candy Bar", price=1.00, category="Fruit")
    with patch("app.services.item_services.item_repository.create", side_effect=InvalidCategoryError("Candy")) as mock:
        with pytest.raises(InvalidCategoryError) as exc_info:
            item_services.create_item(request)
        assert exc_info.value.name == "Candy"


# --- update_item ---

def test_update_item_returns_updated_item():
    request = ItemUpdateRequest(name="Green Apple", price=2.00, category="Fruit", description="A tart green apple")
    mock_updated = Item(id=1, name="Green Apple", price=2.00, category=Category("Fruit"), description="A tart green apple")
    with patch("app.services.item_services.item_repository.update", return_value=mock_updated) as mock:
        result = item_services.update_item(1, request)
        mock.assert_called_once_with(
            item_id=1, name="Green Apple", price=2.00, category="Fruit", description="A tart green apple"
        )
        assert result.name == "Green Apple"
        assert result.price == 2.00


def test_update_item_raises_when_not_found():
    request = ItemUpdateRequest(name="Ghost", price=1.00, category="Fruit", description=None)
    with patch("app.services.item_services.item_repository.update", side_effect=ItemNotFoundError(99)) as mock:
        with pytest.raises(ItemNotFoundError) as exc_info:
            item_services.update_item(99, request)
        mock.assert_called_once_with(item_id=99, name="Ghost", price=1.00, category="Fruit", description=None)
        assert exc_info.value.item_id == 99


def test_update_item_raises_on_invalid_category():
    request = ItemUpdateRequest(name="Apple", price=1.50, category="Fruit")
    with patch("app.services.item_services.item_repository.update", side_effect=InvalidCategoryError("Invalid")) as mock:
        with pytest.raises(InvalidCategoryError) as exc_info:
            item_services.update_item(1, request)
        assert exc_info.value.name == "Invalid"


# --- patch_item ---

def test_patch_item_returns_patched_item():
    request = ItemPatchRequest(price=3.00)
    mock_patched = Item(id=1, name="Apple", price=3.00, category=Category("Fruit"), description="A juicy red apple")
    with patch("app.services.item_services.item_repository.patch", return_value=mock_patched) as mock:
        result = item_services.patch_item(1, request)
        mock.assert_called_once_with(item_id=1, name=None, price=3.00, category=None, description=None)
        assert result.price == 3.00
        assert result.name == "Apple"


def test_patch_item_raises_when_not_found():
    request = ItemPatchRequest(name="Ghost")
    with patch("app.services.item_services.item_repository.patch", side_effect=ItemNotFoundError(99)) as mock:
        with pytest.raises(ItemNotFoundError) as exc_info:
            item_services.patch_item(99, request)
        mock.assert_called_once_with(item_id=99, name="Ghost", price=None, category=None, description=None)
        assert exc_info.value.item_id == 99


def test_patch_item_raises_on_invalid_category():
    request = ItemPatchRequest(category="Fruit")
    with patch("app.services.item_services.item_repository.patch", side_effect=InvalidCategoryError("Invalid")) as mock:
        with pytest.raises(InvalidCategoryError) as exc_info:
            item_services.patch_item(1, request)
        assert exc_info.value.name == "Invalid"


# --- delete_item ---

def test_delete_item_succeeds_when_found():
    with patch("app.services.item_services.item_repository.delete", return_value=None) as mock:
        item_services.delete_item(1)  # should not raise
        mock.assert_called_once_with(1)


def test_delete_item_raises_when_not_found():
    with patch("app.services.item_services.item_repository.delete", side_effect=ItemNotFoundError(99)) as mock:
        with pytest.raises(ItemNotFoundError) as exc_info:
            item_services.delete_item(99)
        mock.assert_called_once_with(99)
        assert exc_info.value.item_id == 99


# --- get_all_categories ---

def test_get_all_categories_returns_set_from_repository():
    mock_categories = {Category("Fruit"), Category("Vegetable")}
    with patch("app.services.item_services.item_repository.get_all_categories", return_value=mock_categories) as mock:
        result = item_services.get_all_categories()
        mock.assert_called_once()
        assert result == mock_categories
