
from datetime import date
from flask import Blueprint, render_template, request, redirect, session
from database import get_db_connection
from services.booking_service import is_room_available


booking_bp = Blueprint("booking", __name__)


def customer_logged_in():
    return "user_id" in session


@booking_bp.route("/rooms")
def rooms():
    connection = get_db_connection()

    try:
        room_data = connection.execute(
            """
            SELECT id, room_type, description, price,
                   capacity, facilities, available
            FROM rooms
            WHERE available = 1
            ORDER BY id
            """
        ).fetchall()

        return render_template(
            "booking/rooms.html",
            rooms=room_data
        )

    finally:
        connection.close()


@booking_bp.route("/book/<int:room_id>", methods=["GET", "POST"])
def book_room(room_id):
    if not customer_logged_in():
        return redirect("/login")

    message = ""
    connection = get_db_connection()

    try:
        room = connection.execute(
            """
            SELECT id, room_type, price, capacity, available
            FROM rooms
            WHERE id = ?
            """,
            (room_id,)
        ).fetchone()

    finally:
        connection.close()

    if not room or room[4] != 1:
        return redirect("/rooms")

    if request.method == "POST":
        check_in = request.form.get("check_in", "")
        check_out = request.form.get("check_out", "")
        guests_text = request.form.get("guests", "")

        try:
            check_in_date = date.fromisoformat(check_in)
            check_out_date = date.fromisoformat(check_out)
            guests = int(guests_text)

            if check_in_date < date.today():
                message = "Check-in date cannot be in the past."

            elif check_out_date <= check_in_date:
                message = "Check-out must be after check-in."

            elif guests < 1 or guests > room[3]:
                message = "Please select a valid number of guests."

            elif not is_room_available(
                room_id, check_in, check_out
            ):
                message = "This room is not available for these dates."

            else:
                nights = (check_out_date - check_in_date).days
                total_price = nights * room[2]

                connection = get_db_connection()

                try:
                    result = connection.execute(
                        """
                        INSERT INTO bookings
                        (
                            user_id, room_id, check_in, check_out,
                            guests, total_price, payment_status,
                            booking_status
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            session["user_id"],
                            room_id,
                            check_in,
                            check_out,
                            guests,
                            total_price,
                            "Pending",
                            "Pending"
                        )
                    )

                    connection.commit()

                    booking_id = result.lastrowid

                    return redirect(
                        f"/payment/{booking_id}"
                    )

                finally:
                    connection.close()

        except (ValueError, TypeError):
            message = "Please enter valid booking details."

    return render_template(
        "booking/book.html",
        room=room,
        message=message
    )


@booking_bp.route("/payment/<int:booking_id>", methods=["GET", "POST"])
def payment(booking_id):
    if not customer_logged_in():
        return redirect("/login")

    connection = get_db_connection()

    try:
        booking = connection.execute(
            """
            SELECT id, total_price, payment_status, booking_status
            FROM bookings
            WHERE id = ? AND user_id = ?
            """,
            (booking_id, session["user_id"])
        ).fetchone()

        if not booking:
            return redirect("/my-bookings")

        if request.method == "POST":
            connection.execute(
                """
                UPDATE bookings
                SET payment_status = ?,
                    booking_status = ?
                WHERE id = ? AND user_id = ?
                """,
                (
                    "Paid",
                    "Confirmed",
                    booking_id,
                    session["user_id"]
                )
            )

            connection.commit()
            return redirect("/my-bookings")

        return render_template(
            "booking/payment.html",
            booking=booking
        )

    finally:
        connection.close()
