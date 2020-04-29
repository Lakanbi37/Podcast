from django.urls import path

from .views import *

urlpatterns = [
    path("add/", CommentCreateAPIView.as_view()),
    path("<int:pk>/", CommentDetailView.as_view()),
    path("<int:post_id>/comments/", PostCommentListAPIView.as_view()),
]
