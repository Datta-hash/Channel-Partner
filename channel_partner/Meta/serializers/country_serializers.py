from rest_framework import serializers
from Meta.models import Country


class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")

    def validate_display_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Country name is required.")
        return value

    def validate_country_code(self, value):
        return value.upper()

    def validate_dialing_code(self, value):
        if not value.replace("+", "").isdigit():
            raise serializers.ValidationError(
                "Dialing code must contain only numbers and optional '+'."
            )
        return value

    def validate(self, data):
        name = data.get("display_name") or getattr(
            self.instance, "display_name", None
        )

        if Country.objects.filter(
            display_name__iexact=name
        ).exclude(
            id=self.instance.id if self.instance else None
        ).exists():
            raise serializers.ValidationError(
                {"display_name": "Country with this name already exists."}
            )

        return data
