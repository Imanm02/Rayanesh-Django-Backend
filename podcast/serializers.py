from rest_framework import serializers

from .models import Podcast


class PodcastSerializer(serializers.ModelSerializer):
    class Meta:
        model = Podcast
        fields = ['id', 'raw_file', 'cover_image', 'name', 'contributors', 'subject',
                  'length', 'publishing_date', 'views_count']
