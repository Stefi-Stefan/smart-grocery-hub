import sys
from pathlib import Path
import json
import tkinter as tk
from app.app import App
from app.utils.file_utils import CATEGORIES_FILE, ITEMS_FILE

# Ensure the app directory is in the Python path
sys.path.append(str(Path(__file__).resolve().parent / "app"))

if __name__ == "__main__":
    try:
        with CATEGORIES_FILE.open("r", encoding="utf-8") as f:
            categories = json.load(f)
        with ITEMS_FILE.open("r", encoding="utf-8") as f:
            items = json.load(f)
    except Exception as e:
        print(f"Error loading data files: {e}")
        categories = []
        items = []

    app = App()
    app.mainloop()