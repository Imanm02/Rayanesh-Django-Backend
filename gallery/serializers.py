from rest_framework import serializers

from .models import GalleryPhoto


class GalleryPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryPhoto
        fields = ['id', 'image', 'caption', 'attenders', 'shooting_date',
                  'views_count', 'photographer', 'publishing_date']
