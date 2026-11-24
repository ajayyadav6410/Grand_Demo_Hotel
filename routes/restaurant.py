
from flask import Blueprint, render_template, request, redirect, session
from database import get_db_connection


restaurant_bp = Blueprint("restaurant", __name__)


def customer_logged_in():
    return "user_id" in session


@restaurant_bp.route("/menu", methods=["GET", "POST"])
def menu():

    connection = get_db_connection()

    try:
        rows = connection.execute(
            """
            SELECT id, item_name, price, category, image
            FROM restaurant_menu
            ORDER BY id
            """
        ).fetchall()

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

        if request.method == "POST":
            selected_items = []
            total_amount = 0

            for item in menu_items:
                try:
                    quantity = int(
                        request.form.get(
                            "quantity_" + str(item["id"]), 0
                        )
                    )
                except (ValueError, TypeError):
                    quantity = 0

                if quantity < 0 or quantity > 20:
                    quantity = 0

                if quantity > 0:
                    item_total = quantity * item["price"]

                    selected_items.append({
                        "name": item["name"],
                        "quantity": quantity,
                        "price": item["price"],
                        "total": item_total
                    })

                    total_amount += item_total

            if not selected_items:
                message = "Please select at least one food item."

            else:
                cursor = connection.execute(
                    """
                    INSERT INTO food_order_batches
                    (user_id, total_amount)
                    VALUES (?, ?)
                    """,
                    (session["user_id"], total_amount)
                )

                batch_id = cursor.lastrowid

                for item in selected_items:
                    connection.execute(
                        """
                        INSERT INTO food_order_items
                        (
                            batch_id, item_name, quantity,
                            unit_price, item_total
                        )
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            batch_id,
                            item["name"],
                            item["quantity"],
                            item["price"],
                            item["total"]
                        )
                    )

                connection.commit()

                return redirect(f"/food-bill/{batch_id}")

        return render_template(
            "restaurant/menu.html",
            menu_items=menu_items,
            message=message
        )

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


@restaurant_bp.route("/food-bill/<int:batch_id>")
def food_bill(batch_id):
    if not customer_logged_in():
        return redirect("/login")

    connection = get_db_connection()

    try:
        order = connection.execute(
            """
            SELECT *
            FROM food_order_batches
            WHERE id = ? AND user_id = ?
            """,
            (batch_id, session["user_id"])
        ).fetchone()

        if not order:
            return "Food order not found.", 404

        items = connection.execute(
            """
            SELECT *
            FROM food_order_items
            WHERE batch_id = ?
            """,
            (batch_id,)
        ).fetchall()

        return render_template(
            "restaurant/food_bill.html",
            order=order,
            items=items
        )

    finally:
        connection.close()


@restaurant_bp.route(
    "/food-payment/<int:batch_id>",
    methods=["POST"]
)
def food_payment(batch_id):
    if not customer_logged_in():
        return redirect("/login")

    payment_method = request.form.get("payment_method")

    if payment_method not in [
        "Demo Online Payment",
        "Cash at Restaurant"
    ]:
        return "Invalid payment method.", 400

    if payment_method == "Demo Online Payment":
        payment_status = "Paid"
    else:
        payment_status = "Pending"

    connection = get_db_connection()

    try:
        connection.execute(
            """
            UPDATE food_order_batches
            SET payment_method = ?,
                payment_status = ?,
                order_status = 'Confirmed'
            WHERE id = ? AND user_id = ?
            """,
            (
                payment_method,
                payment_status,
                batch_id,
                session["user_id"]
            )
        )

        connection.commit()

    finally:
        connection.close()

    return redirect(f"/food-bill/{batch_id}")
