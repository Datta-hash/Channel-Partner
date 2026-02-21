import random
from twilio.rest import Client
from django.conf import settings


def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp(phone, otp):
    client = Client(
        settings.TWILIO_ACCOUNT_SID,
        settings.TWILIO_AUTH_TOKEN
    )

    client.messages.create(
        body=f"Your OTP is {otp}",
        from_=settings.TWILIO_PHONE_NUMBER,
        to=phone
    )


