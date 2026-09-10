import cloudinary  # type: ignore[reportMissingImports]
import cloudinary.uploader  # type: ignore[reportMissingImports]

def upload_image(file):

    result = cloudinary.uploader.upload(file)

    return result["secure_url"]