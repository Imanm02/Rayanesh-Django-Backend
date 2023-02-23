from django.urls import path
from .views import IssueDetail, IssueList

urlpatterns = [
    path('', IssueList.as_view(), name='issues'),
    path('<int:pk>/', IssueDetail.as_view(), name='issue'),
]
