import tkinter as tk
from app.frames.grocery_frame import GroceryApp
from app.frames.login_frame import LoginFrame
from app.utils.file_utils import CATEGORIES_FILE, ITEMS_FILE, SESSION_FILE
import json

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Grocery App")
        self.geometry("800x600")
        self.categories = []
        self.items = []
        self.load_data()
        self.check_session()

    def check_session(self):
        """Check if a session exists and log in the user automatically if valid."""
        try:
            if SESSION_FILE.exists():
                with SESSION_FILE.open("r", encoding="utf-8") as f:
                    session_data = json.load(f)
                    email = session_data.get("email")
                    if email:
                        self.on_login_success(email)
                        return
        except Exception as e:
            print(f"Error reading session file: {e}")

        # If no valid session, show login screen
        self.show_login()

    def load_data(self):
        """Load categories and items data from their respective files."""
        try:
            with CATEGORIES_FILE.open("r", encoding="utf-8") as f:
                self.categories = json.load(f)
            with ITEMS_FILE.open("r", encoding="utf-8") as f:
                self.items = json.load(f)
        except Exception as e:
            print(f"Error loading data files: {e}")
            self.categories = []
            self.items = []

    def show_login(self):
        """Display the login screen."""
        from app.managers.user_manager import UserManager
        from app.utils.file_utils import save_session

        for widget in self.winfo_children():
            widget.destroy()

        user_manager = UserManager()  # Initialize the UserManager
        login_frame = LoginFrame(self, self.on_login_success, user_manager, save_session)
        login_frame.pack(expand=True, fill="both")

    def on_login_success(self, email):
        """Handle successful login and transition to the GroceryApp frame."""
        for widget in self.winfo_children():
            widget.destroy()
        grocery_frame = GroceryApp(self, email, self.categories, self.items)
        grocery_frame.pack(expand=True, fill="both")

if __name__ == "__main__":
    app = App()
    app.mainloop()