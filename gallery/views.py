from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import GalleryPhoto
from .serializers import GalleryPhotoSerializer

from django_filters import rest_framework as filters


class GalleryList(ListAPIView):
    queryset = GalleryPhoto.objects.all()
    serializer_class = GalleryPhotoSerializer
    filter_backends = (filters.DjangoFilterBackend,)


class GalleryDetail(APIView):

    def get(self, request, pk):
        gallery_photo = GalleryPhoto.objects.get(pk=pk)
        gallery_photo.views_count += 1
        gallery_photo.save()
        serializer = GalleryPhotoSerializer(gallery_photo)
        return Response(serializer.data)
