from app import get_db_connection

def add_demo_data():
    conn = get_db_connection()

    # Add Rooms
    count = conn.execute("SELECT COUNT(*) FROM rooms").fetchone()[0]

    if count == 0:
        conn.execute("""
            INSERT INTO rooms
            (room_type, description, price, capacity, facilities)
            VALUES
            ('Single Room', 'Comfortable room for one person', 1500, 1, 'WiFi, TV'),
            ('Double Room', 'Comfortable room for two people', 2500, 2, 'WiFi, TV, AC'),
            ('Deluxe Room', 'Spacious deluxe room', 4000, 3, 'WiFi, TV, AC, Mini Bar')
        """)

    # Add Hotel Facilities
    count = conn.execute("SELECT COUNT(*) FROM facilities").fetchone()[0]

    if count == 0:
        conn.execute("""
            INSERT INTO facilities (name, description)
            VALUES
            ('Free WiFi', 'Free internet for guests'),
            ('Swimming Pool', 'Swimming pool facility'),
            ('Parking', 'Free vehicle parking')
        """)


        conn.execute("""
    DELETE FROM restaurant_menu
    WHERE item_name IN (
        'Paneer Butter Masala',
        'Veg Biryani',
        'Cold Coffee'
    )
    """)

    conn.commit()   

    conn.commit()
    conn.close()
    print("Demo Data Added Successfully!")

if __name__ == "__main__":
    add_demo_data()