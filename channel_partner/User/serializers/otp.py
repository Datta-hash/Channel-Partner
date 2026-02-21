from rest_framework import serializers
from django.contrib.auth import get_user_model
from User.models import AdminProfile

User = get_user_model()


class RequestOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)

    def validate_phone_number(self, value):
        """Allow both admins (AdminProfile) and normal users (User model) to request OTP."""
        is_admin = AdminProfile.objects.filter(phone_number=value).exists()
        # Adjust "phone_number" below if your User model stores it differently
        is_user = User.objects.filter(phone_number=value).exists()

        if not is_admin and not is_user:
            raise serializers.ValidationError(
                "No account found with this phone number."
            )
        return value


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    otp_code = serializers.CharField(min_length=6, max_length=6)

    def validate_otp_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("OTP must contain digits only.")
        return value