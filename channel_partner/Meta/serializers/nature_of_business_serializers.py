from rest_framework import serializers
from Meta.models import NatureOfBusiness


class NatureOfBusinessSerializer(serializers.ModelSerializer):

    class Meta:
        model = NatureOfBusiness
        fields = "__all__"

    def validate_display_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Display name cannot be empty."
            )

        return value
