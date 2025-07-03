import pytest
from core.models.item import Item
from core.models.item_list import ItemList  # Adjust import path if needed

# $env:PYTHONPATH="."
# pytest -q tests/core/test_item_list.py

def make_sample_item(id="apple", quantity=1, category_id="fruit", visible=True):
    return Item(
        id=id,
        name={"en": id.capitalize()},
        category_id=category_id,
        quantity=quantity,
        visible=visible
    )

def test_init_empty_and_with_items():
    empty_list = ItemList()
    assert empty_list.get_copy() == []

    items = [make_sample_item(id="item1"), make_sample_item(id="item2")]
    ilist = ItemList(items)
    assert ilist.get_copy() == items

def test_add_item_new_and_existing():
    ilist = ItemList()
    item1 = make_sample_item(id="banana", quantity=1)
    ilist = ilist.add_item(item1)
    assert len(ilist.get_copy()) == 1
    assert ilist.get_item("banana").quantity == 1

    # Add same item again with quantity=2 should increase quantity by 2 (1+2=3)
    item_more = make_sample_item(id="banana", quantity=2)
    ilist2 = ilist.add_item(item_more)
    assert len(ilist2.get_copy()) == 1
    assert ilist2.get_item("banana").quantity == 3

def test_add_item_zero_quantity_not_added():
    ilist = ItemList()
    item0 = make_sample_item(id="zero", quantity=0)
    ilist2 = ilist.add_item(item0)
    # Should still be empty since quantity=0 is ignored
    assert len(ilist2.get_copy()) == 0

def test_increase_quantity():
    ilist = ItemList()
    item1 = make_sample_item(id="carrot")
    ilist = ilist.add_item(item1)
    ilist2 = ilist.increase_quantity("carrot")
    assert ilist2.get_item("carrot").quantity == 2

    with pytest.raises(ValueError):
        ilist.increase_quantity("nonexistent")

def test_update_quantity_changes_and_removes():
    ilist = ItemList()
    item1 = make_sample_item(id="tomato", quantity=5)
    ilist = ilist.add_item(item1)

    ilist2 = ilist.update_quantity("tomato", 3)
    assert ilist2.get_item("tomato").quantity == 3

    # Quantity zero removes the item
    ilist3 = ilist2.update_quantity("tomato", 0)
    assert ilist3.get_item("tomato") is None
    assert len(ilist3.get_copy()) == 0

    with pytest.raises(ValueError):
        ilist.update_quantity("nonexistent", 2)

def test_remove_item():
    ilist = ItemList()
    item1 = make_sample_item(id="egg")
    item2 = make_sample_item(id="milk")
    ilist = ilist.add_item(item1).add_item(item2)

    ilist2 = ilist.remove_item("egg")
    assert ilist2.get_item("egg") is None
    assert ilist2.get_item("milk") is not None

    # Removing non-existent item does nothing
    ilist3 = ilist2.remove_item("nonexistent")
    assert len(ilist3.get_copy()) == 1

def test_set_visibility_by_category():
    items = [
        make_sample_item(id="item1", category_id="cat1", visible=True),
        make_sample_item(id="item2", category_id="cat2", visible=True),
        make_sample_item(id="item3", category_id="cat1", visible=True),
    ]
    ilist = ItemList(items)
    ilist2 = ilist.set_visibility_by_category("cat1", False)

    assert ilist2.get_item("item1").visible is False
    assert ilist2.get_item("item3").visible is False
    assert ilist2.get_item("item2").visible is True

def test_get_item_returns_none_for_missing():
    ilist = ItemList()
    assert ilist.get_item("missing") is None

def test_encapsulation_get_copy_returns_copy_not_reference():
    item = make_sample_item()
    ilist = ItemList([item])
    copy_list = ilist.get_copy()
    assert copy_list == [item]

    # Modify returned list - should not affect internal _items
    copy_list.append(make_sample_item(id="newitem"))
    assert len(copy_list) == 2
    assert len(ilist.get_copy()) == 1

def test_immutability_of_methods():
    ilist = ItemList()
    item1 = make_sample_item(id="banana")
    ilist2 = ilist.add_item(item1)

    # Original list remains unchanged
    assert len(ilist.get_copy()) == 0
    assert len(ilist2.get_copy()) == 1

    ilist3 = ilist2.update_quantity("banana", 5)
    assert ilist2.get_item("banana").quantity == 1
    assert ilist3.get_item("banana").quantity == 5
