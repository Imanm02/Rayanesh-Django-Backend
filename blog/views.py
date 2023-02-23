from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from .models import BlogPost
from .serializers import BlogPostSerializer
from filters import BlogFilter

from django_filters import rest_framework as filters


class BlogPostList(ListAPIView):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = BlogFilter


class BlogPostDetail(APIView):

    def get(self, request, pk):
        blogpost = BlogPost.objects.get(pk=pk)
        blogpost.views_count += 1
        blogpost.save()
        serializer = BlogPostSerializer(blogpost)
        return Response(serializer.data)
