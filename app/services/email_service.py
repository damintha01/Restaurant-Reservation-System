import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from flask import current_app, render_template, url_for


def send_email(to_email, to_name, subject, html_content):
    """
    Reusable utility: sends one HTML email through the Brevo
    transactional email API. Returns True on success, False on failure
    (the caller's request still succeeds even if the email doesn't).
    """

    configuration = sib_api_v3_sdk.Configuration()

    configuration.api_key["api-key"] = (
        current_app.config["BREVO_API_KEY"]
    )

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    email = sib_api_v3_sdk.SendSmtpEmail(
        to=[
            {
                "email": to_email,
                "name": to_name
            }
        ],
        sender={
            "name": current_app.config["BREVO_SENDER_NAME"],
            "email": current_app.config["BREVO_SENDER_EMAIL"]
        },
        subject=subject,
        html_content=html_content
    )

    try:
        api_instance.send_transac_email(email)
        return True

    except ApiException as e:
        print(f"Brevo email failed: {e}")
        return False


def send_welcome_email(customer_email, customer_name):
    """Sent right after a user registers."""

    html_content = render_template(
        "emails/welcome_email.html",
        customer_name=customer_name,
        login_url=url_for("main.index", _external=True)
    )

    return send_email(
        to_email=customer_email,
        to_name=customer_name,
        subject="🎉 Welcome to Our Restaurant!",
        html_content=html_content
    )


def send_booking_confirmation(customer_email, customer_name, reservation):
    """Sent when an admin approves a customer's reservation."""

    html_content = render_template(
        "emails/booking_confirmation.html",
        customer_name=customer_name,
        reservation=reservation,
        reservations_url=url_for("main.my_reservations", _external=True)
    )

    return send_email(
        to_email=customer_email,
        to_name=customer_name,
        subject="✅ Your Table Reservation is Confirmed!",
        html_content=html_content
    )


def send_booking_rejected(customer_email, customer_name, reservation):
    """Sent when an admin rejects a customer's reservation."""

    html_content = render_template(
        "emails/booking_rejected.html",
        customer_name=customer_name,
        reservation=reservation,
        search_url=url_for("main.search_tables", _external=True)
    )

    return send_email(
        to_email=customer_email,
        to_name=customer_name,
        subject="Update on Your Table Reservation",
        html_content=html_content
    )
