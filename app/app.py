import json
import tkinter as tk
from tkinter import ttk
import time
import os

# Build paths relative to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Load categories
with open(os.path.join(DATA_DIR, "categories.json"), "r", encoding="utf-8") as f:
    categories = json.load(f)

# Load default items
with open(os.path.join(DATA_DIR, "default_items.json"), "r", encoding="utf-8") as f:
    items = json.load(f)

class GroceryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Grocery List")

        self.grocery_list = {}  # item_name -> quantity

        self.long_press_threshold = 500  # milliseconds
        self._press_time = None
        self._press_item = None

        self.build_main_ui()

    def build_main_ui(self):
        # Frame for grocery list display (fixed place)
        self.grocery_frame = tk.Frame(self.root)
        self.grocery_frame.pack(fill="both", expand=False, pady=10)

        self.grocery_text = tk.Text(self.grocery_frame, height=10, width=50)
        self.grocery_text.pack()

        # Frame for the add button (separate from grocery list)
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(fill="x", pady=5)

        self.add_button = tk.Button(self.button_frame, text="+ Add items", command=self.open_add_items_panel)
        self.add_button.pack()

        # Panel for adding items (hidden initially)
        self.add_panel = tk.Frame(self.root)

        # Search bar in add panel
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.on_search_change)
        self.search_entry = tk.Entry(self.add_panel, textvariable=self.search_var, width=50)

        # Treeview for categories, subcategories, items
        self.tree = ttk.Treeview(self.add_panel)
        self.tree.pack(expand=True, fill="both")

        # Bind mouse press/release for long press detection
        self.tree.bind('<ButtonPress-1>', self.on_tree_press)
        self.tree.bind('<ButtonRelease-1>', self.on_tree_release)

        self.update_grocery_display()

    def open_add_items_panel(self):
        # Hide grocery list and button frames
        self.grocery_frame.pack_forget()
        self.button_frame.pack_forget()

        # Show add panel and search bar
        self.add_panel.pack(expand=True, fill="both")
        self.search_entry.pack(pady=5)

        self.populate_tree()

    def close_add_items_panel(self):
        # Hide add panel and search bar
        self.add_panel.pack_forget()
        self.search_entry.pack_forget()

        # Show grocery list and button frames
        self.grocery_frame.pack(fill="both", expand=False, pady=10)
        self.button_frame.pack(fill="x", pady=5)

        self.update_grocery_display()

    def populate_tree(self, filter_text=""):
        self.tree.delete(*self.tree.get_children())

        filter_text_lower = filter_text.lower()

        for cat in categories:
            cat_name = cat["name"]["en"]

            # Check of filter voorkomt in categorie, subcategorie of items
            def category_matches_filter():
                if filter_text_lower in cat_name.lower():
                    return True
                # Kijk in subcategories
                for subcat in cat.get("subcategories", []):
                    if filter_text_lower in subcat["name"]["en"].lower():
                        return True
                # Kijk in items in deze categorie (zonder subcat)
                for item in items:
                    if item["category_id"] == cat["id"]:
                        item_name = item["name"]["en"]
                        if filter_text_lower in item_name.lower():
                            return True
                return False

            if filter_text and not category_matches_filter():
                continue

            cat_iid = f"cat_{cat['id']}"
            self.tree.insert("", "end", iid=cat_iid, text=cat_name, open=False)

            # Voeg subcategorieën toe
            for subcat in cat.get("subcategories", []):
                subcat_name = subcat["name"]["en"]

                # Filter subcategorie ook
                if filter_text and filter_text_lower not in subcat_name.lower():
                    # Misschien nog items in deze subcat die wél matchen?
                    # Toon subcat dan toch:
                    matching_items = [
                        item for item in items
                        if item.get("subcategory_id") == subcat["id"]
                           and filter_text_lower in item["name"]["en"].lower()
                    ]
                    if not matching_items:
                        continue

                subcat_iid = f"sub_{subcat['id']}"
                self.tree.insert(cat_iid, "end", iid=subcat_iid, text=subcat_name, open=False)

                # Items in subcategorie
                for item in items:
                    if item["category_id"] == cat["id"] and item.get("subcategory_id") == subcat["id"]:
                        item_name = item["name"]["en"]
                        if filter_text and filter_text_lower not in item_name.lower():
                            continue
                        item_iid = f"item_{item['id']}"
                        self.tree.insert(subcat_iid, "end", iid=item_iid, text=item_name)

            # Items zonder subcategorie onder de categorie zelf
            for item in items:
                if item["category_id"] == cat["id"] and not item.get("subcategory_id"):
                    item_name = item["name"]["en"]
                    if filter_text and filter_text_lower not in item_name.lower():
                        continue
                    item_iid = f"item_{item['id']}"
                    self.tree.insert(cat_iid, "end", iid=item_iid, text=item_name)

    def on_search_change(self, *args):
        text = self.search_var.get()
        self.populate_tree(filter_text=text)

    def on_tree_press(self, event):
        item_id = self.tree.identify_row(event.y)
        if item_id:
            self._press_time = int(time.time() * 1000)
            self._press_item = item_id

    def on_tree_release(self, event):
        if not self._press_time or not self._press_item:
            return
        release_time = int(time.time() * 1000)
        duration = release_time - self._press_time

        item_id = self.tree.identify_row(event.y)
        if item_id != self._press_item:
            # Released on different item; ignore
            self._press_time = None
            self._press_item = None
            return

        cat_ids = {f"cat_{c['id']}" for c in categories}
        subcat_ids = {f"sub_{sc['id']}" for c in categories for sc in c.get("subcategories", [])}

        if item_id in cat_ids or item_id in subcat_ids:
            # category or subcategory clicked
            if duration >= self.long_press_threshold:
                # Long press: add category/subcategory name as an item to grocery list
                name = self.tree.item(item_id, "text")
                self.add_to_grocery_list(name)
                self.close_add_items_panel()
            else:
                # Tap: toggle expand/collapse
                is_open = self.tree.item(item_id, "open")
                self.tree.item(item_id, open=not is_open)
        else:
            # It's an item
            if duration < self.long_press_threshold:
                # Normal click: add item once
                name = self.tree.item(item_id, "text")
                self.add_to_grocery_list(name)
                self.close_add_items_panel()
            # Ignore long press on item

        self._press_time = None
        self._press_item = None

    def add_to_grocery_list(self, name):
        self.grocery_list[name] = self.grocery_list.get(name, 0) + 1
        self.update_grocery_display()

    def update_grocery_display(self):
        self.grocery_text.delete(1.0, tk.END)
        for name, qty in self.grocery_list.items():
            self.grocery_text.insert(tk.END, f"• {name} x{qty}\n")


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("400x500")
    app = GroceryApp(root)
    root.mainloop()
