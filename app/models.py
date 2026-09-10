from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager

db = SQLAlchemy()
login_manager = LoginManager()


class User(UserMixin, db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        default="customer"
    )

    reservations = db.relationship(
        "Reservation",
        backref="customer",
        lazy=True
    )


class RestaurantTable(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    table_number = db.Column(
        db.Integer,
        unique=True,
        nullable=False
    )

    capacity = db.Column(
        db.Integer,
        nullable=False
    )

    image_url = db.Column(
        db.String(500),
        nullable=True
    )

    reservations = db.relationship(
        "Reservation",
        backref="table",
        lazy=True
    )


class Reservation(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    reservation_date = db.Column(
        db.Date,
        nullable=False
    )

    reservation_time = db.Column(
        db.Time,
        nullable=False
    )

    guests = db.Column(
        db.Integer,
        nullable=False
    )

    status = db.Column(
        db.String(20),
        default="Pending"
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )

    table_id = db.Column(
        db.Integer,
        db.ForeignKey("restaurant_table.id")
    )


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class RestaurantImage(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(100),
        nullable=False
    )

    image_url = db.Column(
        db.String(500),
        nullable=False
    )