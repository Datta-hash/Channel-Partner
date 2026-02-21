from django.db import models
from django.contrib.auth.models import User
from Meta.models.meta_country import Country
from Meta.models.meta_state import State
from Meta.models.meta_city import City
from Meta.models.meta_nature_of_business import NatureOfBusiness
from services.base_model import BaseModel


class UserProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    state = models.ForeignKey(State, on_delete=models.PROTECT)
    city = models.ForeignKey(City, on_delete=models.PROTECT)
    nature_of_business = models.ForeignKey(NatureOfBusiness, on_delete=models.PROTECT)
    referral_code = models.CharField(max_length=10, unique=True, blank=True, null=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.username} ({self.user.get_full_name()})"