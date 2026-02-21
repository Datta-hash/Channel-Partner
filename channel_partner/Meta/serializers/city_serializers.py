from Meta.models import City
from rest_framework import serializers


class CitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = "__all__"

    def validate_display_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError(
                "Display name cannot be empty."
            )
        return value

    def validate(self, data):
        state = data.get("state") or getattr(
            self.instance, "state", None
        )

        name = data.get("display_name") or getattr(
            self.instance, "display_name", None
        )

        queryset = City.objects.filter(
            state=state,
            display_name__iexact=name
        )

        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)

        if queryset.exists():
            raise serializers.ValidationError(
                {"display_name": "City already exists in this state."}
            )

        return data
