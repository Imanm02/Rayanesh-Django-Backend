from rest_framework.generics import ListAPIView

from .models import Staff
from .serializers import StaffSerializer

from django_filters import rest_framework as filters


class StaffList(ListAPIView):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    filter_backends = (filters.DjangoFilterBackend, )