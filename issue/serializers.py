from rest_framework import serializers

from .models import Issue


class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = ['id', 'raw_file', 'cover_image', 'name', 'authors', 'subject',
                  'pages_number', 'publishing_date', 'is_issue', 'views_count']
