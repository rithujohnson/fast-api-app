"""Unit tests for Category model"""

import pytest
from app.models.category import Category
from app.exceptions import InvalidCategoryError


pytestmark = pytest.mark.unit


# --- is_valid ---

def test_is_valid_returns_true_for_known_category():
    assert Category.is_valid("Fruit") is True


def test_is_valid_returns_false_for_unknown_category():
    assert Category.is_valid("Candy") is False


def test_is_valid_is_case_sensitive():
    assert Category.is_valid("fruit") is False


# --- from_string ---

def test_from_string_returns_category_for_valid_name():
    cat = Category.from_string("Fruit")
    assert cat.name == "Fruit"


def test_from_string_raises_for_invalid_name():
    with pytest.raises(InvalidCategoryError) as exc_info:
        Category.from_string("Candy")
    assert exc_info.value.name == "Candy"


# --- __str__ ---

def test_str_returns_name():
    assert str(Category("Fruit")) == "Fruit"


# --- __repr__ ---

def test_repr_returns_debug_string():
    assert repr(Category("Fruit")) == "Category(name='Fruit')"


# --- __eq__ ---

def test_eq_same_name_is_equal():
    assert Category("Fruit") == Category("Fruit")


def test_eq_different_names_are_not_equal():
    assert Category("Fruit") != Category("Vegetable")


def test_eq_is_case_insensitive():
    assert Category("fruit") == Category("Fruit")


# --- __hash__ ---

def test_hash_same_name_same_hash():
    assert hash(Category("Fruit")) == hash(Category("Fruit"))


def test_hash_is_case_insensitive():
    assert hash(Category("fruit")) == hash(Category("Fruit"))


# --- set deduplication ---

def test_set_deduplicates_same_category():
    categories = {Category("Fruit"), Category("Fruit"), Category("Vegetable")}
    assert len(categories) == 2


def test_set_deduplication_is_case_insensitive():
    categories = {Category("Fruit"), Category("fruit")}
    assert len(categories) == 1
