"""Unit tests for item service"""

import pytest
from unittest.mock import patch
from app.models.item import Item
from app.schemas.item_schema import ItemCreateRequest, ItemUpdateRequest, ItemPatchRequest
from app.services import item_services


pytestmark = pytest.mark.unit

APPLE = Item(id=1, name="Apple", price=1.50, category="Fruit", description="A juicy red apple")
BANANA = Item(id=2, name="Banana", price=0.75, category="Fruit", description="A sweet yellow banana")


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
    with pytest.raises(ValueError, match="min_price cannot be greater than max_price"):
        item_services.get_all_items(min_price=5.00, max_price=1.00)

        
# --- get_item ---

def test_get_item_returns_item_when_found():
    with patch("app.services.item_services.item_repository.get_by_id", return_value=APPLE) as mock:
        result = item_services.get_item(1)
        mock.assert_called_once_with(1)
        assert result is not None
        assert result.id == 1
        assert result.name == "Apple"


def test_get_item_returns_none_when_not_found():
    with patch("app.services.item_services.item_repository.get_by_id", return_value=None) as mock:
        result = item_services.get_item(99)
        mock.assert_called_once_with(99)
        assert result is None


# --- create_item ---

def test_create_item_returns_created_item():
    request = ItemCreateRequest(name="Mango", price=2.00, category="Fruit")
    mock_created = Item(id=3, name="Mango", price=2.00, category="Fruit", description=None)
    with patch("app.services.item_services.item_repository.create", return_value=mock_created) as mock:
        result = item_services.create_item(request)
        mock.assert_called_once_with(name="Mango", price=2.00, category="Fruit", description=None)
        assert result.id == 3
        assert result.name == "Mango"
        assert result.price == 2.00


# --- update_item ---

def test_update_item_returns_updated_item():
    request = ItemUpdateRequest(name="Green Apple", price=2.00, category="Fruit", description="A tart green apple")
    mock_updated = Item(id=1, name="Green Apple", price=2.00, category="Fruit", description="A tart green apple")
    with patch("app.services.item_services.item_repository.update", return_value=mock_updated) as mock:
        result = item_services.update_item(1, request)
        mock.assert_called_once_with(
            item_id=1, name="Green Apple", price=2.00, category="Fruit", description="A tart green apple"
        )
        assert result is not None
        assert result.name == "Green Apple"
        assert result.price == 2.00


def test_update_item_returns_none_when_not_found():
    request = ItemUpdateRequest(name="Ghost", price=1.00, category="Other", description=None)
    with patch("app.services.item_services.item_repository.update", return_value=None) as mock:
        result = item_services.update_item(99, request)
        mock.assert_called_once_with(
            item_id=99, name="Ghost", price=1.00, category="Other", description=None
        )
        assert result is None


# --- patch_item ---

def test_patch_item_returns_patched_item():
    request = ItemPatchRequest(price=3.00)
    mock_patched = Item(id=1, name="Apple", price=3.00, category="Fruit", description="A juicy red apple")
    with patch("app.services.item_services.item_repository.patch", return_value=mock_patched) as mock:
        result = item_services.patch_item(1, request)
        mock.assert_called_once_with(item_id=1, name=None, price=3.00, category=None, description=None)
        assert result is not None
        assert result.price == 3.00
        assert result.name == "Apple"


def test_patch_item_returns_none_when_not_found():
    request = ItemPatchRequest(name="Ghost")
    with patch("app.services.item_services.item_repository.patch", return_value=None) as mock:
        result = item_services.patch_item(99, request)
        mock.assert_called_once_with(item_id=99, name="Ghost", price=None, category=None, description=None)
        assert result is None


# --- delete_item ---

def test_delete_item_returns_true_when_found():
    with patch("app.services.item_services.item_repository.delete", return_value=True) as mock:
        result = item_services.delete_item(1)
        mock.assert_called_once_with(1)
        assert result is True


def test_delete_item_returns_false_when_not_found():
    with patch("app.services.item_services.item_repository.delete", return_value=False) as mock:
        result = item_services.delete_item(99)
        mock.assert_called_once_with(99)
        assert result is False