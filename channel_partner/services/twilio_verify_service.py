from twilio.rest import Client
from django.conf import settings

client = Client(
    settings.TWILIO_ACCOUNT_SID,
    settings.TWILIO_AUTH_TOKEN
)

def send_otp(phone):
    verification = client.verify \
        .services(settings.TWILIO_VERIFY_SERVICE_SID) \
        .verifications \
        .create(to=phone, channel="sms")

    return verification.sid


def verify_otp(phone, otp):
    check = client.verify \
        .services(settings.TWILIO_VERIFY_SERVICE_SID) \
        .verification_checks \
        .create(to=phone, code=otp)

    return check.status
