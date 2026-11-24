
from database import get_db_connection


def create_tables():
    conn = get_db_connection()

    try:
        # 1. Users Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. Admin Accounts Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)

        # 3. Rooms Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_type TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                capacity INTEGER NOT NULL,
                facilities TEXT,
                available INTEGER DEFAULT 1
            )
        """)

        # 4. Customer Bookings Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                room_id INTEGER,
                check_in DATE NOT NULL,
                check_out DATE NOT NULL,
                guests INTEGER NOT NULL,
                total_price REAL NOT NULL,
                payment_status TEXT DEFAULT 'Pending',
                booking_status TEXT DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (room_id) REFERENCES rooms(id)
            )
        """)

        # 5. Hotel Facilities Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS facilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT
            )
        """)

        # 6. Restaurant Menu Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS restaurant_menu (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                category TEXT
            )
        """)

        # Add image column if it does not already exist
        columns = conn.execute(
            "PRAGMA table_info(restaurant_menu)"
        ).fetchall()

        column_names = [column[1] for column in columns]

        if "image" not in column_names:
            conn.execute("""
                ALTER TABLE restaurant_menu
                ADD COLUMN image TEXT
            """)

        # 7. Food Order Batches Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS food_order_batches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                total_amount REAL NOT NULL,
                payment_method TEXT DEFAULT 'Not Selected',
                payment_status TEXT DEFAULT 'Pending',
                order_status TEXT DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 8. Food Order Items Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS food_order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id INTEGER NOT NULL,
                item_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                item_total REAL NOT NULL
            )
        """)

        conn.commit()
        print("All 8 database tables are ready!")

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    create_tables()
