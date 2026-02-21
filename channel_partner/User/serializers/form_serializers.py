from rest_framework import serializers
from User.models import RegistrationRequest
import re


class RegistrationRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = RegistrationRequest
        fields = (
            "id",
            "name",
            "email",
            "country_code",
            "phone",
            "country",
            "state",
            "city",
            "nature_of_business",
            "approval_status",
        )
        read_only_fields = ("approval_status",)

    # ---------- STRING FIELDS ----------

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError(
                "Name cannot be empty."
            )
        return value
    
    def validate_country_code(self, value):
        value = value.strip()
        if not re.match(r'^\+[1-9]\d{1,3}$', value):
            raise serializers.ValidationError(
                "Enter a valid country code e.g. +91, +1, +44."
            )
        return value

    def validate_email(self, value):
        value = value.lower().strip()

        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
            raise serializers.ValidationError(
                "Enter a valid email address."
                    )

        return value
    




    def validate_phone(self, value):
        value = value.strip()   

        if not re.match(r'^[6-9]\d{9}$', value):
            raise serializers.ValidationError(
                "Enter a valid 10-digit Indian phone number starting with 6, 7, 8, or 9."
                )

        return value

    # ---------- FOREIGN KEY FIELDS ----------

    def validate_country(self, value):
        if not value:
            raise serializers.ValidationError(
                "Country is required."
            )
        return value

    def validate_state(self, value):
        if not value:
            raise serializers.ValidationError(
                "State is required."
            )
        return value

    def validate_city(self, value):
        if not value:
            raise serializers.ValidationError(
                "City is required."
            )
        return value

    def validate_nature_of_business(self, value):
        if not value:
            raise serializers.ValidationError(
                "Nature of business is required."
            )
        return value

    # ---------- GLOBAL VALIDATION ----------

    def validate(self, data):
        email = data.get("email")
        phone = data.get("phone")

        queryset = RegistrationRequest.objects.all()

        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)

        if queryset.filter(email=email).exists():
            raise serializers.ValidationError({
                "email": "This email is already registered."
            })

        if queryset.filter(phone=phone).exists():
            raise serializers.ValidationError({
                "phone": "This phone number is already registered."
            })

        return data