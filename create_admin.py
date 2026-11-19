from getpass import getpass
from werkzeug.security import generate_password_hash
from app import get_db_connection

username = input("Enter Admin Username: ").strip()
password = getpass("Enter Admin Password: ")

if not username or not password:
    print("Username and password cannot be empty.")
else:
    conn = get_db_connection()

    try:
        existing = conn.execute(
            "SELECT id FROM admins WHERE username = ?",
            (username,)
        ).fetchone()

        if existing:
            print("This admin username already exists.")
        else:
            hashed_password = generate_password_hash(password)

            conn.execute("""
                INSERT INTO admins (username, password)
                VALUES (?, ?)
            """, (username, hashed_password))

            conn.commit()
            print("Admin account created successfully!")

    finally:
        conn.close()