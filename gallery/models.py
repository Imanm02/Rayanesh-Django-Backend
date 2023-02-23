from django.db import models
from model_utils.models import TimeStampedModel


class GalleryPhoto(TimeStampedModel):
    image = models.ImageField(upload_to='gallery_photos')
    caption = models.CharField(max_length=256)
    attenders = models.TextField(help_text='All attenders comma or new line seperated here',
                                 null=True, blank=True)
    photographer = models.CharField(max_length=64)
    shooting_date = models.DateField()
    publishing_date = models.DateField()
    views_count = models.PositiveIntegerField(default=0)
