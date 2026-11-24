
from flask import Blueprint, render_template, request, redirect, session
from database import get_db_connection
from services.security_service import verify_password


admin_bp = Blueprint("admin", __name__)


def admin_logged_in():
    return "admin_id" in session


@admin_bp.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    message = ""

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        connection = get_db_connection()

        try:
            admin = connection.execute(
                """
                SELECT id, username, password
                FROM admins
                WHERE username = ?
                """,
                (username,)
            ).fetchone()

            if admin and verify_password(admin[2], password):
                session.clear()
                session.permanent = True
                session["admin_id"] = admin[0]
                session["admin_username"] = admin[1]

                return redirect("/admin-dashboard")

            message = "Invalid Admin Username or Password."

        finally:
            connection.close()

    return render_template(
        "admin/login.html",
        message=message
    )


@admin_bp.route("/admin-logout")
def admin_logout():
    session.pop("admin_id", None)
    session.pop("admin_username", None)
    return redirect("/admin-login")


@admin_bp.route("/admin-dashboard")
def admin_dashboard():
    if not admin_logged_in():
        return redirect("/admin-login")

    connection = get_db_connection()

    try:
        total_users = connection.execute(
            "SELECT COUNT(*) FROM users"
        ).fetchone()[0]

        total_rooms = connection.execute(
            "SELECT COUNT(*) FROM rooms"
        ).fetchone()[0]

        total_bookings = connection.execute(
            "SELECT COUNT(*) FROM bookings"
        ).fetchone()[0]

        total_food_orders = connection.execute(
            "SELECT COUNT(*) FROM food_order_batches"
        ).fetchone()[0]

        return render_template(
            "admin/dashboard.html",
            total_users=total_users,
            total_rooms=total_rooms,
            total_bookings=total_bookings,
            total_food_orders=total_food_orders
        )

    finally:
        connection.close()


@admin_bp.route("/admin-bookings", methods=["GET", "POST"])
def admin_bookings():
    if not admin_logged_in():
        return redirect("/admin-login")

    connection = get_db_connection()

    try:
        if request.method == "POST":
            booking_id = request.form.get("booking_id")
            new_status = request.form.get("booking_status")

            allowed_statuses = [
                "Pending", "Confirmed", "Cancelled"
            ]

            if new_status in allowed_statuses:
                connection.execute(
                    """
                    UPDATE bookings
                    SET booking_status = ?
                    WHERE id = ?
                    """,
                    (new_status, booking_id)
                )
                connection.commit()

            return redirect("/admin-bookings")

        bookings_data = connection.execute(
            """
            SELECT
                b.id,
                u.name,
                u.email,
                r.room_type,
                b.check_in,
                b.check_out,
                b.guests,
                b.total_price,
                b.payment_status,
                b.booking_status
            FROM bookings b
            LEFT JOIN users u ON b.user_id = u.id
            LEFT JOIN rooms r ON b.room_id = r.id
            ORDER BY b.id DESC
            """
        ).fetchall()

        return render_template(
            "admin/bookings.html",
            bookings_data=bookings_data
        )

    finally:
        connection.close()


@admin_bp.route("/admin-food-orders", methods=["GET", "POST"])
def admin_food_orders():
    if not admin_logged_in():
        return redirect("/admin-login")

    connection = get_db_connection()

    try:
        if request.method == "POST":
            order_id = request.form.get("order_id")
            new_status = request.form.get("order_status")

            allowed_statuses = [
                "Pending", "Confirmed", "Preparing",
                "Ready", "Completed", "Cancelled"
            ]

            if new_status in allowed_statuses:
                connection.execute(
                    """
                    UPDATE food_order_batches
                    SET order_status = ?
                    WHERE id = ?
                    """,
                    (new_status, order_id)
                )
                connection.commit()

            return redirect("/admin-food-orders")

        orders = connection.execute(
            """
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
            """
        ).fetchall()

        order_data = []

        for order in orders:
            items = connection.execute(
                """
                SELECT item_name, quantity, unit_price, item_total
                FROM food_order_items
                WHERE batch_id = ?
                """,
                (order[0],)
            ).fetchall()

            order_data.append((order, items))

        return render_template(
            "admin/food_orders.html",
            order_data=order_data
        )

    finally:
        connection.close()


@admin_bp.route("/admin-rooms", methods=["GET", "POST"])
def admin_rooms():
    if not admin_logged_in():
        return redirect("/admin-login")

    connection = get_db_connection()

    try:
        if request.method == "POST":
            action = request.form.get("action")
            room_id = request.form.get("room_id")

            if action == "add":
                room_type = request.form.get(
                    "room_type", ""
                ).strip()
                description = request.form.get(
                    "description", ""
                ).strip()
                facilities = request.form.get(
                    "facilities", ""
                ).strip()

                try:
                    price = float(request.form.get("price", ""))
                    capacity = int(request.form.get("capacity", ""))

                    if room_type and price > 0 and capacity > 0:
                        connection.execute(
                            """
                            INSERT INTO rooms
                            (
                                room_type, description, price,
                                capacity, facilities, available
                            )
                            VALUES (?, ?, ?, ?, ?, 1)
                            """,
                            (
                                room_type, description, price,
                                capacity, facilities
                            )
                        )
                        connection.commit()

                except (ValueError, TypeError):
                    pass

            elif action == "update":
                room_type = request.form.get(
                    "room_type", ""
                ).strip()
                description = request.form.get(
                    "description", ""
                ).strip()
                facilities = request.form.get(
                    "facilities", ""
                ).strip()
                available = request.form.get("available", "1")

                try:
                    price = float(request.form.get("price", ""))
                    capacity = int(request.form.get("capacity", ""))

                    if (
                        room_type
                        and price > 0
                        and capacity > 0
                        and available in ("0", "1")
                    ):
                        connection.execute(
                            """
                            UPDATE rooms
                            SET room_type = ?,
                                description = ?,
                                price = ?,
                                capacity = ?,
                                facilities = ?,
                                available = ?
                            WHERE id = ?
                            """,
                            (
                                room_type, description, price,
                                capacity, facilities,
                                int(available), room_id
                            )
                        )
                        connection.commit()

                except (ValueError, TypeError):
                    pass

            elif action == "delete":
                booking = connection.execute(
                    """
                    SELECT id FROM bookings
                    WHERE room_id = ?
                    LIMIT 1
                    """,
                    (room_id,)
                ).fetchone()

                if not booking:
                    connection.execute(
                        "DELETE FROM rooms WHERE id = ?",
                        (room_id,)
                    )
                    connection.commit()

            return redirect("/admin-rooms")

        rooms = connection.execute(
            """
            SELECT id, room_type, description, price,
                   capacity, facilities, available
            FROM rooms
            ORDER BY id DESC
            """
        ).fetchall()

        return render_template(
            "admin/rooms.html",
            rooms=rooms
        )

    finally:
        connection.close()


@admin_bp.route("/admin-users")
def admin_users():
    if not admin_logged_in():
        return redirect("/admin-login")

    connection = get_db_connection()

    try:
        users = connection.execute(
            """
            SELECT id, name, email, created_at
            FROM users
            ORDER BY id DESC
            """
        ).fetchall()

        return render_template(
            "admin/users.html",
            users=users
        )

    finally:
        connection.close()
