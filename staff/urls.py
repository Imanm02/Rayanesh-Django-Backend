from django.urls import path
from .views import StaffList

urlpatterns = [
    path('', StaffList.as_view(), name='staffs'),
]
