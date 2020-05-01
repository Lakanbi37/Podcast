from django.urls import path
from .views import MembershipListCreateAPIView, MembershipRetrieveAPIView

app_name = "membership-api"

urlpatterns = [
    path("", MembershipListCreateAPIView.as_view()),
    path("<slug:slug>/", MembershipRetrieveAPIView.as_view(), name="membership")
]