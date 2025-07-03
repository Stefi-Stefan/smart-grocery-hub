from typing import List, Optional
from core.models.item import Item

class ItemList:
    def __init__(self, items: Optional[List[Item]] = None):
        """
        Initialize the ItemList with an optional list of Item objects.
        """
        self._items = items[:] if items else []

    def add_item(self, new_item: Item) -> "ItemList":
        """
        Add a new item to the list.
        If item with the same id exists, increase its quantity by new_item.quantity.
        Items with quantity == 0 are not added.
        """
        if new_item.quantity == 0:
            return ItemList(self._items)  # Ignore zero quantity

        new_items = []
        found = False
        for item in self._items:
            if item.id == new_item.id:
                updated_quantity = item.quantity + new_item.quantity
                new_items.append(item.model_copy(update={"quantity": updated_quantity}))
                found = True
            else:
                new_items.append(item)
        if not found:
            new_items.append(new_item)
        return ItemList(new_items)

    def increase_quantity(self, item_id: str) -> "ItemList":
        """
        Increase the quantity of the specified item by 1.
        Raises ValueError if the item does not exist.
        """
        existing = self.get_item(item_id)
        if not existing:
            raise ValueError(f"Item with id '{item_id}' not found.")
        return self.update_quantity(item_id, existing.quantity + 1)

    def update_quantity(self, item_id: str, quantity: int) -> "ItemList":
        """
        Update the quantity of the specified item.
        Removes the item if quantity is == 0.
        Raises ValueError if the item does not exist.
        """
        new_items = []
        found = False
        for item in self._items:
            if item.id == item_id:
                found = True
                if quantity > 0:
                    new_items.append(item.model_copy(update={"quantity": quantity}))
                # omit item if quantity == 0 to remove it
            else:
                new_items.append(item)
        if not found:
            raise ValueError(f"Item with id '{item_id}' not found.")
        return ItemList(new_items)

    def remove_item(self, item_id: str) -> "ItemList":
        """
        Remove the item with the specified id from the list.
        """
        new_items = [item for item in self._items if item.id != item_id]
        return ItemList(new_items)

    def set_visibility_by_category(self, category_id: str, visible: bool) -> "ItemList":
        """
        Set the visibility flag for all items in the given category.
        """
        new_items = [
            item.model_copy(update={"visible": visible}) if item.category_id == category_id else item
            for item in self._items
        ]
        return ItemList(new_items)

    def get_item(self, item_id: str) -> Optional[Item]:
        """
        Retrieve an item by its id.
        Returns None if the item is not found.
        """
        for item in self._items:
            if item.id == item_id:
                return item
        return None

    def get_copy(self) -> List[Item]:
        """
        Return a copy of the items list to prevent external modification.
        """
        return self._items[:]
