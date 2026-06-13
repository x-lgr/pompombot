import random
import string
from datetime import datetime


def generate_discount_code():
    """Generate a random discount code"""
    return f"DISC{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"


def calculate_discounted_amount(original_amount, discount_percent):
    """Calculate discounted amount"""
    return int(original_amount - (original_amount * discount_percent / 100))


def get_random_discount():
    """Get random discount between 1% and 25%"""
    return random.randint(1, 25)


def generate_payment_url(upi_name, bank_name, amount):
    """Generate payment URL using template"""
    from config import Config
    return Config.PAYMENT_URL_TEMPLATE.format(
        upiname=upi_name,
        bankname=bank_name,
        amount=amount
    )


def format_start_message(message, user):
    """Format start message with user placeholders"""
    first_name = user.first_name or "User"
    last_name = user.last_name or ""
    username = user.username or ""
    user_id = user.id

    return message.format(
        first_name=first_name,
        last_name=last_name,
        username=username,
        user_id=user_id
    )


def validate_url(url):
    """Validate URL format"""
    return url.startswith(("http://", "https://", "t.me/"))


def validate_image_file(file):
    """Validate image file type"""
    allowed_types = ["image/jpeg", "image/jpg", "image/png"]
    return file.mime_type in allowed_types if hasattr(file, "mime_type") else False
