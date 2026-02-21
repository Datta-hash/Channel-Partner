from django.db import models
from services.base_model import BaseModel


class Country(BaseModel):
    country_name=models.CharField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    country_code = models.CharField(max_length=5)


    def __str__(self):
        return self.country_name

class Meta:
    constraints = [
        models.UniqueConstraint(
            fields=['country_code', 'phone'],
            name='unique_phone_per_country'
        )
    ]
