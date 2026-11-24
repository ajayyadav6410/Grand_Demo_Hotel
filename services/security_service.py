
from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(password):
    """Convert a plain password into a secure hash."""
    return generate_password_hash(password)


def verify_password(stored_hash, entered_password):
    """Check whether the entered password matches the stored hash."""
    if not stored_hash or not entered_password:
        return False

    return check_password_hash(stored_hash, entered_password)
