import json
from pathlib import Path
import bcrypt

USERS_FILE = Path("app/data/users.json")

class UserManager:
    def __init__(self):
        self.users = self.load_users()

    def load_users(self):
        if not USERS_FILE.exists():
            USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
            with USERS_FILE.open("w", encoding="utf-8") as f:
                json.dump({}, f, indent=4)
        with USERS_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)

    def save_users(self):
        try:
            with USERS_FILE.open("w", encoding="utf-8") as f:
                json.dump(self.users, f, indent=4)
        except Exception as e:
            print(f"Error saving users: {e}")

    def register_user(self, email, password):
        if email in self.users:
            raise ValueError("User already exists.")
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        self.users[email] = hashed_password.decode("utf-8")
        self.save_users()

    def authenticate_user(self, email, password):
        if email not in self.users:
            return False
        hashed_password = self.users[email].encode("utf-8")
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password)

    def verify_user_by_email(self, email, password):
        if email not in self.users:
            return False
        return bcrypt.checkpw(password.encode("utf-8"), self.users[email].encode("utf-8"))