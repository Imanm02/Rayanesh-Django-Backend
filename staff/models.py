from django.db import models
from model_utils.models import TimeStampedModel


class Staff(TimeStampedModel):
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    position = models.CharField(max_length=64)
    image = models.ImageField(upload_to='staff_images')
    present_in_landing_page = models.BooleanField(default=False)
