from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    DateField,
    TimeField,
    IntegerField
)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    Optional
)
from flask_wtf.file import (
    FileField,
    FileRequired,
    FileAllowed
)
from wtforms import HiddenField


class RegisterForm(FlaskForm):

    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=3, max=50)
        ]
    )

    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Email()
        ]
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=6)
        ]
    )

    submit = SubmitField("Register")


class LoginForm(FlaskForm):

    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Email()
        ]
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired()
        ]
    )

    submit = SubmitField("Login")


from wtforms import IntegerField
from wtforms.validators import NumberRange
class TableForm(FlaskForm):

    table_number = IntegerField(
        "Table Number",
        validators=[
            DataRequired()
        ]
    )

    capacity = IntegerField(
        "Capacity",
        validators=[
            DataRequired(),
            NumberRange(min=1)
        ]
    )

    image = FileField(
        "Table Photo (optional)",
        validators=[
            FileAllowed(
                ["jpg", "jpeg", "png", "webp"],
                "Images only!"
            )
        ]
    )

    submit = SubmitField("Add Table")


class TableSearchForm(FlaskForm):

    reservation_date = DateField(
        "Date",
        validators=[DataRequired()]
    )

    reservation_time = TimeField(
        "Time",
        validators=[DataRequired()]
    )

    guests = IntegerField(
        "Number of Guests",
        validators=[
            DataRequired(),
            NumberRange(min=1)
        ]
    )

    submit = SubmitField("Search Available Tables")


class ReserveTableForm(FlaskForm):
    """
    Tiny hidden form rendered once per table on the search results page,
    so clicking "Reserve" on a specific table carries the search
    criteria (date/time/guests) along with it, plus CSRF protection.
    """

    reservation_date = HiddenField(
        validators=[DataRequired()]
    )

    reservation_time = HiddenField(
        validators=[DataRequired()]
    )

    guests = HiddenField(
        validators=[DataRequired()]
    )

    submit = SubmitField("Reserve This Table")

class CancelReservationForm(FlaskForm):
    """Tiny confirm-and-CSRF form for the Cancel button on My Reservations."""

    submit = SubmitField("Cancel Reservation")


class ProfileForm(FlaskForm):

    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=3, max=50)
        ]
    )

    current_password = PasswordField(
        "Current Password",
        validators=[DataRequired()]
    )

    new_password = PasswordField(
        "New Password (leave blank to keep it)",
        validators=[
            Optional(),
            Length(min=6)
        ]
    )

    submit = SubmitField("Save Changes")


class ImageUploadForm(FlaskForm):

    title = StringField(
        "Image Title",
        validators=[DataRequired()]
    )

    image = FileField(
        "Image",
        validators=[FileRequired()]
    )

    submit = SubmitField(
        "Upload"
    )