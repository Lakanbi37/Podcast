from django.urls import path

from .views import *

urlpatterns = [
    path("", PostListAPIView.as_view()),
    path("add/", PostCreateAPIView.as_view()),
    path("<slug:slug>/", PostRetrieveUpdateDestroyAPIView.as_view()),
    path("<slug:slug>/like/", ToggleLikePost.as_view())
]
