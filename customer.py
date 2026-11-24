
from flask import Blueprint, render_template, session, redirect
from database import get_db_connection


customer_bp = Blueprint("customer", __name__)


def login_required():
    """Check whether a customer is logged in."""
    return "user_id" in session


@customer_bp.route("/dashboard")
def dashboard():
    if not login_required():
        return redirect("/login")

    connection = get_db_connection()

    try:
        user_id = session["user_id"]

        bookings = connection.execute(
            """
            SELECT COUNT(*)
            FROM bookings
            WHERE user_id = ?
            """,
            (user_id,)
        ).fetchone()[0]

        food_orders = connection.execute(
            """
            SELECT COUNT(*)
            FROM food_order_batches
            WHERE user_id = ?
            """,
            (user_id,)
        ).fetchone()[0]

        return render_template(
            "customer/dashboard.html",
            bookings_count=bookings,
            food_orders_count=food_orders
        )

    finally:
        connection.close()


@customer_bp.route("/facilities")
def facilities():

    connection = get_db_connection()

    try:
        facilities_data = connection.execute(
            """
            SELECT id, name, description
            FROM facilities
            ORDER BY id
            """
        ).fetchall()

        return render_template(
            "customer/facilities.html",
            facilities=facilities_data
        )

    finally:
        connection.close()


@customer_bp.route("/my-bookings")
def my_bookings():
    if not login_required():
        return redirect("/login")

    connection = get_db_connection()

    try:
        bookings = connection.execute(
            """
            SELECT
                bookings.id,
                rooms.room_type,
                bookings.check_in,
                bookings.check_out,
                bookings.guests,
                bookings.total_price,
                bookings.payment_status,
                bookings.booking_status
            FROM bookings
            JOIN rooms ON bookings.room_id = rooms.id
            WHERE bookings.user_id = ?
            ORDER BY bookings.id DESC
            """,
            (session["user_id"],)
        ).fetchall()

        return render_template(
            "customer/my_bookings.html",
            bookings=bookings
        )

    finally:
        connection.close()


@customer_bp.route("/my-food-orders")
def my_food_orders():
    if not login_required():
        return redirect("/login")

    connection = get_db_connection()

    try:
        orders = connection.execute(
            """
            SELECT
                id,
                total_amount,
                payment_method,
                payment_status,
                order_status,
                created_at
            FROM food_order_batches
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (session["user_id"],)
        ).fetchall()

        return render_template(
            "restaurant/my_orders.html",
            orders=orders
        )

    finally:
        connection.close()
