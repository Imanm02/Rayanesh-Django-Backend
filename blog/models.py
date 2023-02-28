from django.db import models
from model_utils.models import TimeStampedModel
from django.contrib.postgres.fields import JSONField


class BlogPost(TimeStampedModel):
    # post_text = models.TextField()
    # post_image = models.ImageField(upload_to='blog_post_images')
    post_content = JSONField()
    contributors = models.TextField(help_text='All contributors comma or new line seperated here')
    subject = models.CharField(max_length=32, unique=True)
    reading_time = models.IntegerField()
    posting_date = models.DateTimeField()
    views_count = models.PositiveIntegerField(default=0)
    preview = models.CharField(max_length=128, null=True, blank=True)