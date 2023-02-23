from django.db import models
from model_utils.models import TimeStampedModel


class Podcast(TimeStampedModel):
    raw_file = models.FileField(upload_to='files/podcasts')
    cover_image = models.ImageField(upload_to='podcast_cover_images')
    name = models.CharField(max_length=128)
    contributors = models.TextField(help_text='All contributors comma or new line seperated here')
    subject = models.CharField(max_length=32)
    length = models.DurationField()
    publishing_date = models.DateField()
    views_count = models.PositiveIntegerField(default=0)
