from django.urls import path
from .views import *

urlpatterns = [
    path("discussions/", DiscussionListView.as_view()),
    path("discussion/start/", DiscussionCreateAPIView.as_view()),
    path("discussion/<slug:slug>/", DiscussionRetrieveUpdateDeleteAPIView.as_view()),
]