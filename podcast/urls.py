from django.urls import path
from .views import PodcastList, PodcastDetail

urlpatterns = [
    path('', PodcastList.as_view(), name='podcasts'),
    path('<int:pk>/', PodcastDetail.as_view(), name='podcast'),
]
