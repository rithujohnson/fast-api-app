"""Unit tests for item schema validation"""

import pytest
from pydantic import ValidationError
from app.schemas.item_schema import ItemCreateRequest, ItemUpdateRequest, ItemPatchRequest


pytestmark = pytest.mark.unit

# --- ItemCreateRequest ---

def test_valid_item_create_request():
    request = ItemCreateRequest(name="Apple", price=1.50, category="Fruit")
    assert request.name == "Apple"
    assert request.price == 1.50
    assert request.category == "Fruit"
    assert request.description is None


def test_create_request_with_description():
    request = ItemCreateRequest(name="Apple", price=1.50, category="Fruit", description="A red apple")
    assert request.description == "A red apple"


def test_empty_name_is_rejected():
    with pytest.raises(ValidationError):
        ItemCreateRequest(name="", price=1.50, category="Fruit")


def test_name_too_long_is_rejected():
    with pytest.raises(ValidationError):
        ItemCreateRequest(name="A" * 101, price=1.50, category="Fruit")


def test_negative_price_is_rejected():
    with pytest.raises(ValidationError):
        ItemCreateRequest(name="Apple", price=-1.00, category="Fruit")


def test_zero_price_is_rejected():
    with pytest.raises(ValidationError):
        ItemCreateRequest(name="Apple", price=0, category="Fruit")


def test_missing_name_is_rejected():
    with pytest.raises(ValidationError):
        ItemCreateRequest(price=1.50, category="Fruit")


def test_missing_price_is_rejected():
    with pytest.raises(ValidationError):
        ItemCreateRequest(name="Apple", category="Fruit")


def test_create_missing_category_is_rejected():
    with pytest.raises(ValidationError):
        ItemCreateRequest(name="Apple", price=1.50)


def test_create_empty_category_is_rejected():
    with pytest.raises(ValidationError):
        ItemCreateRequest(name="Apple", price=1.50, category="")


def test_create_description_too_long_is_rejected():
    with pytest.raises(ValidationError):
        ItemCreateRequest(name="Apple", price=1.50, category="Fruit", description="A" * 301)



# --- ItemUpdateRequest ---

def test_valid_item_update_request():
    request = ItemUpdateRequest(name="Apple", price=1.50, category="Fruit", description="Updated")
    assert request.name == "Apple"
    assert request.description == "Updated"


def test_update_missing_name_is_rejected():
    with pytest.raises(ValidationError):
        ItemUpdateRequest(price=1.50, category="Fruit")


def test_update_missing_price_is_rejected():
    with pytest.raises(ValidationError):
        ItemUpdateRequest(name="Apple", category="Fruit")


def test_update_missing_category_is_rejected():
    with pytest.raises(ValidationError):
        ItemUpdateRequest(name="Apple", price=1.50)


def test_update_empty_name_is_rejected():
    with pytest.raises(ValidationError):
        ItemUpdateRequest(name="", price=1.50, category="Fruit")


def test_update_negative_price_is_rejected():
    with pytest.raises(ValidationError):
        ItemUpdateRequest(name="Apple", price=-1.00, category="Fruit")


def test_update_empty_category_is_rejected():
    with pytest.raises(ValidationError):
        ItemUpdateRequest(name="Apple", price=1.50, category="")


# --- ItemPatchRequest ---

def test_patch_all_fields_none_is_valid():
    # A completely empty patch body is valid — caller sends nothing to change
    request = ItemPatchRequest()
    assert request.name is None
    assert request.price is None
    assert request.category is None
    assert request.description is None


def test_patch_single_field_is_valid():
    request = ItemPatchRequest(price=3.00)
    assert request.price == 3.00
    assert request.name is None


def test_patch_multiple_fields_is_valid():
    request = ItemPatchRequest(name="Mango", category="Tropical")
    assert request.name == "Mango"
    assert request.category == "Tropical"


def test_patch_empty_name_is_rejected():
    with pytest.raises(ValidationError):
        ItemPatchRequest(name="")


def test_patch_empty_category_is_rejected():
    with pytest.raises(ValidationError):
        ItemPatchRequest(category="")


def test_patch_negative_price_is_rejected():
    with pytest.raises(ValidationError):
        ItemPatchRequest(price=-1.00)


def test_patch_zero_price_is_rejected():
    with pytest.raises(ValidationError):
        ItemPatchRequest(price=0)


def test_patch_name_too_long_is_rejected():
    with pytest.raises(ValidationError):
        ItemPatchRequest(name="A" * 101)


def test_patch_description_too_long_is_rejected():
    with pytest.raises(ValidationError):
        ItemPatchRequest(description="A" * 301)
