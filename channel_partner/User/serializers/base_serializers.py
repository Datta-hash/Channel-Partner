from services.base_model import BaseModel
from rest_framework import serializers

class BaseSerializer(serializers.ModelSerializer):

    class Meta:
        abstract = True
        read_only_fields = (
            "created_at",
            "updated_at",
        )