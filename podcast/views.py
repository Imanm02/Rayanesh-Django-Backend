from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView

from .models import Podcast
from .serializers import PodcastSerializer
from filters import PodcastFilter

from django_filters import rest_framework as filters


class PodcastList(ListAPIView):
    queryset = Podcast.objects.all()
    serializer_class = PodcastSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = PodcastFilter


class PodcastDetail(APIView):

    def get(self, request, pk):
        podcast = Podcast.objects.get(pk=pk)
        podcast.views_count += 1
        podcast.save()
        serializer = PodcastSerializer(podcast)
        return Response(serializer.data)
