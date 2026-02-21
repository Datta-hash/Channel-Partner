from rest_framework import serializers
from Meta.models import State


class StateSerializer(serializers.ModelSerializer):

    class Meta:
        model = State
        fields = "__all__"

    def validate_display_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError(
                "Display name cannot be empty."
            )
        return value

    def validate(self, data):
        name = data.get("display_name")
        country = data.get("country") or getattr(
            self.instance, "country", None
        )

        queryset = State.objects.filter(
            display_name__iexact=name,
            country=country
        )

        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)

        if queryset.exists():
            raise serializers.ValidationError(
                {"display_name": "State already exists in this country."}
            )

        return data
