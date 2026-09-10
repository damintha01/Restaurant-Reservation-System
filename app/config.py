import os
from dotenv import load_dotenv

load_dotenv()


class Config:

    SECRET_KEY = os.getenv("SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = "sqlite:///restaurant.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    SQLALCHEMY_DATABASE_URI = os.getenv(
    "DATABASE_URL",
    "sqlite:///restaurant.db"
)

    CLOUDINARY_CLOUD_NAME = os.getenv(
        "CLOUDINARY_CLOUD_NAME"
    )

    CLOUDINARY_API_KEY = os.getenv(
        "CLOUDINARY_API_KEY"
    )

    CLOUDINARY_API_SECRET = os.getenv(
        "CLOUDINARY_API_SECRET"
    )

    BREVO_API_KEY = os.getenv(
        "BREVO_API_KEY"
    )

    BREVO_SENDER_EMAIL = os.getenv(
        "BREVO_SENDER_EMAIL"
    )

    BREVO_SENDER_NAME = os.getenv(
        "BREVO_SENDER_NAME",
        "Restaurant"
    )