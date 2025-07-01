import bcrypt

def hash_password(password):
    """Hashes a password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def check_password(password, hashed_password):
    """Verifies a password against a hashed password."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))