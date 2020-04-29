from django.urls import path

from .views import *

urlpatterns = [
    path("", ProfileListAPIView.as_view()),
    path("add/", ProfileCreateAPIView.as_view()),
    path("add-links/", SocialLinkCreateAPIView.as_view()),
    path("settings/", SettingsRetrieveUpdateView.as_view()),
    path("verify/", ToggleProfileVerification.as_view()),
    path("<slug:username>/", ProfileRetrieveUpdateDeleteAPIView.as_view()),
    path("<slug:username>/links/", SocialLinkRetrieveUpdateDeleteAPIView.as_view()),
]
