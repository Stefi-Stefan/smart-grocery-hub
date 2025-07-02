import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "app" / "data"
LISTS_DIR = DATA_DIR / "lists"
USERS_FILE = DATA_DIR / "users.json"
SESSION_FILE = DATA_DIR / "session.json"
CATEGORIES_FILE = DATA_DIR / "categories.json"
ITEMS_FILE = DATA_DIR / "default_items.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)
LISTS_DIR.mkdir(parents=True, exist_ok=True)

def save_session(email: str) -> None:
    with SESSION_FILE.open("w", encoding="utf-8") as f:
        json.dump({"email": email}, f)

def load_session():
    if SESSION_FILE.exists():
        with SESSION_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("email")
    return None

def clear_session() -> None:
    if SESSION_FILE.exists():
        SESSION_FILE.unlink()