import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import traceback  # Add this import for printing stack traces
from app.managers.list_manager import ListManager
from app.utils.file_utils import clear_session

class GroceryApp(tk.Frame):
    def __init__(self, master, email, categories, items):
        super().__init__(master)
        self.master = master
        self.email = email
        self.categories = categories
        self.items = items
        self.list_manager = ListManager()

        self.current_list = None
        self.grocery_list = {}
        self.ensure_default_list_exists()
        self.list_names = self.get_accessible_lists()

        self.long_press_threshold = 500  # ms
        self._press_time = None
        self._press_item_id = None
        self._long_press_job = None
        self._press_start_time = None

        self.build_main_ui()
        if self.list_names:
            self.load_list(self.list_names[0])

    def ensure_default_list_exists(self):
        self.list_manager.ensure_default_list_exists(self.email)

    def build_main_ui(self):
        # List selection dropdown
        self.list_var = tk.StringVar(value=self.current_list)
        self.list_dropdown = ttk.Combobox(self, textvariable=self.list_var, values=self.list_names, state="readonly")
        self.list_dropdown.grid(row=0, column=0, columnspan=3, pady=5, sticky="ew")
        self.list_dropdown.bind("<<ComboboxSelected>>", self.on_list_change)

        # Label to show who has access
        self.access_label = tk.Label(self, text="")
        self.access_label.grid(row=1, column=0, columnspan=3, pady=5, sticky="w")

        # Grocery list display
        self.grocery_text = tk.Text(self, height=10, width=50)
        self.grocery_text.grid(row=2, column=0, columnspan=3, pady=10, sticky="nsew")

        # Buttons frame
        btn_frame = tk.Frame(self)
        btn_frame.grid(row=3, column=0, columnspan=3, pady=5, sticky="ew")

        self.add_button = tk.Button(btn_frame, text="+ Add items", command=self.open_add_items_panel)
        self.add_button.grid(row=0, column=0, padx=5)

        self.new_list_button = tk.Button(btn_frame, text="New List", command=self.create_new_list)
        self.new_list_button.grid(row=0, column=1, padx=5)

        self.delete_list_button = tk.Button(btn_frame, text="Delete Current List", command=self.delete_current_list)
        self.delete_list_button.grid(row=0, column=2, padx=5)

        self.share_list_button = tk.Button(btn_frame, text="Share List", command=self.share_list)
        self.share_list_button.grid(row=0, column=3, padx=5)

        self.logout_button = tk.Button(btn_frame, text="Logout", command=self.logout)
        self.logout_button.grid(row=0, column=4, padx=5)

        # Add Items panel (hidden initially)
        self.add_panel = tk.Frame(self)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.on_search_change)
        self.search_entry = tk.Entry(self.add_panel, textvariable=self.search_var, width=50)
        self.search_entry.grid(row=0, column=0, columnspan=3, pady=5, sticky="ew")

        # Scrollable tree view for categories and items
        self.tree_scroll = ttk.Scrollbar(self.add_panel, orient="vertical")
        self.tree_scroll.grid(row=1, column=3, sticky="ns")

        self.tree = ttk.Treeview(
            self.add_panel,
            columns=("Name",),
            displaycolumns=(),
            show="tree",
            yscrollcommand=self.tree_scroll.set
        )
        self.tree.grid(row=1, column=0, columnspan=3, sticky="nsew")
        self.tree_scroll.config(command=self.tree.yview)

        # Bindings for item interaction
        self.tree.bind("<ButtonPress-1>", self.on_tree_mouse_down)  # Start timing for long press
        self.tree.bind("<ButtonRelease-1>", self.on_tree_mouse_up)  # Handle short press or long press

        # Cancel button to return to the main screen
        self.cancel_button = tk.Button(self.add_panel, text="Cancel", command=self.close_add_items_panel)
        self.cancel_button.grid(row=2, column=0, columnspan=3, pady=5, sticky="ew")

        self.add_panel.grid(row=2, column=0, columnspan=3, pady=10, sticky="nsew")
        self.add_panel.grid_remove()  # Hide the panel initially

        # Configure grid weights for proper resizing
        self.add_panel.grid_rowconfigure(1, weight=1)
        self.add_panel.grid_columnconfigure(0, weight=1)

    def get_accessible_lists(self):
        return self.list_manager.get_accessible_lists(self.email)

    def on_list_change(self, event):
        self.save_list(self.current_list)
        selected = self.list_var.get()
        self.load_list(selected)

    def load_list(self, list_name):
        """Loads a list for viewing without acquiring an edit lock."""
        try:
            data = self.list_manager.load_list(self.email, list_name)  # Load list data
            if not data:
                self.grocery_list = {}
            else:
                self.grocery_list = data.get("items", {})

            self.current_list = list_name
            self.update_grocery_display()  # Update the grocery display
            self.list_var.set(list_name)
            self.update_access_label()  # Update the access label
        except Exception as e:
            print(f"Failed to load list: {e}")
            traceback.print_exc()  # Print the full stack trace to the terminal
            messagebox.showerror("Error", f"Failed to load list: {e}")

    def save_list(self, list_name):
        """Save the current grocery list to the file."""
        try:
            data = self.list_manager.load_list(self.email, list_name)  # Use the correct method
            if not data:
                data = {"items": {}}
            data["items"] = self.grocery_list
            self.list_manager.save_list(self.email, list_name, data)  # Use the correct method
        except Exception as e:
            print(f"Failed to save list: {e}")
            traceback.print_exc()  # Print the full stack trace to the terminal
            messagebox.showerror("Error", f"Failed to save list: {e}")

    def create_new_list(self):
        """Create a new grocery list."""
        new_name = simpledialog.askstring("New List", "Enter new list name:")
        if new_name:
            if new_name in self.list_names:
                messagebox.showerror("Error", f"A list named '{new_name}' already exists.")
                return
            try:
                self.list_manager.create_list(self.email, new_name)  # Pass the correct arguments
                self.list_names.append(new_name)
                self.list_dropdown.config(values=self.list_names)
                self.load_list(new_name)
            except Exception as e:
                print(f"Failed to create new list: {e}")
                traceback.print_exc()
                messagebox.showerror("Error", f"Failed to create new list: {e}")

    def delete_current_list(self):
        """Delete the currently selected grocery list."""
        if not self.current_list:
            messagebox.showerror("Error", "No list is currently selected.")
            return

        if self.current_list == "default":
            # Special case: Reset the default list instead of deleting it
            confirm = messagebox.askyesno("Confirm Reset", "Are you sure you want to reset the default list?")
            if confirm:
                try:
                    self.grocery_list = {}  # Clear all items in the default list
                    self.update_grocery_display()
                    self.save_list(self.current_list)  # Save the cleared list
                    messagebox.showinfo("Success", "The default list has been reset.")
                except Exception as e:
                    print(f"Failed to reset default list: {e}")
                    traceback.print_exc()
                    messagebox.showerror("Error", f"Failed to reset default list: {e}")
            return

        # For non-default lists, delete them
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the list '{self.current_list}'?")
        if confirm:
            try:
                list_file = self.list_manager._get_list_file(self.email, self.current_list)
                if list_file.exists():
                    list_file.unlink()  # Delete the list file
                self.list_names.remove(self.current_list)
                self.list_dropdown.config(values=self.list_names)
                self.current_list = None
                self.grocery_list = {}
                self.grocery_text.delete("1.0", tk.END)  # Clear the grocery list display
                messagebox.showinfo("Success", "List deleted successfully.")
                if self.list_names:
                    self.load_list(self.list_names[0])  # Load the first available list
                else:
                    # Ensure a default list exists if no lists remain
                    self.ensure_default_list_exists()
                    self.load_list("default")
            except Exception as e:
                print(f"Failed to delete list: {e}")
                traceback.print_exc()
                messagebox.showerror("Error", f"Failed to delete list: {e}")

    def share_list(self):
        """Share the current grocery list with another user."""
        if not self.current_list:
            messagebox.showerror("Error", "No list is currently selected.")
            return

        email_to_share = simpledialog.askstring("Share List", "Enter the email of the user to share the list with:")
        if email_to_share:
            try:
                list_data = self.list_manager.load_list(self.email, self.current_list)
                if email_to_share in list_data.get("shared_with", []):
                    messagebox.showinfo("Info", f"The list is already shared with {email_to_share}.")
                    return

                list_data.setdefault("shared_with", []).append(email_to_share)
                self.list_manager.save_list(self.email, self.current_list, list_data)
                messagebox.showinfo("Success", f"The list '{self.current_list}' has been shared with {email_to_share}.")
                self.update_access_label()  # Update the access label to reflect the new shared user
            except Exception as e:
                print(f"Failed to share list: {e}")
                traceback.print_exc()
                messagebox.showerror("Error", f"Failed to share list: {e}")

    def logout(self):
        """Log out the current user and return to the login screen."""
        from app.utils.file_utils import clear_session

        try:
            clear_session()  # Clear the session file
            self.master.show_login()  # Return to the login screen
        except Exception as e:
            print(f"Failed to log out: {e}")
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to log out: {e}")

    def open_add_items_panel(self):
        """Open the Add Items panel."""
        # Hide the main grocery list display and Add Items button
        self.add_button.grid_remove()
        self.grocery_text.grid_remove()

        # Show the Add Items panel
        self.add_panel.grid(row=2, column=0, columnspan=3, pady=10, sticky="nsew")
        self.search_entry.grid(row=0, column=0, columnspan=3, pady=5, sticky="ew")
        self.tree.grid(row=1, column=0, columnspan=3, sticky="nsew")
        self.add_panel.tkraise()  # Bring the Add Items panel to the front

        # Populate the tree view with categories and items
        self.populate_tree_with_items()

    def close_add_items_panel(self):
        """Close the Add Items panel and return to the main grocery list view."""
        # Hide the Add Items panel
        self.add_panel.grid_remove()
        self.search_entry.grid_remove()
        self.tree.grid_remove()

        # Show the main grocery list display and Add Items button
        self.grocery_text.grid(row=2, column=0, columnspan=3, pady=10, sticky="nsew")
        self.add_button.grid(row=3, column=0, padx=5)

    def populate_tree_with_items(self):
        """Populate the tree view with categories and their items."""
        self.tree.delete(*self.tree.get_children())  # Clear existing items

        # Pre-group items by category and subcategory for fast lookup
        items_by_cat_subcat = {}
        for item in self.items:
            cat_id = item.get("category_id")
            subcat_id = item.get("subcategory_id")  # Can be None
            key = (cat_id, subcat_id)
            items_by_cat_subcat.setdefault(key, []).append(item)

        def insert_category(parent_id, category):
            cat_id = category["id"]
            cat_name = category.get("name", {}).get("en", "Unnamed Category")
            # Insert category node with its unique ID
            category_node_id = self.tree.insert(parent_id, "end", text=cat_name, iid=f"cat-{cat_id}", open=False)

            # Insert items directly under this category (no subcategory)
            for item in items_by_cat_subcat.get((cat_id, None), []):
                item_id = item["id"]
                item_name = item.get("name", {}).get("en", "Unnamed Item")
                self.tree.insert(category_node_id, "end", text=item_name, iid=f"item-{item_id}")

            # Insert subcategories recursively
            for subcat in category.get("subcategories", []):
                subcat_id = subcat["id"]
                subcat_name = subcat.get("name", {}).get("en", "Unnamed Subcategory")
                # Insert subcategory node with its unique ID
                subcat_node_id = self.tree.insert(category_node_id, "end", text=subcat_name, iid=f"subcat-{subcat_id}", open=False)

                # Insert items under this subcategory
                for item in items_by_cat_subcat.get((cat_id, subcat_id), []):
                    item_id = item["id"]
                    item_name = item.get("name", {}).get("en", "Unnamed Item")
                    self.tree.insert(subcat_node_id, "end", text=item_name, iid=f"item-{item_id}")

        for category in self.categories:
            insert_category("", category)

    def on_search_change(self, *args):
        """Filter items in the tree view based on the search query."""
        query = self.search_var.get().lower()
        self.tree.delete(*self.tree.get_children())  # Clear existing items
        for category in self.categories:
            filtered_items = [item for item in category.get("items", []) if query in item["name"].lower()]
            if query in category["name"]["en"].lower() or filtered_items:
                parent = self.tree.insert("", "end", text=category["name"]["en"], open=True)
                for item in filtered_items:
                    self.tree.insert(parent, "end", text=item["name"])

    def on_tree_mouse_down(self, event):
        """Start timing to detect a long press on a tree item."""
        self._press_item_id = self.tree.identify_row(event.y)
        if self._press_item_id:
            self._press_start_time = self.after(self.long_press_threshold, self.mark_long_press)

    def on_tree_mouse_up(self, event):
        """Handle release: either it's a short press or a long press."""
        if self._press_start_time:
            self.after_cancel(self._press_start_time)
            self._press_start_time = None

            # Check if it was a long press
            if self._long_press_job:
                self.handle_long_press()
                self._long_press_job = None
            else:
                # Treat it as a short press
                self.handle_short_press(event)

    def mark_long_press(self):
        """Mark the current press as a long press."""
        self._long_press_job = True

    def handle_short_press(self, event):
        """Short press behavior: toggle or add item."""
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return

        if item_id.startswith("cat-") or item_id.startswith("subcat-"):  # It's a category or subcategory
            is_open = self.tree.item(item_id, "open")
            self.tree.item(item_id, open=not is_open)  # Toggle open/close state
        elif item_id.startswith("item-"):  # It's an item
            self.add_item_to_list_with_lock(item_id)
            self.close_add_items_panel()  # Return to the main screen after adding an item

    def handle_long_press(self):
        """If long press is triggered: add the name of the clicked item or category to the list."""
        if self._press_item_id:
            item_name = self.tree.item(self._press_item_id, "text")
            self.add_item_to_list_with_lock(item_name)
            self.close_add_items_panel()  # Return to the main screen after adding an item or category

        self._long_press_job = None  # Reset

    def add_item_to_list_with_lock(self, item_id_or_name):
        """Add an item to the grocery list with a lock to handle concurrency."""
        try:
            if not self.list_manager.acquire_edit_lock(self.email, self.current_list):
                messagebox.showwarning("List in use", f"The list '{self.current_list}' is currently being edited by another user.")
                return

            if item_id_or_name.startswith("item-"):  # If it's an item ID
                item_id = item_id_or_name.split("-", 1)[1]  # Extract the actual item ID
                item = next((item for item in self.items if item["id"] == item_id), None)
                if item:
                    item_name = item.get("name", {}).get("en", "Unnamed Item")
                    self.add_item_to_list(item_name)
            else:  # If it's a category or item name
                self.add_item_to_list(item_id_or_name)

            self.save_list(self.current_list)  # Save the list after adding the item
        except Exception as e:
            print(f"Failed to add item with lock: {e}")
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to add item: {e}")
        finally:
            self.list_manager.release_edit_lock()  # Always release the lock

    def add_item_to_list(self, item_name):
        """Add the selected item to the grocery list."""
        if item_name in self.grocery_list:
            self.grocery_list[item_name] += 1
        else:
            self.grocery_list[item_name] = 1
        self.update_grocery_display()

    def update_grocery_display(self):
        """Update the grocery list display with the current list items."""
        self.grocery_text.delete("1.0", tk.END)  # Clear the text area
        for item, quantity in self.grocery_list.items():
            self.grocery_text.insert(tk.END, f"{item}: {quantity}\n")

    def update_access_label(self):
        """Update the label showing who has access to the current list."""
        try:
            if self.current_list:
                data = self.list_manager.load_list(self.email, self.current_list)
                users = data.get("shared_with", [])
                users_str = ", ".join(users) if users else "No other users"
                self.access_label.config(text=f"Access: {users_str}")
        except Exception as e:
            print(f"Failed to update access label: {e}")
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to update access label: {e}")

    def clear_grocery_list(self):
        """Clear all items from the current grocery list."""
        if not self.current_list:
            messagebox.showerror("Error", "No list is currently selected.")
            return

        confirm = messagebox.askyesno("Confirm Clear", "Are you sure you want to clear all items from the list?")
        if confirm:
            try:
                self.grocery_list = {}
                self.update_grocery_display()
                self.save_list(self.current_list)
                messagebox.showinfo("Success", "The grocery list has been cleared.")
            except Exception as e:
                print(f"Failed to clear grocery list: {e}")
                traceback.print_exc()
                messagebox.showerror("Error", f"Failed to clear grocery list: {e}")

    def remove_item_from_list(self, item_name):
        """Remove a specific item from the grocery list."""
        if item_name in self.grocery_list:
            del self.grocery_list[item_name]
            self.update_grocery_display()
            self.save_list(self.current_list)
        else:
            messagebox.showerror("Error", f"Item '{item_name}' not found in the list.")

    def rename_list(self):
        """Rename the current grocery list."""
        if not self.current_list:
            messagebox.showerror("Error", "No list is currently selected.")
            return

        new_name = simpledialog.askstring("Rename List", "Enter the new name for the list:")
        if new_name:
            if new_name in self.list_names:
                messagebox.showerror("Error", f"A list named '{new_name}' already exists.")
                return
            try:
                list_data = self.list_manager.load_list(self.email, self.current_list)
                self.list_manager.create_list(self.email, new_name, list_data.get("shared_with", []))
                self.list_manager.save_list(self.email, new_name, list_data)
                self.list_manager._get_list_file(self.email, self.current_list).unlink()  # Delete old file
                self.list_names.remove(self.current_list)
                self.list_names.append(new_name)
                self.list_dropdown.config(values=self.list_names)
                self.current_list = new_name
                self.list_var.set(new_name)
                messagebox.showinfo("Success", f"The list has been renamed to '{new_name}'.")
            except Exception as e:
                print(f"Failed to rename list: {e}")
                traceback.print_exc()
                messagebox.showerror("Error", f"Failed to rename list: {e}")
