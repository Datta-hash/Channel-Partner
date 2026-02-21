from services.base_model import BaseModel
from django.db import models
from .meta_country import Country 

class State(BaseModel):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    state_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.state_name
    
