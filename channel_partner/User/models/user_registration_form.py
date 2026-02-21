from services.base_model import BaseModel
from Meta.models.meta_country import Country
from Meta.models.meta_state import State
from Meta.models.meta_city import City
from Meta.models.meta_nature_of_business import NatureOfBusiness
from django.db import models


class RegistrationRequest(BaseModel):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)

    country_code = models.CharField(max_length=5, default="+91")
    phone = models.CharField(max_length=15)

    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    state = models.ForeignKey(State, on_delete=models.PROTECT)
    city = models.ForeignKey(City, on_delete=models.PROTECT)

    nature_of_business = models.ForeignKey(
        NatureOfBusiness,
        on_delete=models.PROTECT
    )

    approval_status = models.CharField(
        max_length=20,
        choices=(
            ('PENDING', 'Pending'),
            ('APPROVED', 'Approved'),
            ('REJECTED', 'Rejected')
        ),
        default='PENDING'
    )