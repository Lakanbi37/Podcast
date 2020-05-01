from django.urls import path

from .views import *

urlpatterns = [
    path("", PostListAPIView.as_view()),
    path("add/", PostCreateAPIView.as_view()),
    path("categories/", CategoryListAPIView.as_view()),
    path("<slug:slug>/", PostRetrieveUpdateDestroyAPIView.as_view()),
    path("polls/vote/", PollVotesAPIView.as_view()),
    path("category/<slug:slug>/", CategoryRetrieveAPIView.as_view()),
    path("<slug:slug>/react/", ReactToPostAPIView.as_view()),
    path("<int:post_id>/polls/", PollChoiceListCreateView.as_view())
]
