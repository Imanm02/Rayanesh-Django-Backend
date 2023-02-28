from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework import status

from .models import BlogPost
from .serializers import BlogPostSerializer
from filters import BlogFilter

from django_filters import rest_framework as filters
from django.shortcuts import render


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


class BlogPostCreate(CreateAPIView):
    serializer_class = BlogPostSerializer

    def post(self, request, *args, **kwargs):
        serializer = BlogPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

