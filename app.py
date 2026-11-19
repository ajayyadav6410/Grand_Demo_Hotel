from datetime import date 
from flask import Flask, render_template_string, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
import turso_serverless

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-this-secret-key")

def get_db_connection():
    return turso_serverless.connect(
        os.getenv("TURSO_DATABASE_URL"),
        auth_token=os.getenv("TURSO_AUTH_TOKEN")
    )

@app.route('/')
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Grand Demo Hotel - Home</title>
        <style>
            body {
                font-family: Arial;
                background: #f2f4f7;
                margin: 0;
                color: #243447;
            }

            header {
                background: #243447;
                color: white;
                text-align: center;
                padding: 20px;
            }

            nav {
                background: white;
                padding: 15px;
                text-align: center;
            }

            nav a {
                color: #16834a;
                text-decoration: none;
                margin: 0 12px;
                font-weight: bold;
            }

            .welcome-box {
                background: white;
                max-width: 650px;
                margin: 50px auto;
                padding: 40px 25px;
                text-align: center;
                border-radius: 10px;
            }

            .welcome-box h2 {
                color: #243447;
            }

            .welcome-box p {
                color: #555;
                line-height: 1.6;
            }

            .button {
                display: inline-block;
                background: #16834a;
                color: white;
                padding: 12px 22px;
                margin: 10px 5px;
                border-radius: 5px;
                text-decoration: none;
            }

            footer {
                text-align: center;
                padding: 20px;
                color: #666;
            }
        </style>
    </head>

    <body>
        <header>
            <h1>Grand Demo Hotel</h1>
            <p>Your Comfort, Our Priority</p>
        </header>

        <nav>
            <a href="/">Home</a>
            <a href="/register">Register</a>
            <a href="/login">Login</a>
        </nav>

        <div class="welcome-box">
            <h2>Welcome to Grand Demo Hotel!</h2>

            <p>
                Enjoy a comfortable and relaxing stay with us.
                Explore our rooms and hotel facilities.
                We are happy to serve you.
            </p>

            
            <a class="button" href="/register">Create Account</a>
            <a class="button" href="/login">User Login</a>
        </div>

        <footer>
            <p>© 2026 Grand Demo Hotel | All Rights Reserved</p>
        </footer>
    </body>
    </html>
    """)



@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ""

    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']

        if not name or not email or not password:
            message = "Please fill all fields."
        else:
            conn = get_db_connection()
            try:
                hashed_password = generate_password_hash(password)
                conn.execute("""
                    INSERT INTO users (name, email, password)
                    VALUES (?, ?, ?)
                """, (name, email, hashed_password))
                conn.commit()
                message = "Registration Successful!"
            except Exception:
                message = "This email is already registered. Try another."
            finally:
                conn.close()


    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>Grand Demo Hotel - Registration</title>
    <style>
        body {
            font-family: Arial;
            background: #f2f4f7;
            margin: 0;
        }

        header {
            background: #243447;
            color: white;
            text-align: center;
            padding: 20px;
        }

        .register-box {
            background: white;
            width: 320px;
            margin: 40px auto;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
        }

        input {
            width: 90%;
            padding: 12px;
            margin: 10px 0;
            border: 1px solid #ccc;
            border-radius: 5px;
        }

        button {
            background: #16834a;
            color: white;
            padding: 12px;
            width: 100%;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }

        a {
            color: #16834a;
            text-decoration: none;
        }
    </style>
</head>

<body>
    <header>
        <h1>Grand Demo Hotel</h1>
        <h2>User Registration</h2>
    </header>

    <div class="register-box">
        <h2>Create Account</h2>

        <p style="color:green;">{{ message }}</p>

        <form method="POST">
            <input type="text" name="name"
                   placeholder="Enter Name" required>

            <input type="email" name="email"
                   placeholder="Enter Email" required>

            <input type="password" name="password"
                   placeholder="Enter Password" required>

            <button type="submit">Register</button>
        </form>

        <p>Already Registered? <a href="/login">Login Here</a></p>
        <a href="/">Back to Home</a>
    </div>
</body>
</html>
""", message=message)



@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ""

    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']

        conn = get_db_connection()

        try:
            user = conn.execute("""
                SELECT password, id, name, email
                FROM users
                WHERE LOWER(email) = ?
            """, (email,)).fetchone()

            if user:
                stored_password = user[0]

                if check_password_hash(stored_password, password):
                    session['user_id'] = user[1]
                    session['user_name'] = user[2]
                    return redirect('/dashboard')

            message = "Invalid email or password."

        finally:
            conn.close()

    return render_template_string("""

    <!DOCTYPE html>
<html>
<head>
    <title>Grand Demo Hotel - Login</title>
    <style>
        body {
            font-family: Arial;
            background: #f2f4f7;
            margin: 0;
        }

        header {
            background: #243447;
            color: white;
            text-align: center;
            padding: 20px;
        }

        .login-box {
            background: white;
            width: 320px;
            margin: 50px auto;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
        }

        input {
            width: 90%;
            padding: 12px;
            margin: 10px 0;
            border: 1px solid #ccc;
            border-radius: 5px;
        }

        button {
            background: #16834a;
            color: white;
            padding: 12px;
            width: 100%;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }

        a {
            color: #16834a;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <header>
        <h1>Grand Demo Hotel</h1>
        <h2>User Login</h2>
    </header>

    <div class="login-box">
        <h2>Welcome Back!</h2>
        <p style="color:red;">{{ message }}</p>

        <form method="POST">
            <input type="email" name="email"
                   placeholder="Enter Email" required>

            <input type="password" name="password"
                   placeholder="Enter Password" required>

            <button type="submit">Login</button>
        </form>

        <p>New User? <a href="/register">Register Here</a></p>
        <a href="/">Back to Home</a>
    </div>
</body>
</html>

    """, message=message)
    
      
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Grand Demo Hotel Dashboard</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f2f4f7;
                margin: 0;
            }

            .header {
                background: #243447;
                color: white;
                padding: 20px;
                text-align: center;
            }

            .container {
                max-width: 850px;
                margin: 40px auto;
                padding: 25px;
                background: white;
                border-radius: 8px;
                text-align: center;
            }

            .menu {
                display: flex;
                justify-content: center;
                flex-wrap: wrap;
                gap: 15px;
                margin-top: 30px;
            }

            .menu a {
                background: #243447;
                color: white;
                padding: 15px 25px;
                text-decoration: none;
                border-radius: 5px;
            }

            .menu a:hover {
                background: #405a75;
            }

            .logout {
                display: inline-block;
                margin-top: 30px;
                color: #c0392b;
                text-decoration: none;
            }
        </style>
    </head>

    <body>
        <div class="header">
            <h1>Grand Demo Hotel</h1>
            <p>User Dashboard</p>
        </div>

        <div class="container">
            <h2>Welcome, {{ name }}!</h2>
            <p>You have successfully logged in.</p>

            <div class="menu">
                <a href="/rooms">View Rooms</a>
                <a href="/facilities">Hotel Facilities</a>
                <a href="/menu">Restaurant Menu</a>
                <a href="/my-bookings">My Bookings</a>
                <a href="/my-food-orders">My Food Orders</a>
                
            </div>

            <a class="logout" href="/logout">Logout</a>
        </div>
    </body>
    </html>
    """, name=session['user_name'])

@app.route('/rooms')
def rooms():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()

    try:
        rooms_data = conn.execute("""
            SELECT * FROM rooms
            WHERE available = 1
        """).fetchall()
    finally:
        conn.close()

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Grand Demo Hotel - Available Rooms</title>

        <style>
            body {
                font-family: Arial;
                background: #f2f4f7;
                margin: 0;
                color: #243447;
            }

            header {
                background: #243447;
                color: white;
                text-align: center;
                padding: 20px;
            }

            .container {
                max-width: 1000px;
                margin: 30px auto;
                padding: 15px;
            }

            .room-card {
                background: white;
                padding: 22px;
                margin-bottom: 20px;
                border-radius: 10px;
                border-left: 5px solid #16834a;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            }

            .room-card h3 {
                color: #243447;
                margin-top: 0;
            }

            .price {
                color: #16834a;
                font-size: 20px;
                font-weight: bold;
            }

            .room-detail {
                color: #555;
                line-height: 1.7;
            }

            .back-button {
                display: inline-block;
                background: #16834a;
                color: white;
                padding: 12px 20px;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 15px;
            }

            .no-room {
                background: white;
                padding: 25px;
                text-align: center;
                border-radius: 10px;
            }
        </style>
    </head>

    <body>

        <header>
            <h1>Grand Demo Hotel</h1>
            <h2>Available Rooms</h2>
            <p>Choose a room for your comfortable stay</p>
        </header>

        <div class="container">

            {% for room in rooms_data %}

                <div class="room-card">
                {% if 'single' in room[1]|lower %}
    <img src="https://images.unsplash.com/photo-1611892440504-42a792e24d32?w=600"
         alt="Single Room"
         style="width:100%; height:200px; object-fit:cover; border-radius:8px;">

{% elif 'double' in room[1]|lower %}
    <img src="https://images.unsplash.com/photo-1616594039964-ae9021a400a0?w=600"
         alt="Double Room"
         style="width:100%; height:200px; object-fit:cover; border-radius:8px;">

{% elif 'deluxe' in room[1]|lower %}
    <img src="https://images.unsplash.com/photo-1611892440504-42a792e24d32?w=600"
         alt="Deluxe Room"
         style="width:100%; height:200px; object-fit:cover; border-radius:8px;">
{% endif %}


                    <h3>{{ room[1] }}</h3>

                    <p class="room-detail">
                        {{ room[2] }}
                    </p>

                    <p class="price">
                        ₹{{ room[3] }} / Night
                    </p>

                    <p class="room-detail">
                        <b>Capacity:</b> {{ room[4] }} Guests
                    </p>

                    <p class="room-detail">
                        <b>Facilities:</b> {{ room[5] }}
                    </p>
                    <a class="back-button" href="/book/{{ room[0] }}">
    Book Now
</a>

                </div>

            {% else %}

                <div class="no-room">
                    <h3>No Rooms Available</h3>
                    <p>Please check again later.</p>
                </div>

            {% endfor %}

            <a class="back-button" href="/dashboard">
                Back to Dashboard
            </a>

        </div>

    </body>
    </html>
    """, rooms_data=rooms_data)


@app.route('/facilities')
def facilities():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()

    try:
        facilities_data = conn.execute("""
            SELECT * FROM facilities
        """).fetchall()
    finally:
        conn.close()

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Hotel Facilities - Grand Demo Hotel</title>
        <style>
            body {
                font-family: Arial;
                background: #f2f4f7;
                margin: 0;
                color: #243447;
            }

            header {
                background: #243447;
                color: white;
                text-align: center;
                padding: 20px;
            }

            .container {
                max-width: 900px;
                margin: 30px auto;
                padding: 15px;
            }

            .facility-card {
                background: white;
                padding: 22px;
                margin-bottom: 18px;
                border-radius: 10px;
                border-left: 5px solid #16834a;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            }

            .facility-card h3 {
                margin-top: 0;
                color: #243447;
            }

            .facility-card p {
                color: #555;
                line-height: 1.6;
            }

            .back-button {
                display: inline-block;
                background: #16834a;
                color: white;
                padding: 12px 20px;
                border-radius: 5px;
                text-decoration: none;
            }

            .empty {
                background: white;
                padding: 25px;
                text-align: center;
                border-radius: 10px;
            }
        </style>
    </head>

    <body>
        <header>
            <h1>Grand Demo Hotel</h1>
            <h2>Hotel Facilities</h2>
            <p>Enjoy our hotel services and facilities</p>
        </header>

        <div class="container">
            {% for facility in facilities_data %}
                <div class="facility-card">
                    <h3>{{ facility[1] }}</h3>
                    <p>{{ facility[2] }}</p>
                </div>
            {% else %}
                <div class="empty">
                    <h3>No Facilities Available</h3>
                </div>
            {% endfor %}

            <a class="back-button" href="/dashboard">
                Back to Dashboard
            </a>
        </div>
    </body>
    </html>
    """, facilities_data=facilities_data)





@app.route('/book/<int:room_id>', methods=['GET', 'POST'])
def book_room(room_id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()

    try:
        room = conn.execute("""
            SELECT * FROM rooms
            WHERE id = ? AND available = 1
        """, (room_id,)).fetchone()

        if not room:
            return "Room not found or unavailable."

        message = ""

        if request.method == 'POST':
            check_in = request.form.get('check_in')
            check_out = request.form.get('check_out')
            guests = request.form.get('guests')

            try:
                check_in_date = date.fromisoformat(check_in)
                check_out_date = date.fromisoformat(check_out)
                guests = int(guests)

                if check_in_date < date.today():
                    message = "Check-in date cannot be in the past."
                elif check_out_date <= check_in_date:
                    message = "Check-out must be after check-in."
                elif guests < 1 or guests > room[4]:
                    message = "Please enter guests within room capacity."
                else:
                    existing = conn.execute("""
                        SELECT id FROM bookings
                        WHERE room_id = ?
                        AND booking_status != 'Cancelled'
                        AND check_in < ?
                        AND check_out > ?
                    """, (room_id, check_out, check_in)).fetchone()

                    if existing:
                        message = "Room is already booked for these dates."
                    else:
                        nights = (check_out_date - check_in_date).days
                        total_price = nights * room[3]

                        cursor = conn.execute("""
                            INSERT INTO bookings
                            (user_id, room_id, check_in, check_out,
                             guests, total_price)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            session['user_id'],
                            room_id,
                            check_in,
                            check_out,
                            guests,
                            total_price
                        ))

                        conn.commit()
                        booking_id = cursor.lastrowid

                        return redirect('/payment/' + str(booking_id))

            except (ValueError, TypeError):
                message = "Please enter valid booking details."

        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Book Room - Grand Demo Hotel</title>
            <style>
                body {
                    font-family: Arial;
                    background: #f2f4f7;
                    margin: 0;
                    color: #243447;
                }
                header {
                    background: #243447;
                    color: white;
                    text-align: center;
                    padding: 20px;
                }
                .booking-box {
                    background: white;
                    max-width: 420px;
                    margin: 35px auto;
                    padding: 25px;
                    border-radius: 10px;
                }
                input {
                    width: 95%;
                    padding: 11px;
                    margin: 8px 0 16px;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    box-sizing: border-box;
                }
                button {
                    background: #16834a;
                    color: white;
                    padding: 12px;
                    width: 100%;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                }
                .price {
                    color: #16834a;
                    font-weight: bold;
                }
                a {
                    color: #16834a;
                    text-decoration: none;
                }
            </style>
        </head>
        <body>
            <header>
                <h1>Grand Demo Hotel</h1>
                <h2>Room Booking</h2>
            </header>

            <div class="booking-box">
                <h2>{{ room[1] }}</h2>
                <p>{{ room[2] }}</p>
                <p class="price">₹{{ room[3] }} / Night</p>
                <p>Capacity: {{ room[4] }} Guests</p>

                <p style="color:red;">{{ message }}</p>

                <form method="POST">
                    <label>Check-in Date</label>
                    <input type="date" name="check_in" required>

                    <label>Check-out Date</label>
                    <input type="date" name="check_out" required>

                    <label>Number of Guests</label>
                    <input type="number" name="guests"
                           min="1" max="{{ room[4] }}" required>

                    <button type="submit">Continue to Payment</button>
                </form>

                <p><a href="/rooms">Back to Rooms</a></p>
            </div>
        </body>
        </html>
        """, room=room, message=message)

    finally:
        conn.close()

@app.route('/payment/<int:booking_id>', methods=['GET', 'POST'])
def payment(booking_id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()

    try:
        booking = conn.execute("""
            SELECT bookings.id, bookings.total_price,
                   bookings.payment_status, rooms.room_type
            FROM bookings
            JOIN rooms ON bookings.room_id = rooms.id
            WHERE bookings.id = ? AND bookings.user_id = ?
        """, (booking_id, session['user_id'])).fetchone()

        if not booking:
            return "Booking not found."

        if request.method == 'POST':
            conn.execute("""
                UPDATE bookings
                SET payment_status = 'Paid',
                    booking_status = 'Confirmed'
                WHERE id = ? AND user_id = ?
            """, (booking_id, session['user_id']))

            conn.commit()
            return redirect('/my-bookings')

        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Demo Payment</title>
            <style>
                body {
                    font-family: Arial;
                    background: #f2f4f7;
                    margin: 0;
                    color: #243447;
                }
                header {
                    background: #243447;
                    color: white;
                    text-align: center;
                    padding: 20px;
                }
                .payment-box {
                    background: white;
                    max-width: 400px;
                    margin: 50px auto;
                    padding: 25px;
                    border-radius: 10px;
                    text-align: center;
                }
                button {
                    background: #16834a;
                    color: white;
                    padding: 12px;
                    width: 100%;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                }
            </style>
        </head>
        <body>
            <header>
                <h1>Grand Demo Hotel</h1>
                <h2>Demo Payment</h2>
            </header>

            <div class="payment-box">
                <h3>Booking #{{ booking[0] }}</h3>
                <p>Room: {{ booking[3] }}</p>
                <h2>Amount: ₹{{ booking[1] }}</h2>
                <p>Payment Status: {{ booking[2] }}</p>
                <p>This is a demo payment. No real money will be charged.</p>

                {% if booking[2] != 'Paid' %}
                <form method="POST">
                    <button type="submit">Confirm Demo Payment</button>
                </form>
                {% else %}
                <p>Payment already completed.</p>
                {% endif %}
            </div>
        </body>
        </html>
        """, booking=booking)

    finally:
        conn.close()


@app.route('/my-bookings')
def my_bookings():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()

    try:
        bookings = conn.execute("""
            SELECT bookings.id, rooms.room_type,
                   bookings.check_in, bookings.check_out,
                   bookings.guests, bookings.total_price,
                   bookings.payment_status, bookings.booking_status
            FROM bookings
            JOIN rooms ON bookings.room_id = rooms.id
            WHERE bookings.user_id = ?
            ORDER BY bookings.id DESC
        """, (session['user_id'],)).fetchall()
    finally:
        conn.close()

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>My Bookings - Grand Demo Hotel</title>
        <style>
            body {
                font-family: Arial;
                background: #f2f4f7;
                margin: 0;
                color: #243447;
            }
            header {
                background: #243447;
                color: white;
                text-align: center;
                padding: 20px;
            }
            .container {
                max-width: 850px;
                margin: 30px auto;
                padding: 15px;
            }
            .booking-card {
                background: white;
                padding: 22px;
                margin-bottom: 20px;
                border-radius: 10px;
                border-left: 5px solid #16834a;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            }
            .booking-card h3 {
                margin-top: 0;
            }
            .booking-card p {
                line-height: 1.5;
                color: #555;
            }
            .amount {
                color: #16834a;
                font-size: 20px;
                font-weight: bold;
            }
            .back-button {
                display: inline-block;
                background: #16834a;
                color: white;
                padding: 12px 20px;
                border-radius: 5px;
                text-decoration: none;
            }
            .empty {
                background: white;
                padding: 25px;
                text-align: center;
                border-radius: 10px;
            }
        </style>
    </head>
    <body>
        <header>
            <h1>Grand Demo Hotel</h1>
            <h2>My Bookings</h2>
        </header>

        <div class="container">
            {% for booking in bookings %}
            <div class="booking-card">
                <h3>Booking #{{ booking[0] }}</h3>
                <h3>{{ booking[1] }}</h3>

                <p><b>Check-in:</b> {{ booking[2] }}</p>
                <p><b>Check-out:</b> {{ booking[3] }}</p>
                <p><b>Guests:</b> {{ booking[4] }}</p>

                <p class="amount">Total: ₹{{ booking[5] }}</p>

                <p><b>Payment:</b> {{ booking[6] }}</p>
                <p><b>Booking Status:</b> {{ booking[7] }}</p>
            </div>
            {% else %}
            <div class="empty">
                <h3>No Bookings Yet</h3>
                <p>Explore our rooms and book your stay.</p>
                <a href="/rooms">View Rooms</a>
            </div>
            {% endfor %}

            <a class="back-button" href="/dashboard">
                Back to Dashboard
            </a>
        </div>
    </body>
    </html>
    """, bookings=bookings)


# ================= RESTAURANT SECTION =================

def setup_restaurant_tables():
    conn = get_db_connection()

    try:
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

        conn.execute("""
            CREATE TABLE IF NOT EXISTS restaurant_menu (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                category TEXT,
                image TEXT
            )
        """)

        columns = conn.execute(
            "PRAGMA table_info(restaurant_menu)"
        ).fetchall()

        if not any(col[1] == "image" for col in columns):
            conn.execute(
                "ALTER TABLE restaurant_menu ADD COLUMN image TEXT"
            )

        conn.commit()

    finally:
        conn.close()



def add_restaurant_menu_data():
    conn = get_db_connection()

    items = [
        ("Veg Burger", "Fresh vegetable burger", 120, "Snacks",
         "https://images.unsplash.com/photo-1520072959219-c595dc870360?w=500"),
        ("Pizza", "Delicious pizza", 250, "Fast Food",
         "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=500"),
        ("Pasta", "Italian pasta", 180, "Italian",
         "https://images.unsplash.com/photo-1473093295043-cdd812d0e601?w=500"),
        ("French Fries", "Crispy French fries", 100, "Snacks",
         "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=500"),
        ("Sandwich", "Fresh sandwich", 130, "Snacks",
         "https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=500"),
        ("Cold Coffee", "Chilled cold coffee", 90, "Drinks",
         "https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=500")
    ]

    try:
        conn.execute("""
            DELETE FROM restaurant_menu
            WHERE item_name IN (
                'Paneer Butter Masala',
                'Veg Biryani'
            )
        """)
        conn.execute("""
            UPDATE restaurant_menu
            SET image = ?
            WHERE item_name = 'Cold Coffee'
        """, (
            "https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=500",
        ))


        for item in items:
            existing = conn.execute(
                "SELECT id FROM restaurant_menu WHERE item_name=?",
                (item[0],)
            ).fetchone()

            if not existing:
                conn.execute("""
                    INSERT INTO restaurant_menu
                    (item_name, description, price, category, image)
                    VALUES (?, ?, ?, ?, ?)
                """, item)

        conn.commit()
    finally:
        conn.close()


RESTAURANT_MENU = [
    {
        "id": 1,
        "name": "Veg Burger",
        "price": 120,
        "category": "Snacks",
        "image": "https://images.unsplash.com/photo-1520072959219-c595dc870360?w=500"
    },
    {
        "id": 2,
        "name": "Pizza",
        "price": 250,
        "category": "Fast Food",
        "image": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=500"
    },
    {
        "id": 3,
        "name": "Pasta",
        "price": 180,
        "category": "Italian",
        "image": "https://images.unsplash.com/photo-1473093295043-cdd812d0e601?w=500"
    },
    {
        "id": 4,
        "name": "French Fries",
        "price": 100,
        "category": "Snacks",
        "image": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=500"
    },
    {
        "id": 5,
        "name": "Sandwich",
        "price": 130,
        "category": "Snacks",
        "image": "https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=500"
    },
    {
        "id": 6,
        "name": "Cold Coffee",
        "price": 100,
        "category": "Drinks",
        "image": "https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=500"
    }
]


@app.route('/menu', methods=['GET', 'POST'])
def menu():

    if 'user_id' not in session:
        return redirect('/login')

    setup_restaurant_tables()
    add_restaurant_menu_data()

    conn = get_db_connection()

    try:
        rows = conn.execute("""
            SELECT id, item_name, price, category, image
            FROM restaurant_menu
            ORDER BY id
        """).fetchall()
    finally:
        conn.close()

    menu_items = [
        {
            "id": row[0],
            "name": row[1],
            "price": row[2],
            "category": row[3],
            "image": row[4] or ""
        }
        for row in rows
    ]

    message = ""

    if request.method == 'POST':

        selected_items = []
        total_amount = 0

        for item in menu_items:

            try:
                quantity = int(request.form.get(
                    'quantity_' + str(item['id']), 0
                ))
            except (ValueError, TypeError):
                quantity = 0

            if quantity < 0:
                quantity = 0

            if quantity > 0:
                item_total = quantity * item['price']

                selected_items.append({
                    "name": item['name'],
                    "quantity": quantity,
                    "price": item['price'],
                    "total": item_total
                })

                total_amount += item_total

        if not selected_items:
            message = "Please select at least one food item."

        else:
            conn = get_db_connection()

            try:
                cursor = conn.execute("""
                    INSERT INTO food_order_batches
                    (user_id, total_amount)
                    VALUES (?, ?)
                """, (session['user_id'], total_amount))

                batch_id = cursor.lastrowid

                for item in selected_items:
                    conn.execute("""
                        INSERT INTO food_order_items
                        (batch_id, item_name, quantity,
                         unit_price, item_total)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        batch_id,
                        item['name'],
                        item['quantity'],
                        item['price'],
                        item['total']
                    ))

                conn.commit()

                return redirect('/food-bill/' + str(batch_id))

            finally:
                conn.close()

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Restaurant Menu - Grand Demo Hotel</title>

        <style>
            body {
                font-family: Arial;
                background: #f2f4f7;
                margin: 0;
                color: #243447;
            }

            header {
                background: #243447;
                color: white;
                text-align: center;
                padding: 20px;
            }

            .container {
                max-width: 1100px;
                margin: 30px auto;
                padding: 15px;
            }

            .food-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
                gap: 20px;
            }

            .food-card {
                background: white;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                text-align: center;
                padding-bottom: 20px;
            }

            .food-card img {
                width: 100%;
                height: 160px;
                object-fit: cover;
            }

            .food-card h3 {
                margin-bottom: 5px;
            }

            .price {
                color: #16834a;
                font-weight: bold;
                font-size: 18px;
            }

            input {
                width: 65px;
                padding: 9px;
                border: 1px solid #ccc;
                border-radius: 5px;
                text-align: center;
            }

            button, .back-button {
                background: #16834a;
                color: white;
                padding: 12px 20px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
                margin-top: 15px;
            }

            .message {
                color: red;
                text-align: center;
            }

            .actions {
                text-align: center;
                margin: 25px;
            }
        </style>
    </head>

    <body>

        <header>
            <h1>Grand Demo Hotel</h1>
            <h2>Restaurant Food Menu</h2>
            <p>Choose your favorite food</p>
        </header>

        <div class="container">

            <p class="message">{{ message }}</p>

            <form method="POST">

                <div class="food-grid">

                    {% for item in menu_items %}

                    <div class="food-card">

                        <img src="{{ item.image }}"
                             alt="{{ item.name }}">

                        <h3>{{ item.name }}</h3>

                        <p>{{ item.category }}</p>

                        <p class="price">
                            ₹{{ item.price }}
                        </p>

                        <label>Quantity:</label>

                        <input type="number"
                               name="quantity_{{ item.id }}"
                               min="0"
                               max="20"
                               value="0">

                    </div>

                    {% endfor %}

                </div>

                <div class="actions">

                    <button type="submit">
                        Generate Food Bill
                    </button>

                    <br>

                    <a class="back-button" href="/dashboard">
                        Back to Dashboard
                    </a>

                </div>

            </form>

        </div>

    </body>
    </html>
    """, menu_items=menu_items, message=message)



@app.route('/food-bill/<int:batch_id>', methods=['GET', 'POST'])
def food_bill(batch_id):

    if 'user_id' not in session:
        return redirect('/login')

    setup_restaurant_tables()

    conn = get_db_connection()

    try:
        order = conn.execute("""
            SELECT * FROM food_order_batches
            WHERE id = ? AND user_id = ?
        """, (batch_id, session['user_id'])).fetchone()

        if not order:
            return "Food order not found."

        items = conn.execute("""
            SELECT * FROM food_order_items
            WHERE batch_id = ?
        """, (batch_id,)).fetchall()

    finally:
        conn.close()

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Food Bill - Grand Demo Hotel</title>

        <style>
            body {
                font-family: Arial;
                background: #f2f4f7;
                margin: 0;
                color: #243447;
            }

            header {
                background: #243447;
                color: white;
                text-align: center;
                padding: 20px;
            }

            .bill {
                max-width: 650px;
                margin: 35px auto;
                background: white;
                padding: 25px;
                border-radius: 10px;
            }

            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }

            th, td {
                border-bottom: 1px solid #ddd;
                padding: 12px 5px;
                text-align: center;
            }

            th {
                background: #243447;
                color: white;
            }

            .total {
                text-align: right;
                font-size: 22px;
                color: #16834a;
                font-weight: bold;
                margin-top: 20px;
            }

            button {
                background: #16834a;
                color: white;
                border: none;
                padding: 12px 18px;
                border-radius: 5px;
                cursor: pointer;
                margin: 8px 4px;
            }

            .cash {
                background: #243447;
            }

            .center {
                text-align: center;
                margin-top: 25px;
            }
        </style>
    </head>

    <body>

        <header>
            <h1>Grand Demo Hotel</h1>
            <h2>Your Food Bill</h2>
        </header>

        <div class="bill">

            <h3>Bill Number: {{ order[0] }}</h3>

            <table>
                <tr>
                    <th>Food Item</th>
                    <th>Qty</th>
                    <th>Price</th>
                    <th>Total</th>
                </tr>

                {% for item in items %}
                <tr>
                    <td>{{ item[2] }}</td>
                    <td>{{ item[3] }}</td>
                    <td>₹{{ item[4] }}</td>
                    <td>₹{{ item[5] }}</td>
                </tr>
                {% endfor %}
            </table>

            <p class="total">
                Grand Total: ₹{{ order[2] }}
            </p>

            <div class="center">

                {% if order[4] == 'Pending' %}

                <h3>Select Payment Method</h3>

                <form method="POST"
                      action="/food-payment/{{ order[0] }}">

                    <button type="submit" name="payment_method"
                            value="Demo Online Payment">
                        Demo Online Payment
                    </button>

                    <button type="submit" name="payment_method"
                            value="Cash at Restaurant"
                            class="cash">
                        Cash at Restaurant
                    </button>

                </form>

                {% else %}

                <h3>Payment Method: {{ order[3] }}</h3>
                <h3>Payment Status: {{ order[4] }}</h3>
                <h3>Order Status: {{ order[5] }}</h3>

                {% endif %}

                <br>

                <a href="/my-food-orders">
                    My Food Orders
                </a>

                <br><br>

                <a href="/dashboard">
                    Back to Dashboard
                </a>

            </div>

        </div>

    </body>
    </html>
    """, order=order, items=items)


@app.route('/food-payment/<int:batch_id>', methods=['POST'])
def food_payment(batch_id):

    if 'user_id' not in session:
        return redirect('/login')

    payment_method = request.form.get('payment_method')

    if payment_method not in [
        'Demo Online Payment',
        'Cash at Restaurant'
    ]:
        return "Invalid payment method."

    setup_restaurant_tables()

    if payment_method == 'Demo Online Payment':
        payment_status = 'Paid'
    else:
        payment_status = 'Pending'

    conn = get_db_connection()

    try:
        conn.execute("""
            UPDATE food_order_batches
            SET payment_method = ?,
                payment_status = ?,
                order_status = 'Confirmed'
            WHERE id = ? AND user_id = ?
        """, (
            payment_method,
            payment_status,
            batch_id,
            session['user_id']
        ))

        conn.commit()

    finally:
        conn.close()

    return redirect('/food-bill/' + str(batch_id))


@app.route('/my-food-orders')
def my_food_orders():

    if 'user_id' not in session:
        return redirect('/login')

    setup_restaurant_tables()

    conn = get_db_connection()

    try:
        orders = conn.execute("""
            SELECT * FROM food_order_batches
            WHERE user_id = ?
            ORDER BY id DESC
        """, (session['user_id'],)).fetchall()

        order_items = {}

        for order in orders:
            items = conn.execute("""
                SELECT * FROM food_order_items
                WHERE batch_id = ?
            """, (order[0],)).fetchall()

            order_items[order[0]] = items

    finally:
        conn.close()

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>My Food Orders - Grand Demo Hotel</title>

        <style>
            body {
                font-family: Arial;
                background: #f2f4f7;
                margin: 0;
                color: #243447;
            }

            header {
                background: #243447;
                color: white;
                text-align: center;
                padding: 20px;
            }

            .container {
                max-width: 850px;
                margin: 30px auto;
                padding: 15px;
            }

            .order-card {
                background: white;
                padding: 22px;
                margin-bottom: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            }

            .total {
                color: #16834a;
                font-weight: bold;
                font-size: 19px;
            }

            .back-button {
                display: inline-block;
                background: #16834a;
                color: white;
                padding: 12px 20px;
                text-decoration: none;
                border-radius: 5px;
            }
        </style>
    </head>

    <body>

        <header>
            <h1>Grand Demo Hotel</h1>
            <h2>My Food Orders</h2>
        </header>

        <div class="container">

            {% for order in orders %}

            <div class="order-card">

                <h3>Order #{{ order[0] }}</h3>

                {% for item in order_items[order[0]] %}

                <p>
                    {{ item[2] }} -
                    Quantity: {{ item[3] }} -
                    ₹{{ item[5] }}
                </p>

                {% endfor %}

                <p class="total">
                    Total: ₹{{ order[2] }}
                </p>

                <p>
                    Payment Method: {{ order[3] }}
                </p>

                <p>
                    Payment Status: {{ order[4] }}
                </p>

                <p>
                    Order Status: {{ order[5] }}
                </p>

                <a href="/food-bill/{{ order[0] }}">
                    View Bill
                </a>

            </div>

            {% else %}

            <div class="order-card">
                <h3>No Food Orders Yet</h3>
                <p>Please visit our restaurant menu.</p>
            </div>

            {% endfor %}

            <a class="back-button" href="/menu">
                Order Food
            </a>

            <a class="back-button" href="/dashboard">
                Dashboard
            </a>

        </div>

    </body>
    </html>
    """, orders=orders, order_items=order_items)

# ================= END RESTAURANT SECTION =================


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')



# ================= ADMIN LOGIN =================

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():

    message = ""

    if request.method == 'POST':

        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        conn = get_db_connection()

        try:
            admin = conn.execute("""
                SELECT id, username, password
                FROM admins
                WHERE username = ?
            """, (username,)).fetchone()

            if admin and check_password_hash(admin[2], password):

                session['admin_id'] = admin[0]
                session['admin_username'] = admin[1]

                return redirect('/admin-dashboard')

            else:
                message = "Invalid Admin Username or Password."

        finally:
            conn.close()

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Login - Grand Demo Hotel</title>

        <style>
            body {
                font-family: Arial;
                background: #f2f4f7;
                margin: 0;
            }

            header {
                background: #243447;
                color: white;
                text-align: center;
                padding: 20px;
            }

            .login-box {
                background: white;
                width: 320px;
                margin: 50px auto;
                padding: 25px;
                border-radius: 10px;
                text-align: center;
            }

            input {
                width: 90%;
                padding: 12px;
                margin: 10px 0;
                border: 1px solid #ccc;
                border-radius: 5px;
            }

            button {
                background: #16834a;
                color: white;
                padding: 12px;
                width: 100%;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }

            a {
                color: #16834a;
                text-decoration: none;
            }
        </style>
    </head>

    <body>

        <header>
            <h1>Grand Demo Hotel</h1>
            <h2>Admin Login</h2>
        </header>

        <div class="login-box">

            <h2>Administrator</h2>

            <p style="color:red;">{{ message }}</p>

            <form method="POST">

                <input type="text"
                       name="username"
                       placeholder="Admin Username"
                       required>

                <input type="password"
                       name="password"
                       placeholder="Admin Password"
                       required>

                <button type="submit">Admin Login</button>

            </form>

            <p><a href="/">Back to Home</a></p>

        </div>

    </body>
    </html>
    """, message=message)


@app.route('/admin-logout')
def admin_logout():

    session.pop('admin_id', None)
    session.pop('admin_username', None)

    return redirect('/admin-login')

# ================= END ADMIN LOGIN =================

# ================= ADMIN DASHBOARD =================

@app.route('/admin-dashboard')
def admin_dashboard():

    if 'admin_id' not in session:
        return redirect('/admin-login')

    conn = get_db_connection()

    try:
        total_users = conn.execute(
            "SELECT COUNT(*) FROM users"
        ).fetchone()[0]

        total_rooms = conn.execute(
            "SELECT COUNT(*) FROM rooms"
        ).fetchone()[0]

        total_bookings = conn.execute(
            "SELECT COUNT(*) FROM bookings"
        ).fetchone()[0]

        total_food_orders = conn.execute(
            "SELECT COUNT(*) FROM food_order_batches"
        ).fetchone()[0]

    finally:
        conn.close()

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Dashboard - Grand Demo Hotel</title>

        <style>
            body {
                font-family: Arial;
                background: #f2f4f7;
                margin: 0;
                color: #243447;
            }

            header {
                background: #243447;
                color: white;
                text-align: center;
                padding: 20px;
            }

            .container {
                max-width: 1000px;
                margin: 35px auto;
                padding: 20px;
            }

            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
            }

            .card {
                background: white;
                padding: 25px;
                text-align: center;
                border-radius: 10px;
                border-left: 5px solid #16834a;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            }

            .card h2 {
                color: #16834a;
                font-size: 30px;
            }

            .logout {
                display: inline-block;
                margin-top: 30px;
                background: #c0392b;
                color: white;
                padding: 12px 20px;
                text-decoration: none;
                border-radius: 5px;
            }
        </style>
    </head>

    <body>

        <header>
            <h1>Grand Demo Hotel</h1>
            <h2>Admin Dashboard</h2>
            <p>Welcome, {{ admin_name }}</p>
        </header>

        <div class="container">

            <div class="stats">


             <div style="text-align:center; margin-top:15px;">
                <a href="/admin-users"
                   style="background:#16834a; color:white;
                   padding:12px 20px; text-decoration:none;
                   border-radius:5px; display:inline-block;">
                    Manage Users
                </a>
            </div>

               <div style="text-align:center; margin-top:15px;">
                <a href="/admin-rooms"
                   style="background:#16834a; color:white;
                   padding:12px 20px; text-decoration:none;
                   border-radius:5px; display:inline-block;">
                    Manage Rooms
                </a>
            </div>


            <div style="text-align:center; margin-top:30px;">
            <a href="/admin-bookings"
       style="background:#16834a; color:white;
       padding:12px 20px; text-decoration:none;
       border-radius:5px; display:inline-block;">
         Manage Bookings
            </a>
            </div>

              <div style="text-align:center; margin-top:15px;">
                                <a href="/admin-food-orders"
                                   style="background:#16834a; color:white;
                                   padding:12px 20px; text-decoration:none;
                                   border-radius:5px; display:inline-block;">
                                    Manage Restaurant Orders
                                </a>
                            </div>
   

                <div class="card">
                    <h3>Total Users</h3>
                    <h2>{{ total_users }}</h2>
                </div>

                <div class="card">
                    <h3>Total Rooms</h3>
                    <h2>{{ total_rooms }}</h2>
                </div>

                <div class="card">
                    <h3>Total Bookings</h3>
                    <h2>{{ total_bookings }}</h2>
                </div>

                <div class="card">
                    <h3>Total Food Orders</h3>
                    <h2>{{ total_food_orders }}</h2>
                </div>

            </div>

            <a class="logout" href="/admin-logout">
                Admin Logout
            </a>

        </div>

    </body>
    </html>
    """,
    admin_name=session.get('admin_username'),
    total_users=total_users,
    total_rooms=total_rooms,
    total_bookings=total_bookings,
    total_food_orders=total_food_orders
    )

# ================= END ADMIN DASHBOARD =================


# ================= ADMIN MANAGE BOOKINGS =================

@app.route('/admin-bookings', methods=['GET', 'POST'])
def admin_bookings():

    if 'admin_id' not in session:
        return redirect('/admin-login')

    conn = get_db_connection()

    try:

        if request.method == 'POST':

            booking_id = request.form.get('booking_id')
            new_status = request.form.get('booking_status')

            allowed_statuses = [
                'Pending',
                'Confirmed',
                'Cancelled'
            ]

            if new_status in allowed_statuses and booking_id:
                conn.execute("""
                    UPDATE bookings
                    SET booking_status = ?
                    WHERE id = ?
                """, (new_status, booking_id))

                conn.commit()

        bookings_data = conn.execute("""
            SELECT
                bookings.id,
                users.name,
                users.email,
                rooms.room_type,
                bookings.check_in,
                bookings.check_out,
                bookings.guests,
                bookings.total_price,
                bookings.payment_status,
                bookings.booking_status
            FROM bookings
            LEFT JOIN users
                ON bookings.user_id = users.id
            LEFT JOIN rooms
                ON bookings.room_id = rooms.id
            ORDER BY bookings.id DESC
        """).fetchall()

    finally:
        conn.close()

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Manage Bookings - Grand Demo Hotel</title>

        <style>
            body {
                font-family: Arial;
                background: #f2f4f7;
                margin: 0;
                color: #243447;
            }

            header {
                background: #243447;
                color: white;
                text-align: center;
                padding: 20px;
            }

            .container {
                max-width: 1100px;
                margin: 30px auto;
                padding: 15px;
            }

            .booking-card {
                background: white;
                padding: 20px;
                margin-bottom: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                overflow-wrap: anywhere;
            }

            .booking-card h3 {
                color: #16834a;
            }

            select {
                padding: 9px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }

            button {
                background: #16834a;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 5px;
                cursor: pointer;
            }

            .back-button {
                display: inline-block;
                background: #243447;
                color: white;
                padding: 12px 20px;
                text-decoration: none;
                border-radius: 5px;
                margin-bottom: 20px;
            }

            .empty {
                background: white;
                padding: 25px;
                text-align: center;
                border-radius: 10px;
            }
        </style>
    </head>

    <body>

        <header>
            <h1>Grand Demo Hotel</h1>
            <h2>Manage Room Bookings</h2>
        </header>

        <div class="container">

            <a class="back-button" href="/admin-dashboard">
                Back to Admin Dashboard
            </a>

            {% for booking in bookings_data %}

            <div class="booking-card">

                <h3>Booking ID: #{{ booking[0] }}</h3>

                <p><b>Customer:</b> {{ booking[1] or 'Unknown' }}</p>

                <p><b>Email:</b> {{ booking[2] or 'N/A' }}</p>

                <p><b>Room:</b> {{ booking[3] or 'N/A' }}</p>

                <p><b>Check-in:</b> {{ booking[4] }}</p>

                <p><b>Check-out:</b> {{ booking[5] }}</p>

                <p><b>Guests:</b> {{ booking[6] }}</p>

                <p><b>Total Amount:</b> ₹{{ booking[7] }}</p>

                <p><b>Payment Status:</b> {{ booking[8] }}</p>

                <p><b>Booking Status:</b> {{ booking[9] }}</p>

                <form method="POST">

                    <input type="hidden"
                           name="booking_id"
                           value="{{ booking[0] }}">

                    <label><b>Update Booking Status:</b></label>

                    <select name="booking_status">

                        <option value="Pending"
                            {% if booking[9] == 'Pending' %}selected{% endif %}>
                            Pending
                        </option>

                        <option value="Confirmed"
                            {% if booking[9] == 'Confirmed' %}selected{% endif %}>
                            Confirmed
                        </option>

                        <option value="Cancelled"
                            {% if booking[9] == 'Cancelled' %}selected{% endif %}>
                            Cancelled
                        </option>

                    </select>

                    <button type="submit">
                        Update Status
                    </button>

                </form>

            </div>

            {% else %}

            <div class="empty">
                <h3>No Bookings Found</h3>
            </div>

            {% endfor %}

        </div>

    </body>
    </html>
    """, bookings_data=bookings_data)

# ================= END ADMIN MANAGE BOOKINGS =================

@app.route('/admin-food-orders', methods=['GET', 'POST'])
def admin_food_orders():
    if 'admin_id' not in session:
        return redirect('/admin-login')

    conn = get_db_connection()

    # Update Food Order Status
    if request.method == 'POST':
        order_id = request.form.get('order_id')
        new_status = request.form.get('order_status')

        allowed_statuses = [
            'Pending', 'Confirmed', 'Preparing',
            'Ready', 'Completed', 'Cancelled'
        ]

        if new_status in allowed_statuses:
            conn.execute(
                "UPDATE food_order_batches SET order_status=? WHERE id=?",
                (new_status, order_id)
            )
            conn.commit()

        conn.close()
        return redirect('/admin-food-orders')

    # Fetch all food orders
    orders = conn.execute("""
        SELECT
            b.id,
            u.name,
            u.email,
            b.total_amount,
            b.payment_method,
            b.payment_status,
            b.order_status,
            b.created_at
        FROM food_order_batches b
        LEFT JOIN users u ON b.user_id = u.id
        ORDER BY b.id DESC
    """).fetchall()

    # Fetch items belonging to each order
    order_data = []

    for order in orders:
        items = conn.execute("""
            SELECT item_name, quantity, unit_price, item_total
            FROM food_order_items
            WHERE batch_id=?
        """, (order[0],)).fetchall()

        order_data.append((order, items))

    conn.close()

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Manage Restaurant Orders</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f4f4f4;
                padding: 20px;
            }
            h2 {
                text-align: center;
                color: #333;
            }
            .order-card {
                background: white;
                padding: 20px;
                margin: 20px auto;
                max-width: 750px;
                border-radius: 10px;
                box-shadow: 0 2px 8px #ccc;
            }
            .order-card h3 {
                color: #16834a;
            }
            .order-card select,
            .order-card button {
                padding: 10px;
                margin-top: 10px;
            }
            .order-card button {
                background: #16834a;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }
            .back {
                display: inline-block;
                margin: 10px;
                color: #16834a;
                text-decoration: none;
            }
        </style>
    </head>
    <body>

        <a class="back" href="/admin-dashboard">← Admin Dashboard</a>
        <h2>Manage Restaurant Orders</h2>

        {% if order_data %}
            {% for order, items in order_data %}
                <div class="order-card">
                    <h3>Food Order #{{ order[0] }}</h3>

                    <p><b>Customer:</b> {{ order[1] or 'Unknown' }}</p>
                    <p><b>Email:</b> {{ order[2] or 'N/A' }}</p>

                    <hr>
                    <h4>Ordered Items</h4>

                    {% for item in items %}
                        <p>
                            {{ item[0] }} -
                            Quantity: {{ item[1] }} -
                            ₹{{ item[3] }}
                        </p>
                    {% endfor %}

                    <hr>
                    <p><b>Total Amount:</b> ₹{{ order[3] }}</p>
                    <p><b>Payment Method:</b> {{ order[4] or 'N/A' }}</p>
                    <p><b>Payment Status:</b> {{ order[5] }}</p>
                    <p><b>Current Order Status:</b> {{ order[6] }}</p>
                    <p><b>Order Date:</b> {{ order[7] }}</p>

                    <form method="POST">
                        <input type="hidden" name="order_id"
                               value="{{ order[0] }}">

                        <label><b>Update Order Status:</b></label>
                        <select name="order_status" required>
                            {% for status in [
                                'Pending', 'Confirmed', 'Preparing',
                                'Ready', 'Completed', 'Cancelled'
                            ] %}
                                <option value="{{ status }}"
                                    {% if order[6] == status %}selected{% endif %}>
                                    {{ status }}
                                </option>
                            {% endfor %}
                        </select>

                        <button type="submit">Update Status</button>
                    </form>
                </div>
            {% endfor %}
        {% else %}
            <p style="text-align:center;">No food orders found.</p>
        {% endif %}

    </body>
    </html>
    """, order_data=order_data)



@app.route('/admin-rooms', methods=['GET', 'POST'])
def admin_rooms():
    if 'admin_id' not in session:
        return redirect('/admin-login')

    conn = get_db_connection()

    if request.method == 'POST':
        action = request.form.get('action')
        room_id = request.form.get('room_id')

        if action == 'add':
            room_type = request.form.get('room_type', '').strip()
            description = request.form.get('description', '').strip()
            price = request.form.get('price', '')
            capacity = request.form.get('capacity', '')
            facilities = request.form.get('facilities', '').strip()

            try:
                price = float(price)
                capacity = int(capacity)

                if room_type and price > 0 and capacity > 0:
                    conn.execute("""
                        INSERT INTO rooms
                        (room_type, description, price, capacity, facilities, available)
                        VALUES (?, ?, ?, ?, ?, 1)
                    """, (room_type, description, price, capacity, facilities))
                    conn.commit()
            except (ValueError, TypeError):
                pass

        elif action == 'update':
            room_type = request.form.get('room_type', '').strip()
            description = request.form.get('description', '').strip()
            price = request.form.get('price', '')
            capacity = request.form.get('capacity', '')
            facilities = request.form.get('facilities', '').strip()
            available = request.form.get('available', '1')

            try:
                price = float(price)
                capacity = int(capacity)

                if room_type and price > 0 and capacity > 0 and available in ('0', '1'):
                    conn.execute("""
                        UPDATE rooms
                        SET room_type=?, description=?, price=?,
                            capacity=?, facilities=?, available=?
                        WHERE id=?
                    """, (room_type, description, price, capacity,
                          facilities, int(available), room_id))
                    conn.commit()
            except (ValueError, TypeError):
                pass

        elif action == 'delete':
            # Do not delete a room that has booking records
            booking = conn.execute(
                "SELECT id FROM bookings WHERE room_id=? LIMIT 1",
                (room_id,)
            ).fetchone()

            if not booking:
                conn.execute("DELETE FROM rooms WHERE id=?", (room_id,))
                conn.commit()

        conn.close()
        return redirect('/admin-rooms')

    rooms = conn.execute("""
        SELECT id, room_type, description, price,
               capacity, facilities, available
        FROM rooms
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Manage Rooms</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f4f4f4;
                padding: 20px;
            }
            h2 { text-align: center; }
            .card, .add-box {
                background: white;
                max-width: 750px;
                margin: 20px auto;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 8px #ccc;
            }
            input, textarea, select {
                width: 100%;
                padding: 10px;
                margin: 7px 0 14px;
                box-sizing: border-box;
            }
            button {
                padding: 10px 16px;
                border: none;
                border-radius: 5px;
                color: white;
                cursor: pointer;
            }
            .save { background: #16834a; }
            .delete { background: #c0392b; }
            .back {
                color: #16834a;
                text-decoration: none;
            }
            hr { margin: 20px 0; }
        </style>
    </head>
    <body>

        <a class="back" href="/admin-dashboard">← Admin Dashboard</a>
        <h2>Manage Rooms</h2>

        <div class="add-box">
            <h3>Add New Room</h3>

            <form method="POST">
                <input type="hidden" name="action" value="add">

                <label>Room Type</label>
                <input name="room_type" placeholder="Example: Deluxe"
                       required>

                <label>Description</label>
                <textarea name="description"
                          placeholder="Room description"></textarea>

                <label>Price per Night (₹)</label>
                <input type="number" name="price" min="1" step="0.01"
                       required>

                <label>Capacity (Guests)</label>
                <input type="number" name="capacity" min="1" required>

                <label>Facilities</label>
                <input name="facilities"
                       placeholder="AC, Wi-Fi, TV">

                <button class="save" type="submit">Add Room</button>
            </form>
        </div>

        <h2>All Rooms</h2>

        {% if rooms %}
            {% for room in rooms %}
                <div class="card">
                    <h3>Room #{{ room[0] }} - {{ room[1] }}</h3>

                    <form method="POST">
                        <input type="hidden" name="action" value="update">
                        <input type="hidden" name="room_id"
                               value="{{ room[0] }}">

                        <label>Room Type</label>
                        <input name="room_type" value="{{ room[1] }}"
                               required>

                        <label>Description</label>
                        <textarea name="description">{{ room[2] or '' }}</textarea>

                        <label>Price per Night (₹)</label>
                        <input type="number" name="price"
                               value="{{ room[3] }}" min="1"
                               step="0.01" required>

                        <label>Capacity</label>
                        <input type="number" name="capacity"
                               value="{{ room[4] }}" min="1" required>

                        <label>Facilities</label>
                        <input name="facilities"
                               value="{{ room[5] or '' }}">

                        <label>Availability</label>
                        <select name="available">
                            <option value="1"
                                {% if room[6] == 1 %}selected{% endif %}>
                                Available
                            </option>
                            <option value="0"
                                {% if room[6] == 0 %}selected{% endif %}>
                                Not Available
                            </option>
                        </select>

                        <button class="save" type="submit">
                            Save Changes
                        </button>
                    </form>

                    <hr>

                    <form method="POST"
                          onsubmit="return confirm('Are you sure you want to delete this room?');">
                        <input type="hidden" name="action" value="delete">
                        <input type="hidden" name="room_id"
                               value="{{ room[0] }}">
                        <button class="delete" type="submit">
                            Delete Room
                        </button>
                    </form>
                </div>
            {% endfor %}
        {% else %}
            <p style="text-align:center;">No rooms found.</p>
        {% endif %}

    </body>
    </html>
    """, rooms=rooms)

@app.route('/admin-users')
def admin_users():
    if 'admin_id' not in session:
        return redirect('/admin-login')

    conn = get_db_connection()

    users = conn.execute("""
        SELECT id, name, email, created_at
        FROM users
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Manage Users</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f4f4f4;
                padding: 20px;
            }
            h2 { text-align: center; }
            .user-card {
                background: white;
                max-width: 700px;
                margin: 15px auto;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 8px #ccc;
            }
            .back {
                color: #16834a;
                text-decoration: none;
            }
        </style>
    </head>
    <body>

        <a class="back" href="/admin-dashboard">
            ← Admin Dashboard
        </a>

        <h2>Registered Users</h2>

        <p style="text-align:center;">
            Total Users: {{ users|length }}
        </p>

        {% if users %}
            {% for user in users %}
                <div class="user-card">
                    <h3>{{ user[1] }}</h3>
                    <p><b>User ID:</b> {{ user[0] }}</p>
                    <p><b>Email:</b> {{ user[2] }}</p>
                    <p><b>Registration Date:</b> {{ user[3] }}</p>
                </div>
            {% endfor %}
        {% else %}
            <p style="text-align:center;">No registered users found.</p>
        {% endif %}

    </body>
    </html>
    """, users=users)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    