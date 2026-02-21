from services.base_model import BaseModel
from django.db import models

class NatureOfBusiness(BaseModel):
   
    nature_of_business=models.CharField(max_length=100)
   
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nature_of_business