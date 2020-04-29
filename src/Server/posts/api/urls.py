from django.urls import path

from .views import *


urlpatterns = [
    path("", PostListAPIView.as_view()),
    path("<int:pk>/", PostRetrieveUpdateDestroyAPIView.as_view()),
]