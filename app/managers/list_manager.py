from filelock import FileLock, Timeout
import json
import uuid
from pathlib import Path
from tkinter import messagebox
import traceback  # Add this import for printing stack traces

LISTS_DIR = Path("app/data/lists")


class ListManager:
    def __init__(self):
        LISTS_DIR.mkdir(parents=True, exist_ok=True)
        self.current_lock = None  # Track the current lock

    def _get_user_folder(self, user_email):
        """Returns the folder path for the user's lists."""
        user_folder = LISTS_DIR / user_email
        user_folder.mkdir(parents=True, exist_ok=True)
        return user_folder

    def _get_list_file(self, user_email, list_name):
        """Returns the file path for a specific list."""
        user_folder = self._get_user_folder(user_email)
        return user_folder / f"{list_name}.json"

    def _get_lock_file(self, list_file):
        """Returns the lock file path for a specific list."""
        return list_file.with_suffix(".lock")

    def acquire_edit_lock(self, user_email, list_name, timeout=5):
        """Acquire a file lock for a specific list."""
        list_file = self._get_list_file(user_email, list_name)
        lock_file = self._get_lock_file(list_file)
        lock = FileLock(lock_file)

        try:
            lock.acquire(timeout=timeout)
            self.current_lock = lock
            return True
        except Timeout:
            return False

    def release_edit_lock(self):
        """Release the current file lock."""
        if self.current_lock:
            try:
                self.current_lock.release()
            except Exception as e:
                print(f"Error releasing lock: {e}")
            finally:
                self.current_lock = None

    def is_locked(self, user_email, list_name):
        """Check if a list is currently locked."""
        list_file = self._get_list_file(user_email, list_name)
        lock_file = self._get_lock_file(list_file)
        return lock_file.exists()

    def list_exists(self, user_email, list_name):
        """Checks if a list already exists for the user."""
        list_file = self._get_list_file(user_email, list_name)
        return list_file.exists()

    def ensure_default_list_exists(self, user_email):
        """Ensures a default list exists for the user."""
        default_list_name = "default"
        default_list_file = self._get_list_file(user_email, default_list_name)

        if not default_list_file.exists():
            default_list_data = {
                "id": "default",
                "name": default_list_name,
                "owner": user_email,
                "shared_with": [],
                "items": {}
            }
            with default_list_file.open("w", encoding="utf-8") as f:
                json.dump(default_list_data, f, indent=4)
            print(f"Default list created for user: {user_email}")

    def get_owned_lists(self, user_email):
        """Returns a list of lists owned by the user."""
        user_folder = self._get_user_folder(user_email)
        return [file.stem for file in user_folder.glob("*.json")]

    def get_shared_lists(self, user_email):
        """Returns a list of lists shared with the user."""
        shared_lists = []
        for user_folder in LISTS_DIR.iterdir():
            if user_folder.is_dir():
                for list_file in user_folder.glob("*.json"):
                    with list_file.open("r", encoding="utf-8") as f:
                        list_data = json.load(f)
                        if user_email in list_data.get("shared_with", []):
                            shared_lists.append(list_data["name"])
        return shared_lists

    def get_accessible_lists(self, user_email):
        """Combine owned and shared lists, avoid duplicates, sorted."""
        owned = self.get_owned_lists(user_email)
        shared = self.get_shared_lists(user_email)
        return sorted(set(owned + shared))

    def create_list(self, user_email, list_name, shared_with=None):
        """Creates a new grocery list for the user."""
        if self.list_exists(user_email, list_name):
            raise ValueError(f"A list named '{list_name}' already exists for this user.")

        list_file = self._get_list_file(user_email, list_name)
        list_data = {
            "id": str(uuid.uuid4()),
            "name": list_name,
            "owner": user_email,
            "shared_with": shared_with or [],
            "items": {}
        }
        with list_file.open("w", encoding="utf-8") as f:
            json.dump(list_data, f, indent=4)
        return list_data

    def load_list(self, user_email, list_name):
        """Loads the list data for the given list name."""
        try:
            list_file = self._get_list_file(user_email, list_name)
            if not list_file.exists():
                raise FileNotFoundError(f"The list '{list_name}' does not exist.")

            with list_file.open("r", encoding="utf-8") as f:
                data = json.load(f)

            return data  # Return the loaded data to the caller
        except Exception as e:
            print(f"Failed to load list: {e}")
            traceback.print_exc()  # Print the full stack trace to the terminal
            messagebox.showerror("Error", f"Failed to load list: {e}")

    def save_list(self, user_email, list_name, list_data):
        """Saves the updated grocery list for the user."""
        try:
            list_file = self._get_list_file(user_email, list_name)
            with list_file.open("w", encoding="utf-8") as f:
                json.dump(list_data, f, indent=4)
            print(f"List '{list_name}' saved successfully.")
        except Exception as e:
            print(f"Error saving list '{list_name}': {e}")
            raise

    def add_item(self, user_email, list_name, item_name, quantity):
        """Adds an item to the specified list."""
        try:
            print(f"Adding item: {item_name}, Quantity: {quantity}, User: {user_email}, List: {list_name}")
            list_data = self.load_list(user_email, list_name)
            list_data["items"][item_name] = quantity
            self.save_list(user_email, list_name, list_data)
            print(f"Item '{item_name}' successfully added.")
        except Exception as e:
            print(f"Failed to add item: {e}")
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to add item: {e}")

    def remove_item(self, user_email, list_name, item_name):
        """Removes an item from the grocery list."""
        list_data = self.load_list(user_email, list_name)
        if item_name in list_data["items"]:
            del list_data["items"][item_name]
            self.save_list(user_email, list_name, list_data)
