from datetime import datetime, timezone

from flask import Flask
from sqlalchemy import inspect, text
from .config import Config
from .models import db, login_manager, User
from .routes import main
import cloudinary


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "main.login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()

        # db.create_all() only creates missing tables, it doesn't add new
        # columns to a table that already exists. Since this project has
        # no migration tool, add the "image_url" column by hand if an
        # older database is missing it, without touching existing rows.
        inspector = inspect(db.engine)

        if "restaurant_table" in inspector.get_table_names():

            columns = [
                column["name"]
                for column in inspector.get_columns("restaurant_table")
            ]

            if "image_url" not in columns:
                db.session.execute(
                    text(
                        "ALTER TABLE restaurant_table "
                        "ADD COLUMN image_url VARCHAR(500)"
                    )
                )
                db.session.commit()

    app.register_blueprint(main)

    # Makes {{ current_year }} available in every template (used in the footer)
    @app.context_processor
    def inject_current_year():
        return {"current_year": datetime.now(timezone.utc).year}

    cloudinary.config(
        cloud_name=app.config["CLOUDINARY_CLOUD_NAME"],
        api_key=app.config["CLOUDINARY_API_KEY"],
        api_secret=app.config["CLOUDINARY_API_SECRET"]
    )

    return app