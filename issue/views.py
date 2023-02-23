from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView

from .models import Issue
from .serializers import IssueSerializer
from filters import IssueFilter

from django_filters import rest_framework as filters


class IssueList(ListAPIView):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = IssueFilter


class IssueDetail(APIView):

    def get(self, request, pk):
        issue = Issue.objects.get(pk=pk)
        issue.views_count += 1
        issue.save()
        serializer = IssueSerializer(issue)
        return Response(serializer.data)
