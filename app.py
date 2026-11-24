
from flask import Flask, render_template

from config import get_config
from database import get_db_connection
from extensions import init_extensions

from routes.auth import auth_bp
from routes.customer import customer_bp
from routes.booking import booking_bp
from routes.restaurant import restaurant_bp
from routes.admin import admin_bp


def create_app():
    app = Flask(__name__)

    # Load application configuration
    app.config.from_object(get_config())

    # Initialize optional Redis connection
    init_extensions(app)

    # Register all application blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(restaurant_bp)
    app.register_blueprint(admin_bp)

    # Home page
    @app.route("/")
    def home():
        return render_template("home.html")

    # Simple health check
    @app.route("/health")
    def health():
        return {"status": "ok", "application": "Grand Demo Hotel"}, 200

    return app


app = create_app()


# Keep get_db_connection available from app.py
# for existing scripts such as init_db.py and create_admin.py.

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=app.config.get("DEBUG", False)
    )