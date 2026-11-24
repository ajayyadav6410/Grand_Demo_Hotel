
from flask import Blueprint, render_template, request, redirect, session
from database import get_db_connection
from services.security_service import hash_password, verify_password


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    message = ""

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            message = "Please fill all fields."

        elif len(password) < 8:
            message = "Password must be at least 8 characters long."

        else:
            connection = get_db_connection()

            try:
                existing_user = connection.execute(
                    """
                    SELECT id FROM users
                    WHERE LOWER(email) = ?
                    """,
                    (email,)
                ).fetchone()

                if existing_user:
                    message = "This email is already registered. Try another."

                else:
                    password_hash = hash_password(password)

                    connection.execute(
                        """
                        INSERT INTO users (name, email, password)
                        VALUES (?, ?, ?)
                        """,
                        (name, email, password_hash)
                    )

                    connection.commit()
                    message = "Registration Successful! Please login."

            except Exception:
                connection.rollback()
                message = "Registration could not be completed. Please try again."

            finally:
                connection.close()

    return render_template("auth/register.html", message=message)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    message = ""

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            message = "Please enter email and password."

        else:
            connection = get_db_connection()

            try:
                user = connection.execute(
                    """
                    SELECT password, id, name, email
                    FROM users
                    WHERE LOWER(email) = ?
                    """,
                    (email,)
                ).fetchone()

                if user and verify_password(user[0], password):
                    session.clear()
                    session.permanent = True
                    session["user_id"] = user[1]
                    session["user_name"] = user[2]

                    return redirect("/dashboard")

                message = "Invalid email or password."

            finally:
                connection.close()

    return render_template("auth/login.html", message=message)


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")

