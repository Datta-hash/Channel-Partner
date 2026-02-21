from services.base_model import BaseModel
from django.db import models
from .meta_state import State  

class City(BaseModel):
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    city_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.city_name