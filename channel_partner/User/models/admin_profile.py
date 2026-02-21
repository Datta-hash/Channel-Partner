from django.conf import settings
from django.db import models
from services.base_model import BaseModel


class AdminProfile(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="admin_profile"
    )

    phone_number = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        unique=True,
    )

    email = models.EmailField(
        null=True,
        blank=True,
        unique=True,)
    

    def __str__(self):
        return self.user.username