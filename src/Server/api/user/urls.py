from django.urls import path

from .views import *

urlpatterns = [
    path("", UserAPIView.as_view()),
    path("discussions/", UserDiscussionAPIView.as_view()),
    path("<slug:username>/", UserDetailsAPIView.as_view()),
]