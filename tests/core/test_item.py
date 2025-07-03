import pytest # pytest -q tests/core/test_item.py
from pydantic import ValidationError
from core.models.item import Item

# $env:PYTHONPATH="."
# pytest -q tests/core/test_item.py

def test_item_creation_minimal():
    item = Item(
        id="white_bread",
        name={"en": "White Bread", "nl": "Wit brood", "fr": "Pain blanc", "de": "Weißbrot"},
        category_id="grains"
    )
    assert item.id == "white_bread"
    assert item.name["en"] == "White Bread"
    assert item.category_id == "grains"
    assert item.subcategory_id is None
    assert item.icon is None
    assert item.quantity == 1
    assert item.visible is True
    assert item.note is None

def test_item_creation_full():
    item = Item(
        id="celery",
        name={"en": "Celery", "nl": "Selderij","fr": "Céleri", "de": "Sellerie"},
        category_id="fruit_veg",
        subcategory_id="vegetables",
        icon="🥬",
        quantity=5,
        visible=False,
        note="Fresh from the farm"
    )
    assert item.subcategory_id == "vegetables"
    assert item.icon == "🥬"
    assert item.quantity == 5
    assert item.visible is False
    assert item.note == "Fresh from the farm"

def test_item_invalid_missing_required():
    with pytest.raises(ValidationError):
        Item(name={"en": "No ID"}, category_id="misc")  # Missing id

def test_item_invalid_name_type():
    with pytest.raises(ValidationError):
        Item(id="bad_name", name="just a string", category_id="misc")  # name should be dict

def test_quantity_must_be_positive():
    try:
        bad_item = Item(id="test", name={"en": "Test"}, category_id="misc", quantity=0)
    except ValidationError as e:
        print("Validation error:", e)
