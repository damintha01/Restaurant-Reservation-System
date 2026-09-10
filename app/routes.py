import re
from datetime import datetime

from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from .models import db, User,RestaurantTable, Reservation,RestaurantImage
from .forms import (
    RegisterForm,
    LoginForm,
    TableForm,
    ImageUploadForm,
    TableSearchForm,
    ReserveTableForm,
    CancelReservationForm,
    ProfileForm
)

from flask import Blueprint
from .decorators import admin_required
from .cloudinary_service import upload_image
from .services.email_service import (
    send_booking_confirmation,
    send_welcome_email
)



main = Blueprint("main", __name__)


def apply_gallery_photos(tables):
    """
    Tables without their own photo fall back to a gallery image titled
    after their number, e.g. "Table 1" or "Tabel 2" (a common typo) for
    the table numbered 1 or 2. Doesn't touch tables that already have
    their own uploaded photo, and doesn't write anything to the database.
    """

    gallery_by_number = {}

    for image in RestaurantImage.query.all():

        match = re.match(
            r"^\s*tab[le]{2}\D*(\d+)",
            image.title.strip().lower()
        )

        if match:
            gallery_by_number[int(match.group(1))] = image.image_url

    for table in tables:
        if not table.image_url:
            table.image_url = gallery_by_number.get(table.table_number)

    return tables


# Homepage: shows the Login and Register forms side by side.
# "tab" tells the page which of the two forms to show first,
# e.g. /?tab=register opens straight on the Register side.
@main.route("/")
def index():

    active_tab = request.args.get("tab", "login")

    return render_template(
        "home.html",
        login_form=LoginForm(),
        register_form=RegisterForm(),
        active_tab=active_tab
    )


@main.route("/about")
def about():

    return render_template("about.html")


@main.route("/register", methods=["GET", "POST"])
def register():

    form = RegisterForm()

    if form.validate_on_submit():

        existing_user = User.query.filter(
            (User.username == form.username.data) |
            (User.email == form.email.data)
        ).first()

        if existing_user:

            if existing_user.username == form.username.data:
                form.username.errors.append("That username is already taken.")

            if existing_user.email == form.email.data:
                form.email.errors.append("An account with that email already exists.")

        else:

            hashed_password = generate_password_hash(
                form.password.data
            )

            user = User(
                username=form.username.data,
                email=form.email.data,
                password_hash=hashed_password
            )

            db.session.add(user)
            db.session.commit()

            send_welcome_email(
                customer_email=user.email,
                customer_name=user.username
            )

            flash("Registration successful! Please log in.")

            return redirect(
                url_for("main.index")
            )

    if form.is_submitted():
        # Registration failed validation: show the homepage again
        # with the Register side open and the error messages visible.
        return render_template(
            "home.html",
            login_form=LoginForm(),
            register_form=form,
            active_tab="register"
        )

    return redirect(
        url_for("main.index", tab="register")
    )

from flask_login import (
    login_user,
    logout_user
)


@main.route("/login", methods=["GET", "POST"])
def login():

    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(
            email=form.email.data
        ).first()

        if user and check_password_hash(
            user.password_hash,
            form.password.data
        ):

            login_user(user)

            flash("Login successful!")

            return redirect(
                url_for("main.dashboard")
            )

        flash("Invalid credentials")

    if form.is_submitted():
        # Login failed: show the homepage again with the Login side
        # open and the error messages visible.
        return render_template(
            "home.html",
            login_form=form,
            register_form=RegisterForm(),
            active_tab="login"
        )

    return redirect(
        url_for("main.index")
    )

@main.route("/logout")
def logout():

    logout_user()

    flash("Logged out successfully")

    return redirect(
        url_for("main.login")
    )

from flask_login import (
    login_required,
    current_user
)


@main.route("/dashboard")
@login_required
def dashboard():

    my_reservations = Reservation.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Reservation.reservation_date,
        Reservation.reservation_time
    ).all()

    upcoming = [
        r for r in my_reservations
        if r.status != "Rejected" and r.reservation_date >= datetime.now().date()
    ]

    next_reservation = upcoming[0] if upcoming else None

    return render_template(
        "dashboard.html",
        user=current_user,
        next_reservation=next_reservation,
        reservation_count=len(my_reservations)
    )




@main.route("/admin")
@login_required
@admin_required
def admin_dashboard():

    return render_template(
        "admin_dashboard.html"
    )



@main.route("/admin/tables")
@login_required
@admin_required
def view_tables():

    tables = RestaurantTable.query.order_by(
        RestaurantTable.table_number
    ).all()

    return render_template(
        "tables.html",
        tables=apply_gallery_photos(tables)
    )

@main.route("/admin/tables/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_table():

    form = TableForm()

    if form.validate_on_submit():

        existing_table = RestaurantTable.query.filter_by(
            table_number=form.table_number.data
        ).first()

        if existing_table:

            flash("Table number already exists.")

            return redirect(
                url_for("main.add_table")
            )

        image_url = None

        if form.image.data:
            image_url = upload_image(form.image.data)

        table = RestaurantTable(
            table_number=form.table_number.data,
            capacity=form.capacity.data,
            image_url=image_url
        )

        db.session.add(table)
        db.session.commit()

        flash("Table added successfully!")

        return redirect(
            url_for("main.view_tables")
        )

    return render_template(
        "add_table.html",
        form=form
    )


@main.route("/admin/tables/delete/<int:id>")
@login_required
@admin_required
def delete_table(id):

    table = RestaurantTable.query.get_or_404(id)

    db.session.delete(table)

    db.session.commit()

    flash("Table deleted successfully!")

    return redirect(
        url_for("main.view_tables")
    )


# Old direct-booking link. It used to auto-assign whichever table was
# free; now customers search and pick a specific table instead.
@main.route("/book-table")
@login_required
def book_table():

    return redirect(
        url_for("main.search_tables")
    )


@main.route("/search-tables", methods=["GET", "POST"])
@login_required
def search_tables():

    form = TableSearchForm()
    available_tables = []

    if form.validate_on_submit():

        candidate_tables = RestaurantTable.query.filter(
            RestaurantTable.capacity >= form.guests.data
        ).order_by(
            RestaurantTable.capacity
        ).all()

        for table in candidate_tables:

            already_booked = Reservation.query.filter_by(
                table_id=table.id,
                reservation_date=form.reservation_date.data,
                reservation_time=form.reservation_time.data
            ).first()

            if not already_booked:
                available_tables.append(table)

        apply_gallery_photos(available_tables)

        # A tiny reserve form per available table, pre-filled with the
        # search criteria so clicking "Reserve" carries it along.
        reserve_forms = {
            table.id: ReserveTableForm(
                formdata=None,
                reservation_date=form.reservation_date.data.isoformat(),
                reservation_time=form.reservation_time.data.strftime("%H:%M"),
                guests=str(form.guests.data)
            )
            for table in available_tables
        }

    else:
        reserve_forms = {}

    return render_template(
        "search_tables.html",
        form=form,
        tables=available_tables,
        reserve_forms=reserve_forms,
        searched=form.is_submitted()
    )


@main.route("/reserve-table/<int:table_id>", methods=["POST"])
@login_required
def reserve_table(table_id):

    form = ReserveTableForm()

    if not form.validate_on_submit():

        flash("Something went wrong. Please search again.")

        return redirect(
            url_for("main.search_tables")
        )

    table = RestaurantTable.query.get_or_404(table_id)

    reservation_date = datetime.strptime(
        form.reservation_date.data, "%Y-%m-%d"
    ).date()

    reservation_time = datetime.strptime(
        form.reservation_time.data, "%H:%M"
    ).time()

    guests = int(form.guests.data)

    if table.capacity < guests:

        flash("That table can't fit that many guests.")

        return redirect(
            url_for("main.search_tables")
        )

    already_booked = Reservation.query.filter_by(
        table_id=table.id,
        reservation_date=reservation_date,
        reservation_time=reservation_time
    ).first()

    if already_booked:

        flash("Sorry, that table was just booked. Please choose another.")

        return redirect(
            url_for("main.search_tables")
        )

    reservation = Reservation(
        reservation_date=reservation_date,
        reservation_time=reservation_time,
        guests=guests,
        user_id=current_user.id,
        table_id=table.id
    )

    db.session.add(reservation)

    db.session.commit()

    flash(
        "Reservation submitted successfully! "
        "We'll email you once it's approved."
    )

    return redirect(
        url_for("main.my_reservations")
    )


@main.route("/my-reservations")
@login_required
def my_reservations():

    reservations = Reservation.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Reservation.reservation_date,
        Reservation.reservation_time
    ).all()

    cancel_forms = {
        r.id: CancelReservationForm()
        for r in reservations
        if r.status in ("Pending", "Approved")
    }

    return render_template(
        "my_reservations.html",
        reservations=reservations,
        cancel_forms=cancel_forms
    )


@main.route("/reservation/cancel/<int:id>", methods=["POST"])
@login_required
def cancel_reservation(id):

    reservation = Reservation.query.get_or_404(id)

    if reservation.user_id != current_user.id:

        flash("You can't cancel someone else's reservation.")

        return redirect(
            url_for("main.my_reservations")
        )

    if reservation.status not in ("Pending", "Approved"):

        flash("That reservation can no longer be cancelled.")

        return redirect(
            url_for("main.my_reservations")
        )

    reservation.status = "Cancelled"

    db.session.commit()

    flash("Reservation cancelled.")

    return redirect(
        url_for("main.my_reservations")
    )


@main.route("/profile", methods=["GET", "POST"])
@login_required
def profile():

    form = ProfileForm()

    if request.method == "GET":
        form.username.data = current_user.username

    if form.validate_on_submit():

        if not check_password_hash(
            current_user.password_hash,
            form.current_password.data
        ):
            form.current_password.errors.append("Current password is incorrect.")

        elif (
            form.username.data != current_user.username
            and User.query.filter_by(username=form.username.data).first()
        ):
            form.username.errors.append("That username is already taken.")

        else:

            current_user.username = form.username.data

            if form.new_password.data:
                current_user.password_hash = generate_password_hash(
                    form.new_password.data
                )

            db.session.commit()

            flash("Profile updated successfully!")

            return redirect(
                url_for("main.profile")
            )

    return render_template(
        "profile.html",
        form=form
    )


@main.route("/admin/reservations")
@login_required
@admin_required
def admin_reservations():

    query = Reservation.query.join(User, Reservation.user_id == User.id)

    status_filter = request.args.get("status", "")
    date_filter = request.args.get("date", "")
    customer_filter = request.args.get("customer", "").strip()

    if status_filter:
        query = query.filter(Reservation.status == status_filter)

    if date_filter:
        try:
            parsed_date = datetime.strptime(date_filter, "%Y-%m-%d").date()
            query = query.filter(Reservation.reservation_date == parsed_date)
        except ValueError:
            date_filter = ""

    if customer_filter:
        query = query.filter(User.username.ilike(f"%{customer_filter}%"))

    reservations = query.order_by(
        Reservation.reservation_date,
        Reservation.reservation_time
    ).all()

    return render_template(
        "admin_reservations.html",
        reservations=reservations,
        status_filter=status_filter,
        date_filter=date_filter,
        customer_filter=customer_filter
    )

@main.route("/admin/reservation/approve/<int:id>")
@login_required
@admin_required
def approve_reservation(id):

    reservation = Reservation.query.get_or_404(id)

    reservation.status = "Approved"

    db.session.commit()

    # Notify the customer now that their booking is confirmed,
    # not the admin who just clicked "Approve".
    send_booking_confirmation(
        customer_email=reservation.customer.email,
        customer_name=reservation.customer.username,
        reservation=reservation
    )

    flash(
        "Reservation approved."
    )

    return redirect(
        url_for("main.admin_reservations")
    )


@main.route("/admin/reservation/reject/<int:id>")
@login_required
@admin_required
def reject_reservation(id):

    reservation = Reservation.query.get_or_404(id)

    reservation.status = "Rejected"

    db.session.commit()

    flash(
        "Reservation rejected."
    )

    return redirect(
        url_for("main.admin_reservations")
    )


@main.route(
    "/admin/upload-image",
    methods=["GET", "POST"]
)
@login_required
@admin_required
def upload_restaurant_image():

    form = ImageUploadForm()

    if form.validate_on_submit():

        image_url = upload_image(
            form.image.data
        )

        image = RestaurantImage(
            title=form.title.data,
            image_url=image_url
        )

        db.session.add(image)

        db.session.commit()

        flash(
            "Image uploaded successfully!"
        )

        return redirect(
            url_for("main.gallery")
        )

    return render_template(
        "upload_image.html",
        form=form
    )

@main.route("/gallery")
def gallery():

    images = RestaurantImage.query.all()

    return render_template(
        "gallery.html",
        images=images
    )