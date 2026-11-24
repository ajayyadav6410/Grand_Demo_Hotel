
from app import get_db_connection


def add_demo_data():
    conn = get_db_connection()

    try:
        # 1. Add Rooms
        count = conn.execute(
            "SELECT COUNT(*) FROM rooms"
        ).fetchone()[0]

        if count == 0:
            conn.execute("""
                INSERT INTO rooms
                (room_type, description, price, capacity, facilities)
                VALUES
                ('Single Room', 'Comfortable room for one person', 1500, 1, 'WiFi, TV'),
                ('Double Room', 'Comfortable room for two people', 2500, 2, 'WiFi, TV, AC'),
                ('Deluxe Room', 'Spacious deluxe room', 4000, 3, 'WiFi, TV, AC, Mini Bar')
            """)

        # 2. Add Hotel Facilities
        count = conn.execute(
            "SELECT COUNT(*) FROM facilities"
        ).fetchone()[0]

        if count == 0:
            conn.execute("""
                INSERT INTO facilities (name, description)
                VALUES
                ('Free WiFi', 'Free internet for guests'),
                ('Swimming Pool', 'Swimming pool facility'),
                ('Parking', 'Free vehicle parking')
            """)

        # 3. Remove only unwanted food items
        conn.execute("""
            DELETE FROM restaurant_menu
            WHERE item_name IN (?, ?)
        """, ("Paneer Butter Masala", "Veg Biryani"))

        # 4. Restaurant Menu Items
        menu_items = [
            (
                "Veg Burger",
                "Delicious vegetarian burger",
                120,
                "Snacks",
                "https://images.unsplash.com/photo-1520072959219-c595dc870360?w=500"
            ),
            (
                "Pizza",
                "Freshly prepared pizza",
                250,
                "Fast Food",
                "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=500"
            ),
            (
                "Pasta",
                "Italian style pasta",
                180,
                "Italian",
                "https://images.unsplash.com/photo-1473093295043-cdd812d0e601?w=500"
            ),
            (
                "French Fries",
                "Crispy golden fries",
                100,
                "Snacks",
                "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=500"
            ),
            (
                "Sandwich",
                "Fresh vegetable sandwich",
                130,
                "Snacks",
                "https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=500"
            ),
            (
                "Cold Coffee",
                "Chilled creamy cold coffee",
                90,
                "Drinks",
                "https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=500"
            )
        ]

        # 5. Insert new items or update existing items
        for item in menu_items:
            existing = conn.execute(
                "SELECT id FROM restaurant_menu WHERE item_name = ?",
                (item[0],)
            ).fetchone()

            if existing:
                conn.execute("""
                    UPDATE restaurant_menu
                    SET description = ?,
                        price = ?,
                        category = ?,
                        image = ?
                    WHERE item_name = ?
                """, (
                    item[1],
                    item[2],
                    item[3],
                    item[4],
                    item[0]
                ))
            else:
                conn.execute("""
                    INSERT INTO restaurant_menu
                    (item_name, description, price, category, image)
                    VALUES (?, ?, ?, ?, ?)
                """, item)

        conn.commit()
        print("Demo Data Added Successfully!")

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    add_demo_data()
