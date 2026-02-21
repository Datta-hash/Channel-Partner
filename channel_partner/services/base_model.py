from django.db import models

class BaseModel(models.Model):
    created_by = models.IntegerField(null=False, default=-1)
    created_at = models.DateTimeField(auto_now_add=True)

    updated_by = models.IntegerField(null=False, default=-1)
    updated_at = models.DateTimeField(auto_now=True)

    status = models.BooleanField(default=True)
    
    
    class Meta:
        abstract = True